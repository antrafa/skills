#!/usr/bin/env bash
# Wire mobilekit into the AI agents installed on this machine.
# Symlinks only — nothing is copied, no config file is modified.
#
# `npx skills add <owner>/<repo>` is the supported alternative and needs none of this.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK=0
EXTRA_DIR=""
PREFIX="mobilekit-"

# The skill's name comes from SKILL.md's frontmatter, not from the directory it was
# cloned into — cloning as `skill-mobilekit` must still produce `/mobilekit:*`.
NAME="$(sed -n 's/^name:[[:space:]]*//p' "$REPO/SKILL.md" | head -1)"
[ -n "$NAME" ] || { echo "SKILL.md has no name: field" >&2; exit 1; }

usage() {
  cat <<EOF
usage: install.sh [--check] [--commands-dir DIR] [--prefix P]

  --check              verify existing links, change nothing
  --commands-dir DIR   also link each command into DIR (for an agent not known here)
  --prefix P           filename prefix used in flat command dirs   [default: mobilekit-]
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK=1 ;;
    --commands-dir) EXTRA_DIR="${2:?--commands-dir needs a path}"; shift ;;
    --prefix) PREFIX="${2:?--prefix needs a value}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

ok=0; skipped=0; conflict=0

# link TARGET LINK — idempotent; never clobbers something that is not ours
link() {
  local target="$1" link="$2"
  if [ -L "$link" ]; then
    if [ "$(readlink -f "$link")" = "$(readlink -f "$target")" ]; then
      printf '  ok       %s\n' "$link"; ok=$((ok+1)); return
    fi
    printf '  CONFLICT %s -> %s (expected %s)\n' "$link" "$(readlink "$link")" "$target" >&2
    conflict=$((conflict+1)); return
  fi
  if [ -e "$link" ]; then
    printf '  CONFLICT %s exists and is not a symlink — left alone\n' "$link" >&2
    conflict=$((conflict+1)); return
  fi
  if [ "$CHECK" = 1 ]; then
    printf '  missing  %s\n' "$link"; skipped=$((skipped+1)); return
  fi
  mkdir -p "$(dirname "$link")"
  ln -s "$target" "$link"
  printf '  linked   %s\n' "$link"; ok=$((ok+1))
}

# A flat command dir: one prefixed symlink per command file.
link_commands_flat() {
  local dir="$1" f
  for f in "$REPO"/commands/*.md; do
    link "$f" "$dir/${PREFIX}$(basename "$f")"
  done
}

# A command exists twice on purpose: commands/<x>.md for Claude Code, codex/<x>/SKILL.md for
# Codex. Both hosts read a `name:` key and want different values in it, so the files cannot be
# merged — see codex/README.md. Drift between the two sets is the failure this catches.
check_command_parity() {
  local f n missing=0
  for f in "$REPO"/commands/*.md; do
    n="$(basename "$f" .md)"
    [ -f "$REPO/codex/$n/SKILL.md" ] || { printf '  MISSING  codex/%s/SKILL.md\n' "$n" >&2; missing=1; }
  done
  for f in "$REPO"/codex/*/SKILL.md; do
    n="$(basename "$(dirname "$f")")"
    [ -f "$REPO/commands/$n.md" ] || { printf '  MISSING  commands/%s.md\n' "$n" >&2; missing=1; }
  done
  [ "$missing" = 0 ] && printf '  ok       commands/ and codex/ agree\n'
  return "$missing"
}

echo "$NAME at $REPO"
[ "$CHECK" = 1 ] && echo "(check only — nothing will be written)"

echo "Commands:"
check_command_parity || conflict=$((conflict+1))

# --- Claude Code: namespaced command dir, so the whole directory links at once
if [ -d "$HOME/.claude" ]; then
  echo "Claude Code:"
  link "$REPO" "$HOME/.claude/skills/$NAME"
  link "$REPO/commands" "$HOME/.claude/commands/$NAME"
else
  echo "Claude Code: not installed, skipped"
fi

# --- Codex: skills dir if present, and prompts are a flat directory
if [ -d "$HOME/.codex" ]; then
  echo "Codex:"
  link "$REPO" "$HOME/.codex/skills/$NAME"
  link_commands_flat "$HOME/.codex/prompts"
else
  echo "Codex: not installed, skipped"
fi

# --- Antigravity: global skills live in ~/.gemini/config/skills
# (https://antigravity.google/docs/skills — ~/.gemini alone may be just Gemini CLI)
if [ -d "$HOME/.gemini/antigravity" ]; then
  echo "Antigravity:"
  link "$REPO" "$HOME/.gemini/config/skills/$NAME"
else
  echo "Antigravity: not installed, skipped"
fi

# --- Cursor
if [ -d "$HOME/.cursor" ]; then
  echo "Cursor:"
  link "$REPO" "$HOME/.cursor/skills/$NAME"
else
  echo "Cursor: not installed, skipped"
fi

# --- Vendor-neutral skill location, when this repo lives somewhere else
if [ -d "$HOME/.agents/skills" ] && [ "$REPO" != "$HOME/.agents/skills/$NAME" ]; then
  echo "Agent skills:"
  link "$REPO" "$HOME/.agents/skills/$NAME"
fi

# --- Anything else, by explicit path
if [ -n "$EXTRA_DIR" ]; then
  echo "$EXTRA_DIR:"
  link_commands_flat "$EXTRA_DIR"
fi

echo
echo "linked/ok: $ok · missing: $skipped · conflicts: $conflict"
if [ "$conflict" -gt 0 ]; then
  echo "Resolve the conflicts above by hand — nothing was overwritten." >&2
  exit 1
fi
[ "$CHECK" = 1 ] && [ "$skipped" -gt 0 ] && exit 1
exit 0
