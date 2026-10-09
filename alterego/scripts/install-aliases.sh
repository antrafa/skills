#!/usr/bin/env bash
# Generates and installs shell aliases/functions for AlterEgo commands.
# Supports Claude Code (cl-*), Antigravity (agy-*), and Codex (cx-*).
# Idempotent and non-intrusive: writes to ~/.alterego/aliases.sh and sources it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_DIR="${HOME}/.alterego"
TARGET_FILE="${TARGET_DIR}/aliases.sh"

UNINSTALL=0
DRY_RUN=0

usage() {
  cat <<EOF
Usage: install-aliases.sh [options]

Options:
  --dry-run      Print generated aliases to stdout without modifying files
  --uninstall    Remove AlterEgo aliases and clean up shell configuration
  -h, --help     Show this help message
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

# Detect shell RC file
detect_rc_file() {
  if [ -n "${ZSH_VERSION:-}" ] || [ "${SHELL##*/}" = "zsh" ]; then
    echo "${HOME}/.zshrc"
  elif [ -n "${BASH_VERSION:-}" ] || [ "${SHELL##*/}" = "bash" ]; then
    if [ -f "${HOME}/.bashrc" ]; then
      echo "${HOME}/.bashrc"
    else
      echo "${HOME}/.bash_profile"
    fi
  else
    if [ -f "${HOME}/.zshrc" ]; then
      echo "${HOME}/.zshrc"
    elif [ -f "${HOME}/.bashrc" ]; then
      echo "${HOME}/.bashrc"
    else
      echo "${HOME}/.profile"
    fi
  fi
}

RC_FILE="$(detect_rc_file)"
SOURCE_LINE="[ -f \"${TARGET_FILE}\" ] && source \"${TARGET_FILE}\""

# Handle uninstallation
if [ "$UNINSTALL" -eq 1 ]; then
  echo "=== Removendo atalhos do AlterEgo ==="
  if [ -f "$RC_FILE" ] && grep -Fq "$TARGET_FILE" "$RC_FILE" 2>/dev/null; then
    # Remove source block cleanly
    TMP_RC="$(mktemp)"
    grep -v -F "$TARGET_FILE" "$RC_FILE" | grep -v "# AlterEgo CLI Shortcuts" > "$TMP_RC" || true
    mv "$TMP_RC" "$RC_FILE"
    echo "  [rc] Removida integração de $RC_FILE"
  fi
  if [ -f "$TARGET_FILE" ]; then
    rm -f "$TARGET_FILE"
    echo "  [rm] Removido $TARGET_FILE"
  fi
  echo "Desinstalação concluída com sucesso."
  exit 0
fi

# Generate aliases content
generate_content() {
  cat << 'HEADER'
# ------------------------------------------------------------------------------
# AlterEgo CLI Shortcuts
# Generated automatically by alterego/scripts/install-aliases.sh
# ------------------------------------------------------------------------------

HEADER

  COMMANDS=(
    "start" "dev" "refactor" "control" "clear" "daily" "wrap" "review"
    "mr" "adr" "commit" "pr-desc" "tour-project" "project-analyser"
    "idea" "local-app" "digest" "skill" "sre" "study" "setup" "persona" "help"
  )

  # --- Claude Code (cl-*) ---
  if command -v claude >/dev/null 2>&1 || [ "$DRY_RUN" -eq 1 ]; then
    cat << 'EOF'
# --- Claude Code (cl-*) ---
cl-ae() { claude "/alterego${*:+ }$*"; }
cl-alterego() { cl-ae "$@"; }
EOF
    for cmd in "${COMMANDS[@]}"; do
      echo "cl-${cmd}() { claude \"/alterego ${cmd}\${*:+ }\$*\"; }"
    done
    # Conveniences / aliases adicionais
    echo "cl-tour() { cl-tour-project \"\$@\"; }"
    echo "cl-analyse() { cl-project-analyser \"\$@\"; }"
    echo ""
  fi

  # --- Antigravity (agy-*) ---
  if command -v agy >/dev/null 2>&1 || [ "$DRY_RUN" -eq 1 ]; then
    cat << 'EOF'
# --- Antigravity (agy-*) ---
agy-ae() { agy -i "/alterego${*:+ }$*"; }
agy-alterego() { agy-ae "$@"; }
EOF
    for cmd in "${COMMANDS[@]}"; do
      echo "agy-${cmd}() { agy -i \"/alterego ${cmd}\${*:+ }\$*\"; }"
    done
    echo "agy-tour() { agy-tour-project \"\$@\"; }"
    echo "agy-analyse() { agy-project-analyser \"\$@\"; }"
    echo ""
  fi

  # --- OpenAI Codex (cx-*) ---
  if command -v codex >/dev/null 2>&1 || [ "$DRY_RUN" -eq 1 ]; then
    cat << 'EOF'
# --- OpenAI Codex (cx-*) ---
cx-ae() { codex "\$alterego\${*:+ }\$*"; }
cx-alterego() { cx-ae "$@"; }
EOF
    for cmd in "${COMMANDS[@]}"; do
      echo "cx-${cmd}() { codex \"\\\$alterego ${cmd}\${*:+ }\$*\"; }"
    done
    echo "cx-tour() { cx-tour-project \"\$@\"; }"
    echo "cx-analyse() { cx-project-analyser \"\$@\"; }"
    echo ""
  fi

  # --- Terminal Help / Cheatsheet (ae-help) ---
  cat << 'EOF'
# --- Terminal Help Cheatsheet ---
ae-help() {
  cat << 'HELP_MSG'
AlterEgo CLI Shortcuts & Quick Reference

Terminal aliases (opens AI session with AlterEgo pre-loaded):
  Claude Code:     cl-<cmd>       (e.g., cl-daily, cl-sre, cl-review)
  Antigravity:     agy-<cmd>      (e.g., agy-daily, agy-sre, agy-dev)
  OpenAI Codex:    cx-<cmd>       (e.g., cx-daily, cx-sre, cx-mr)

Key subcommands:
  daily               Organize the day and prioritize tasks
  wrap                Close the day and log pending items
  dev [<step>]        Guided 7-step development pipeline
  refactor <goal>     Structural refactor via Mikado Method
  review [<target>]   Socratic code review (file, diff, branch)
  mr [<iid>|<url>]    Remote MR/PR impact evaluation in worktree
  sre <symptom>       Incident investigation by measurement
  adr <decision>      Structural architectural decision record
  idea <idea>         Refine raw idea into testable proposal
  study <topic>       Guided study with Socratic challenges
  commit [<scope>]    Generate commit message from real diff
  pr-desc [<iid>]     Generate MR/PR description in 4 blocks
  tour-project        Technical onboarding of codebase (alias: tour)
  project-analyser    360° technical audit (alias: analyse)
  setup               Calibrate developer profile
  persona [<name>]    Switch technical persona lens
  help [<command>]    Detailed card of any command

Free-form shortcuts:
  cl-ae "<prompt>"    Free-form request in Claude Code
  agy-ae "<prompt>"   Free-form request in Antigravity
  cx-ae "<prompt>"    Free-form request in Codex

In-depth AI explanation for a command:
  cl-help <cmd>  |  agy-help <cmd>  |  cx-help <cmd>
HELP_MSG
}
alterego-help() { ae-help "$@"; }
EOF
}

if [ "$DRY_RUN" -eq 1 ]; then
  generate_content
  exit 0
fi

echo "=== Instalando atalhos de terminal do AlterEgo ==="

mkdir -p "$TARGET_DIR"
generate_content > "$TARGET_FILE"
chmod 644 "$TARGET_FILE"
echo "  [file] Gerado: $TARGET_FILE"

# Detect installed CLIs for user feedback
[ -x "$(command -v claude 2>/dev/null)" ] && echo "  [cli]  Claude Code detectado -> atalhos 'cl-*' ativados"
[ -x "$(command -v agy 2>/dev/null)" ]    && echo "  [cli]  Antigravity detectado -> atalhos 'agy-*' ativados"
[ -x "$(command -v codex 2>/dev/null)" ]  && echo "  [cli]  Codex detectado       -> atalhos 'cx-*' ativados"

# Inject into RC file
mkdir -p "$(dirname "$RC_FILE")"
touch "$RC_FILE"

if ! grep -Fq "$TARGET_FILE" "$RC_FILE" 2>/dev/null; then
  {
    echo ""
    echo "# AlterEgo CLI Shortcuts"
    echo "$SOURCE_LINE"
  } >> "$RC_FILE"
  echo "  [rc]   Adicionada integração em $RC_FILE"
else
  echo "  [rc]   $RC_FILE já contém a integração."
fi

echo ""
echo "Sucesso! Para carregar agora no seu terminal atual, execute:"
echo "  source \"$RC_FILE\""
