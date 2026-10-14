#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p notify
cat > notify/send.py <<'PY'
import json
import urllib.request


def send(url, message):
    body = json.dumps({"text": message}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=5).status
PY
git add -A
git commit -q -m "feat(notify): post a message to a webhook"
