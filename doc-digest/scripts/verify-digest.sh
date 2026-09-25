#!/usr/bin/env bash
# Checks a digest against the original document: line references, reading
# budget and Mermaid syntax. Exits with 1 if anything fails.
# usage: scripts/verify-digest.sh <digest.md> <original.md>
set -u
digest="$1"; orig="$2"
fail=0
ok()  { printf 'OK    %s\n' "$1"; }
err() { printf 'ERROR %s\n' "$1"; fail=1; }

total_lines=$(wc -l < "$orig")
orig_words=$(wc -w < "$orig")

# --- 1. Every L<n> or L<a>-<b> reference points to an existing, non-empty line
refs=$(grep -oE '\bL[0-9]+(-[0-9]+)?\b' "$digest" | sort -u)
bad=0
for r in $refs; do
  start=${r#L}; start=${start%%-*}; end=${r##*-}; end=${end#L}
  for n in $start $end; do
    if [ "$n" -gt "$total_lines" ] || [ -z "$(sed -n "${n}p" "$orig" | tr -d '[:space:]')" ]; then
      err "$r points to line $n, missing or empty in the original"; bad=1
    fi
  done
done
[ "$bad" = 0 ] && ok "$(printf '%s\n' $refs | grep -c .) line references exist in the original"

# --- 2. Budget (words outside the Mermaid block). Section headings are matched
#        by language-agnostic stems: the digest follows the document's language.
read -r bl tldr blocks bullets_max matrix idx words move asked questions <<<"$(awk '
  /^```mermaid/ { inm=1; next }
  inm && /^```/ { inm=0; next }
  inm { next }
  /^## / { sec=$0 }
  { words += NF }
  !sec && /^\*\*[^*]+:\*\* / && !bl { bl = NF }
  sec ~ /TL;DR/ && !/^## / { tldr += NF }
  sec ~ /Vibe/ && /^> \[!/ { blocks++ }
  sec ~ /Vibe/ && /^> - / { b[blocks]++; if (b[blocks] > max) max = b[blocks] }
  sec ~ /[Mm]atri/ && /^\|/ { matrix++ }
  /^## / && /[Ss]ua vez|[Yy]our move/ { move=1 }
  sec ~ /[Ss]ua vez|[Yy]our move/ && /^\*\*[^*]+:\*\*/ { asked=1 }
  sec ~ /[Ss]ua vez|[Yy]our move/ && /^[0-9]+\. / { questions++ }
  sec ~ /ndice|[Ii]ndex/ && /^\|/ { idx++ }
  END { printf "%d %d %d %d %d %d %d %d %d %d", bl, tldr, blocks, max, (matrix ? matrix-2 : 0), (idx ? idx-2 : 0), words, move, asked, questions }
' "$digest")"

if [ "$bl" -eq 0 ]; then err "no bottom line (**<label>:** before the first section)"
else [ "$bl" -le 30 ] && ok "Bottom line with $bl words (max. 30)" || err "Bottom line with $bl words (max. 30)"; fi
[ "$tldr" -le 70 ]        && ok "TL;DR with $tldr words (max. 70)"            || err "TL;DR with $tldr words (max. 70)"
[ "$bullets_max" -le 3 ]  && ok "Box: up to $bullets_max items per block (max. 3)" || err "Box: block with $bullets_max items (max. 3)"
if [ "$move" -eq 0 ]; then err "no Your move section (## Your move / ## Sua vez)"
elif [ "$asked" -eq 0 ]; then err "Your move without the asked line (**<label>:**)"
else [ "$questions" -le 3 ] && ok "Your move with $questions questions (max. 3)" || err "Your move with $questions questions (max. 3)"; fi
[ "$matrix" -le 6 ]       && ok "Matrix with $matrix rows (max. 6)"           || err "Matrix with $matrix rows (max. 6)"
[ "$idx" -le 10 ]         && ok "Index with $idx rows (max. 10)"              || err "Index with $idx rows (max. 10)"
[ "$words" -le 600 ]      && ok "Digest with $words words (max. 600)"         || err "Digest with $words words (max. 600)"
[ "$words" -lt "$orig_words" ] && ok "Digest smaller than the original ($orig_words words)" \
                               || err "Digest ($words words) is not smaller than the original ($orig_words)"

# --- 3. Mermaid syntax: official parser via mermaid+jsdom (no Chromium),
#        else mermaid-cli, else SKIPPED with install instructions.
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
awk '/^```mermaid/{n++; f=1; next} f && /^```/{f=0; next} f{print > sprintf("'"$tmp"'/%d.mmd", n)}' "$digest"

mermaid_modules() {
  for root in "$PWD/node_modules" "$(npm root -g 2>/dev/null)"; do
    [ -d "$root/mermaid" ] && [ -d "$root/jsdom" ] && { echo "$root"; return 0; }
  done
  return 1
}

if ! ls "$tmp"/*.mmd >/dev/null 2>&1; then
  ok "no Mermaid block (short document)"
elif command -v node >/dev/null && root=$(mermaid_modules); then
  MERMAID_MODULES="$root" node "$here/mermaid-parse.mjs" "$tmp"/*.mmd || fail=1
elif command -v npx >/dev/null && npx --no-install -y @mermaid-js/mermaid-cli --version >/dev/null 2>&1; then
  for m in "$tmp"/*.mmd; do
    if npx --no-install -y @mermaid-js/mermaid-cli -q -i "$m" -o "$m.svg" >/dev/null 2>"$m.err"; then
      ok "Mermaid $(basename "$m") valid"
    else
      err "Mermaid $(basename "$m") invalid: $(grep -m1 -iE 'error|parse' "$m.err" | cut -c1-160)"
    fi
  done
else
  cat <<'MSG'
SKIPPED Mermaid not validated: no parser installed. To validate, install one:
        npm i -g mermaid jsdom               (243 MB, no browser, official parser)
        npm i -g @mermaid-js/mermaid-cli     (1.3 GB, includes Chromium)
        Without installing: open the --html digest in a browser or paste the block into https://mermaid.live
MSG
fi

exit $fail
