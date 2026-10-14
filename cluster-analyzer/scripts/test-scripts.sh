#!/bin/bash
# Testa panorama.sh e envdiff.py contra um kubectl falso, sem cluster.
# Uso: scripts/test-scripts.sh

DIR="$(cd "$(dirname "$0")" && pwd)"
FAKE=$(mktemp -d)
trap 'rm -rf "$FAKE"' EXIT

# kubectl falso: responde pelo contexto (hml|prd) e pelo recurso pedido.
cat > "$FAKE/kubectl" <<'EOF'
#!/bin/bash
args="$*"
ctx=$(echo "$args" | sed -E 's/.*--context ([^ ]+).*/\1/')
case "$args" in
  *"get virtualservice"*) echo 'error: the server doesn'"'"'t have a resource type "virtualservice"' >&2; exit 1 ;;
  *"top pod"*) echo 'error: Metrics API not available' >&2; exit 1 ;;
  *"get secret"*) echo "kubectl falso: script não pode ler secret" >&2; exit 99 ;;
  *"get deployment api"*)
    if [ "$ctx" = hml ]; then img=app:1.2; url=jdbc:hml; extra='{"name":"SO_HML","value":"x"},'
    else img=app:1.2; url=jdbc:prd; extra=''; fi
    cat <<JSON
{"spec":{"template":{"spec":{"containers":[{"name":"api","image":"$img",
 "envFrom":[{"configMapRef":{"name":"api-cm"}},{"secretRef":{"name":"api-sec"}}],
 "env":[$extra{"name":"DB_URL","value":"$url"},{"name":"DB_PASSWORD","value":"s3nha-$ctx"},
        {"name":"TOKEN","valueFrom":{"secretKeyRef":{"name":"api-sec","key":"token"}}},
        {"name":"MODO","valueFrom":{"configMapKeyRef":{"name":"bloqueado","key":"modo"}}}]}]}}}}
JSON
    ;;
  *"get configmap api-cm"*) echo "{\"data\":{\"LOG_LEVEL\":\"$([ "$ctx" = hml ] && echo DEBUG || echo INFO)\",\"TZ\":\"UTC\"}}" ;;
  *"get configmap bloqueado"*) echo 'Error from server (Forbidden): configmaps "bloqueado" is forbidden' >&2; exit 1 ;;
  *) echo "ok $args" ;;
esac
EOF
chmod +x "$FAKE/kubectl"
export PATH="$FAKE:$PATH"

falhas=0
confere() {  # confere <descrição> <saída> <padrão-grep> [nao]
  if echo "$2" | grep -qF -- "$3"; then [ "$4" = nao ] && { echo "FALHA: $1"; falhas=$((falhas+1)); return; }
  else [ "$4" != nao ] && { echo "FALHA: $1"; falhas=$((falhas+1)); return; }; fi
  echo "ok: $1"
}

p=$("$DIR/panorama.sh" kc hml ns); rc=$?
confere "panorama sai com 0 mesmo com seção falhando" "$rc" "0"
confere "panorama relata seção que falhou" "$p" 'FALHOU: error: Metrics API not available'
confere "panorama segue depois da falha" "$p" '== Eventos recentes'
confere "panorama passa kubeconfig e contexto explícitos" "$p" 'ok --kubeconfig kc --context hml -n ns get pods -o wide'

e=$(python3 "$DIR/envdiff.py" api --a kc hml ns --b kc prd ns 2>&1); rc=$?
confere "envdiff sai com 0" "$rc" "0"
confere "envdiff mostra variável só em A" "$e" 'SO_HML=x'
confere "envdiff mostra valor diferente" "$e" 'A=jdbc:hml'
confere "envdiff resolve configmap via envFrom" "$e" 'A=DEBUG'
confere "envdiff mascara credencial diferente" "$e" 'DB_PASSWORD: valores diferentes (mascarado)'
confere "envdiff nunca imprime a senha" "$e" 's3nha' nao
confere "envdiff marca configmap ilegível e segue" "$e" 'Iguais:'

echo
if [ "$falhas" -eq 0 ]; then echo "todos os casos ok"; else echo "$falhas falha(s)"; exit 1; fi
