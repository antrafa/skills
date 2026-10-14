#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
echo "# identity" > README.md
git add -A
git commit -q -m "chore: initial commit"
mkdir -p .alterego/reports
cat > .alterego/reports/login-migration.html <<'HTML'
<!doctype html>
<html><head>
<meta name="alterego-status" content="open">
<meta name="alterego-updated" content="2026-10-01T18:40">
<title>Login migration</title>
</head><body>
<!-- alterego:handoff -->
<pre id="handoff">Goal: move login to the new identity provider.
Stopped at: dev step 4 (TDD), token refresh test red.
Next step: make TokenRefreshTest green in src/auth/refresh.ts.
Report: .alterego/reports/login-migration.html</pre>
<!-- /alterego:handoff -->
</body></html>
HTML
cat > .alterego/reports/old-cache-cleanup.html <<'HTML'
<!doctype html>
<html><head>
<meta name="alterego-status" content="done">
<meta name="alterego-updated" content="2026-09-20T10:00">
<title>Old cache cleanup</title>
</head><body>
<!-- alterego:handoff -->
<pre id="handoff">Goal: remove the legacy cache. All activities done.</pre>
<!-- /alterego:handoff -->
</body></html>
HTML
