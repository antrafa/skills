#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p skills/release-notes
cat > skills/release-notes/SKILL.md <<'MD'
---
name: release-notes
description: Use when the user asks for release notes, changelog, change log, changes list, list of changes, what changed, what's new, version notes, release summary, release report or ship notes. Writes release notes. This skill writes release notes from git history for the user.
---

# Release notes

You are a helpful assistant that writes release notes. Always be helpful.

1. Read the git log since the last tag.
2. Group commits by type.
3. Write the notes.

Do not forget to write the notes. Never write bad notes. Be clear.

## Format
Group by feat, fix and chore. Group commits by type before writing.
MD
git add -A
git commit -q -m "chore: initial import"
