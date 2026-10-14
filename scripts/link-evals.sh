#!/bin/sh
# Links evals/<skill> back to <skill>/evals, where the eval runners and the case
# paths expect it. The suites live outside the skill folders so that installing a
# skill does not ship its fixtures, which carry deliberate vulnerabilities and fake
# secrets for the skill to find. The links are gitignored.
set -eu

root=$(cd "$(dirname "$0")/.." && pwd)
for suite in "$root"/evals/*/; do
  skill=$(basename "$suite")
  [ -d "$root/$skill" ] || continue
  ln -sfn "../evals/$skill" "$root/$skill/evals"
  echo "  link  $skill/evals -> evals/$skill"
done
