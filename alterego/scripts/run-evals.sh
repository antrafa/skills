#!/bin/sh
# Runs the eval suite in evals/ with this repository's defaults.
#
#   --no-publish   the report stays local; claude plugin eval publishes to claude.ai by default
#   --output-dir   results go outside the repo: the plugin declares "." as its skill path, so
#                  the CLI refuses to write results inside it
#   --scaffold     runs each case's fixture.sh, which only builds a throwaway git repo
#   --allow-tools  the cases that commit, edit or run tests need Bash, Edit and Write; the grant
#                  applies to every case, and Bash runs inside the OS sandbox
#
# Extra arguments go straight to claude plugin eval, e.g.:
#   scripts/run-evals.sh --tag smoke --runs 1 --ablation none
#   scripts/run-evals.sh --case '0[3-6]-*' --max-cost-usd 2
set -eu

root=$(cd "$(dirname "$0")/.." && pwd)
out=${ALTEREGO_EVAL_OUT:-${XDG_CACHE_HOME:-$HOME/.cache}/alterego-evals/$(date +%Y%m%d-%H%M%S)}

exec claude plugin eval "$root" \
  --no-publish \
  --output-dir "$out" \
  --scaffold \
  "$@" \
  --allow-tools Bash Edit Write
