#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
echo "# identity" > README.md
git add -A
git commit -q -m "chore: initial commit"
