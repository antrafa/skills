#!/usr/bin/env bash
# Wires the `forja` skill into installed AI agents. Idempotent.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${FORJA_BACKUP_ROOT:-$HOME/.forja/install-backups}"

mkdir -p ~/.forja/progress

link() {
  local target=$1 link_path=$2 backup_path
  mkdir -p "$(dirname "$link_path")"

  if [ "$target" = "$link_path" ]; then
    echo "  source  $link_path"
    return
  fi

  if [ -e "$link_path" ] && [ ! -L "$link_path" ]; then
    mkdir -p "$BACKUP_ROOT"
    backup_path="$BACKUP_ROOT/$(printf '%s' "$link_path" | tr '/' '_')"
    if [ -e "$backup_path" ]; then
      echo "error: backup already exists: $backup_path" >&2
      exit 1
    fi
    mv "$link_path" "$backup_path"
    echo "  backup  $link_path -> $backup_path"
  fi

  ln -sfn "$target" "$link_path"
  echo "  link  $link_path -> $target"
}

# Registers the PreToolUse guard in Claude Code's user settings. The guard is inert
# unless ~/.forja/tutor-active exists, so registering it is safe for every session.
register_hook() {
  local settings=$HOME/.claude/settings.json
  local script=$SKILL_DIR/hooks/forja-guard.py

  if ! command -v python3 >/dev/null 2>&1; then
    echo "  skip  guard hook (python3 not found) — register it by hand:"
    echo "        PreToolUse matcher 'Write|Edit|MultiEdit|NotebookEdit|Bash' -> python3 $script"
    return
  fi

  [ -f "$settings" ] && cp "$settings" "$settings.forja-bak"

  python3 - "$settings" "$script" <<'PY'
import json, os, sys

settings_path, script = sys.argv[1], sys.argv[2]
command = f"python3 {script}"
matcher = "Write|Edit|MultiEdit|NotebookEdit|Bash"

try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

entries = settings.setdefault("hooks", {}).setdefault("PreToolUse", [])
for entry in entries:
    hooks = entry.get("hooks", [])
    if any("forja-guard.py" in h.get("command", "") for h in hooks):
        # Repoint an existing registration instead of stacking a second one.
        entry["matcher"] = matcher
        for h in hooks:
            if "forja-guard.py" in h.get("command", ""):
                h["command"] = command
        break
else:
    entries.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})

os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
print(f"  hook  {settings_path} -> forja-guard.py")
PY
}

echo "forja -> $SKILL_DIR"

link "$SKILL_DIR" ~/.agents/skills/forja
[ -d ~/.claude ]          && link "$SKILL_DIR"                   ~/.claude/skills/forja
[ -d ~/.codex ]           && link "$SKILL_DIR"                   ~/.codex/skills/forja
[ -d ~/.codex ]           && link "$SKILL_DIR/commands/forja.md" ~/.codex/prompts/forja.md
[ -d ~/.gemini ]          && link "$SKILL_DIR"                   ~/.gemini/skills/forja
[ -d ~/.gemini ]          && link "$SKILL_DIR/commands/forja.md" ~/.gemini/commands/forja.md
[ -d ~/.config/opencode ] && link "$SKILL_DIR/commands/forja.md" ~/.config/opencode/commands/forja.md

[ -d ~/.claude ] && register_hook

echo "progress: ~/.forja/progress/"
