#!/bin/bash
# Casos do hook block-dangerous.sh: o que tem que bloquear e o que tem que passar.
# Roda com e sem jq no PATH. Uso: scripts/test-block-dangerous.sh

HOOK="$(dirname "$0")/block-dangerous.sh"

BLOQUEIA=(
  'git push origin main'
  'git push --force'
  'git  push'
  'git -C /tmp/x push origin main'
  'cd repo && git push'
  'git reset --hard HEAD~1'
  'git clean -fd'
  'git clean -d -f'
  'git clean --force'
  'git branch -D feat'
  'git branch --delete --force feat'
  'git checkout .'
  'git checkout -- src/a.txt'
  'git restore .'
  'git stash drop'
  'git stash clear'
  'kubectl delete pod x'
  'kubectl -n prod delete pod x'
  'kubectl --context=prd delete ns app'
  'helm uninstall app'
  'helm -n prod uninstall app'
  'terraform destroy'
  'terraform -chdir=infra destroy'
  'terraform apply -destroy'
  'terraform state rm aws_s3_bucket.x'
  'docker system prune -a'
  'docker volume rm dados'
  'docker compose down -v'
  'docker-compose down --volumes'
  'docker rm -fv mongo'
)

PASSA=(
  'git status'
  'git pull'
  'git log --oneline'
  'git checkout -b feat/push-notificacao'
  'git reset --soft HEAD~1'
  'git clean -n'
  'git branch -d feat'
  'git stash list'
  'kubectl get pods -n prod'
  'kubectl -n prod describe pod x'
  'helm list -A'
  'terraform plan'
  'docker compose down'
  'docker rm mongo'
  'rm -rf /tmp/build'
  'ls | grep push'
)

# Monta o JSON sem jq, para o teste também valer onde ele não existe.
json() { printf '{"tool_input":{"command":"%s"}}' "$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')"; }

SEM_JQ=$(mktemp -d)
trap 'rm -rf "$SEM_JQ"' EXIT
for bin in cat grep printf; do ln -s "$(command -v "$bin")" "$SEM_JQ/$bin"; done

falhas=0
roda() { # <esperado> <PATH> <comando>
  json "$3" | env PATH="$2" /bin/bash "$HOOK" >/dev/null 2>&1
  local obtido=$?
  [ "$obtido" = "$1" ] && return
  echo "FALHOU (PATH=$2): esperado exit=$1, obtido exit=$obtido :: $3"
  falhas=$((falhas + 1))
}

for path in "$PATH" "$SEM_JQ"; do
  for cmd in "${BLOQUEIA[@]}"; do roda 2 "$path" "$cmd"; done
  for cmd in "${PASSA[@]}"; do roda 0 "$path" "$cmd"; done
done

total=$(( (${#BLOQUEIA[@]} + ${#PASSA[@]}) * 2 ))
echo "$((total - falhas))/$total casos ok"
[ "$falhas" -eq 0 ]
