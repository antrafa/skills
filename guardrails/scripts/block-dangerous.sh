#!/bin/bash
# guardrails PreToolUse hook (matcher: Bash). Blocks, before execution, the
# commands from rule 5 of SKILL.md that can be recognized from their text.
# Adapted from mattpocock/skills@git-guardrails-claude-code (MIT).
#
# Claude Code contract: exit 2 blocks the call and hands stderr to the agent;
# any other exit lets it through.
#
# Test: scripts/test-block-dangerous.sh

INPUT=$(cat)

# Without jq, match against the raw JSON: over-block (the description field
# also enters the search), never under-block. Silently allowing everything
# would be worse.
if command -v jq >/dev/null 2>&1; then
  COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
else
  COMMAND=$INPUT
fi
[ -z "$COMMAND" ] && exit 0

# S: anything within the same command (without crossing | ; &) up to a
# space — this is what lets an option through before the subcommand
# (kubectl -n x delete).
# E: end of token, so "push" does not match "feat/push-x".
S='[^|;&]*[[:space:]]'
E='([[:space:]"]|$)'

PADROES=(
  # git: rewrites history or discards work
  "\bgit${S}push${E}"
  "\bgit${S}reset${S}--hard${E}"
  "\bgit${S}clean${S}(-[a-zA-Z]*f[a-zA-Z]*|--force)${E}"
  "\bgit${S}branch${S}(-[a-zA-Z]*D[a-zA-Z]*|--delete${S}--force|--force${S}--delete)${E}"
  "\bgit${S}(checkout|restore)${S}(\.|--${E})"
  "\bgit${S}stash${S}(drop|clear)${E}"
  # infrastructure: destroys a resource outside this session
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
BLOCKED by guardrails: '$COMMAND' matches the pattern '$padrao'.
You do not have the authority to run this. If the action is wanted, show the
command and its consequence to the user and ask them to run it themselves
(prefix ! in the prompt).
MSG
    exit 2
  fi
done

exit 0
