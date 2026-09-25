#!/bin/bash
# Hook PreToolUse (matcher: Bash) do guardrails. Bloqueia, antes de executar,
# os comandos da regra 5 do SKILL.md que dá para reconhecer pelo texto.
# Adaptado de mattpocock/skills@git-guardrails-claude-code (MIT).
#
# Contrato do Claude Code: exit 2 bloqueia a chamada e entrega o stderr ao
# agente; qualquer outro exit deixa passar.
#
# Teste: scripts/test-block-dangerous.sh

INPUT=$(cat)

# Sem jq, casa contra o JSON cru: bloqueia a mais (o campo description também
# entra na busca), nunca a menos. Liberar tudo em silêncio seria pior.
if command -v jq >/dev/null 2>&1; then
  COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
else
  COMMAND=$INPUT
fi
[ -z "$COMMAND" ] && exit 0

# S: qualquer coisa dentro do mesmo comando (sem atravessar | ; &) até um
# espaço — é o que deixa passar opção antes do subcomando (kubectl -n x delete).
# E: fim do token, para "push" não bater em "feat/push-x".
S='[^|;&]*[[:space:]]'
E='([[:space:]"]|$)'

PADROES=(
  # git: reescreve histórico ou descarta trabalho
  "\bgit${S}push${E}"
  "\bgit${S}reset${S}--hard${E}"
  "\bgit${S}clean${S}(-[a-zA-Z]*f[a-zA-Z]*|--force)${E}"
  "\bgit${S}branch${S}(-[a-zA-Z]*D[a-zA-Z]*|--delete${S}--force|--force${S}--delete)${E}"
  "\bgit${S}(checkout|restore)${S}(\.|--${E})"
  "\bgit${S}stash${S}(drop|clear)${E}"
  # infraestrutura: destrói recurso fora desta sessão
  "\bkubectl${S}delete${E}"
  "\bhelm${S}(uninstall|delete)${E}"
  "\bterraform${S}(destroy|-destroy)${E}"
  "\bterraform${S}state${S}rm${E}"
  "\bdocker${S}system${S}prune${E}"
  "\bdocker${S}volume${S}(rm|prune)${E}"
  "\bdocker${S}down${S}(-[a-zA-Z]*v[a-zA-Z]*|--volumes)${E}"
  "\bdocker${S}rm${S}-[a-zA-Z]*v"
)

for padrao in "${PADROES[@]}"; do
  if printf '%s' "$COMMAND" | grep -qE -- "$padrao"; then
    cat >&2 <<MSG
BLOQUEADO pelo guardrails: '$COMMAND' bate no padrão '$padrao'.
Você não tem autoridade para rodar isso. Se a ação for desejada, mostre o comando
e a consequência ao usuário e peça que ele mesmo rode (prefixo ! no prompt).
MSG
    exit 2
  fi
done

exit 0
