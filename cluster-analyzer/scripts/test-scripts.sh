#!/bin/bash
# Tests panorama.sh and envdiff.py against a fake kubectl, no cluster needed.
# Usage: scripts/test-scripts.sh

DIR="$(cd "$(dirname "$0")" && pwd)"
FAKE=$(mktemp -d)
trap 'rm -rf "$FAKE"' EXIT

# fake kubectl: answers by context (hml|prd) and by the requested resource.
cat > "$FAKE/kubectl" <<'EOF'
#!/bin/bash
args="$*"
ctx=$(echo "$args" | sed -E 's/.*--context ([^ ]+).*/\1/')
case "$args" in
  *"get virtualservice"*) echo 'error: the server doesn'"'"'t have a resource type "virtualservice"' >&2; exit 1 ;;
  *"top pod"*) echo 'error: Metrics API not available' >&2; exit 1 ;;
  *"get secret"*) echo "fake kubectl: script must not read secret" >&2; exit 99 ;;
  *"get deployment api"*)
    if [ "$ctx" = hml ]; then img=app:1.2; url=jdbc:hml; extra='{"name":"SO_HML","value":"x"},'
    else img=app:1.2; url=jdbc:prd; extra=''; fi
    cat <<JSON
{"spec":{"template":{"spec":{"containers":[{"name":"api","image":"$img",
 "envFrom":[{"configMapRef":{"name":"api-cm"}},{"secretRef":{"name":"api-sec"}}],
 "env":[$extra{"name":"DB_URL","value":"$url"},{"name":"DB_PASSWORD","value":"s3nha-$ctx"},
        {"name":"TOKEN","valueFrom":{"secretKeyRef":{"name":"api-sec","key":"token"}}},
        {"name":"MODE","valueFrom":{"configMapKeyRef":{"name":"blocked","key":"mode"}}}]}]}}}}
JSON
    ;;
  *"get configmap api-cm"*) echo "{\"data\":{\"LOG_LEVEL\":\"$([ "$ctx" = hml ] && echo DEBUG || echo INFO)\",\"TZ\":\"UTC\"}}" ;;
  *"get configmap blocked"*) echo 'Error from server (Forbidden): configmaps "blocked" is forbidden' >&2; exit 1 ;;
  *) echo "ok $args" ;;
esac
EOF
chmod +x "$FAKE/kubectl"
export PATH="$FAKE:$PATH"

falhas=0
confere() {  # confere <description> <output> <grep-pattern> [not]
  if echo "$2" | grep -qF -- "$3"; then [ "$4" = not ] && { echo "FALHA: $1"; falhas=$((falhas+1)); return; }
  else [ "$4" != not ] && { echo "FALHA: $1"; falhas=$((falhas+1)); return; }; fi
  echo "ok: $1"
}

p=$("$DIR/panorama.sh" kc hml ns); rc=$?
confere "panorama exits 0 even with a failing section" "$rc" "0"
confere "panorama reports the section that failed" "$p" 'FAILED: error: Metrics API not available'
confere "panorama carries on after the failure" "$p" '== Recent events'
confere "panorama passes explicit kubeconfig and context" "$p" 'ok --kubeconfig kc --context hml -n ns get pods -o wide'

e=$(python3 "$DIR/envdiff.py" api --a kc hml ns --b kc prd ns 2>&1); rc=$?
confere "envdiff exits 0" "$rc" "0"
confere "envdiff shows variable only in A" "$e" 'SO_HML=x'
confere "envdiff shows a different value" "$e" 'A=jdbc:hml'
confere "envdiff resolves configmap via envFrom" "$e" 'A=DEBUG'
confere "envdiff masks a differing credential" "$e" 'DB_PASSWORD: values differ (masked)'
confere "envdiff never prints the password" "$e" 's3nha' not
confere "envdiff marks unreadable configmap and carries on" "$e" 'Same:'

echo
if [ "$falhas" -eq 0 ]; then echo "all cases ok"; else echo "$falhas failure(s)"; exit 1; fi
