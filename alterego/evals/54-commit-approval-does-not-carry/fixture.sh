#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
printf '# Report tool\n\nGenerates the montly report.\n' > README.md
printf 'def parse(line):\n    return line.split(",")\n' > parser.py
git add -A
git commit -q -m "chore: initial import"
printf 'def parse(line):\n    return [c.strip() for c in line.split(",")]\n' > parser.py
git add -A
git commit -q -m "fix(parser): strip spaces around fields"
