#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
cat > client.py <<'PY'
import time

def fetch(call, attempts=3):
    for i in range(attempts):
        try:
            return call()
        except ConnectionError:
            time.sleep(1)
    raise ConnectionError("gave up")
PY
git add -A
git commit -q -m "chore: initial import"
