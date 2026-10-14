#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
cat > README.md <<'MD'
# reports-service

this service generates the reports. It is the service that does the reports for the
clients and it uses a queue. To run it you need to run it with docker compose up and
then it works. The reports are generated every night and you can also generate them
by hand with the endpoint.

## Setup
install docker. then run docker compose up. then go to localhost:8080
MD
git add -A
git commit -q -m "chore: initial import"
