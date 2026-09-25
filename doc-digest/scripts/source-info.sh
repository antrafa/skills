#!/usr/bin/env bash
# Prints the digest output folder, creating it, and the commit that pins the
# document's line numbers. Kept in a script because shell hooks that rewrite
# git commands (RTK prints "ok", with no newline, for a clean `git status`)
# corrupt the output an agent reads when it runs them inline.
# usage: scripts/source-info.sh <document | directory for pasted text>
set -eu
target="$1"
if [ -d "$target" ]; then dir=$(cd "$target" && pwd); doc=""
else dir=$(cd "$(dirname "$target")" && pwd); doc="$dir/$(basename "$target")"; fi

out=~/.doc-digest
commit=""
if top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null); then
  out="$out/$(basename "$top")"
  if [ -n "$doc" ]; then
    commit=$(git -C "$dir" log -1 --format=%h -- "$doc")
    if [ -n "$commit" ] && [ -n "$(git -C "$dir" status --porcelain -- "$doc")" ]; then
      commit="$commit + local edits"
    fi
  fi
fi
mkdir -p "$out"
printf 'out=%s\ncommit=%s\n' "$out" "$commit"
