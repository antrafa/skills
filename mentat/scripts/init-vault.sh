#!/usr/bin/env bash
# Creates or repairs the Mentat vault structure.
#
# Every step is individually guarded rather than skipped wholesale, so running
# this against a vault that lost a directory or a Map of Content puts the
# missing piece back instead of reporting success and doing nothing.
set -euo pipefail

VAULT_DIR="${MENTAT_VAULT:-${HOME}/.mentat}"
existed=0
[[ -d "$VAULT_DIR/entries" ]] && existed=1

mkdir -p "$VAULT_DIR"/{entries,maps,daily,archive}

if [[ ! -f "$VAULT_DIR/core-memory.md" ]]; then
  cat > "$VAULT_DIR/core-memory.md" << 'EOF'
# Core Memory & Intent

## Intent Anchor
(Define the current main objective)

## Rules & Constraints
- (Constraint 1)

## World State
(Quick summary of the project context)
EOF
fi

# --- Maps of Content ---

for type in notes ideas journals bugs decisions features learnings snippets episodics schemas; do
  if [[ ! -f "$VAULT_DIR/maps/$type.md" ]]; then
    title="$(echo "$type" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')"
    cat > "$VAULT_DIR/maps/$type.md" << EOF
# $title

## Recent

## By Project
EOF
  fi
done

# --- Index (dashboard) ---

if [[ ! -f "$VAULT_DIR/index.md" ]]; then
  cat > "$VAULT_DIR/index.md" << 'EOF'
# Mentat Vault

## Maps of Content

- [[notes]] — General notes and logs
- [[ideas]] — Loose ideas and future projects
- [[journals]] — Reflections and journals
- [[bugs]] — Fixed bugs and debug sessions
- [[decisions]] — Architecture and design decisions
- [[features]] — Built features
- [[learnings]] — Things learned
- [[snippets]] — Code patterns and recipes
- [[episodics]] — Recorded events and actions
- [[schemas]] — Synthesized abstract patterns

## Recent Entries
EOF
fi

# --- Obsidian configuration ---

mkdir -p "$VAULT_DIR/.obsidian"

if [[ ! -f "$VAULT_DIR/.obsidian/app.json" ]]; then
  cat > "$VAULT_DIR/.obsidian/app.json" << 'EOF'
{
  "useMarkdownLinks": false,
  "newLinkFormat": "shortest",
  "showUnsupportedLinks": true,
  "strictLineBreaks": false,
  "readableLineLength": true
}
EOF
fi

if [[ ! -f "$VAULT_DIR/.obsidian/graph.json" ]]; then
  cat > "$VAULT_DIR/.obsidian/graph.json" << 'EOF'
{
  "collapse-filter": false,
  "search": "",
  "showTags": true,
  "showAttachments": false,
  "hideUnresolved": false,
  "showOrphans": true,
  "collapse-color-groups": false,
  "colorGroups": [
    {"query": "tag:#type/bug", "color": {"a": 1, "rgb": 16711680}},
    {"query": "tag:#type/schema", "color": {"a": 1, "rgb": 65535}},
    {"query": "tag:#type/decision", "color": {"a": 1, "rgb": 16776960}}
  ],
  "collapse-display": false,
  "showArrow": true,
  "textFadeMultiplier": 0,
  "nodeSizeMultiplier": 1,
  "lineSizeMultiplier": 1
}
EOF
fi

if [[ "$existed" == 1 ]]; then
  echo "✓ Vault checked at $VAULT_DIR (missing pieces restored)"
  exit 0
fi

echo "✓ Vault initialized at $VAULT_DIR"
echo ""
echo "To use in Obsidian:"
echo "  1. Open Obsidian"
echo "  2. File → Open vault"
echo "  3. Select folder: $VAULT_DIR"
