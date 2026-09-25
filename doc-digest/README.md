# Doc Digest (`doc-digest`)

Visual synthesis of long AI output: an agent reply pasted as text, or a
document such as an SDD, ADR, implementation plan, spec, RFC or PR/MR
description. Instead of 20 pages of markdown, a
one-minute digest with a Mermaid diagram, a decision matrix, hidden risks and
assumptions, and an index with exact line numbers from the original document.

## The problem

AI agents generate documentation in bulk. The developer skims instead of
reading it and moves on to the code. The result is blind *vibe coding*: fragile
assumptions, broken contracts, no rollback, and side effects that only show up
in production or in review.

Doc Digest is a filter between the document and the human decision. It does not
summarize for the sake of summarizing: it separates what already exists from
what changes, exposes what the document assumed without saying so, and points
out what it does not cover.

## Language

The skill is written in English; the output is not. The digest is always
written in the **same language as the source document** — a Portuguese SDD
produces a Portuguese digest, section headings included — and the assistant
replies in chat in the **user's language**. Nothing is ever translated.

## What comes out

A `~/.doc-digest/<project>/<doc-name>-digest.md` file, outside the
repository because a digest is disposable (`<project>` is the repository name;
outside a repository the file goes straight into `~/.doc-digest/`). Pasted text
is first saved verbatim next to it, so line references have a file to point at.
The digest contains:

1. **TL;DR** in a single paragraph of up to 70 words.
2. **Visual overview** in Mermaid, shaped by the document type: components
   marked existing, new or modified (SDD, spec, PR/MR), options with the
   chosen one highlighted (ADR), or phases in order with the irreversible
   steps marked (plan).
3. **Decision and change matrix**, with columns by type: what changes and what
   does NOT change (SDD), options for and against (ADR), dependencies and way
   back (plan), risk and how to validate (PR/MR).
4. **Anti-Vibe-Coding Box**: the 3 most damaging assumptions, decisions and
   gaps, each citing a line in the original.
5. **Quick reference index** with the exact line number of each section.

The header pins the original's commit hash, so a digest whose line numbers no
longer match a revised document is easy to spot. TL;DR, diagram and Box are
the one-minute read. Matrix and index are reference.
The whole digest fits in 600 words excluding the diagram and is always smaller
than the original; a short document comes out without a diagram or a matrix.

Chat shows only the absolute file path, the TL;DR and the Box. Mermaid does
not render in a terminal; open the `.md` in VS Code or use `--html`.

With `--html` the skill also generates `<name>-digest.html` in the same folder,
standalone, with Mermaid.js from a CDN, ready for `xdg-open` (Linux) or `open`
(macOS).

The exact structure, the budget, the diagram rules and the filling rules live
in [SKILL.md](SKILL.md), the single source of truth for the template.

## Verification

Before showing the result, the skill runs `scripts/verify-digest.sh` over the
digest and the original. The script checks that every cited line exists, that
the budget was respected and that the Mermaid compiles. It exits with code 1 if
anything fails, and the skill fixes the problem before moving on. The script can
also be run by hand:

```bash
scripts/verify-digest.sh ~/.doc-digest/my-repo/my-sdd-digest.md docs/specs/my-sdd.md
```

Section headings are matched by language-agnostic stems, so the budget check
works regardless of the digest's language.

Mermaid validation uses whatever is installed, in this order:

| Option | Install | Size | Note |
|---|---|---|---|
| `mermaid` + `jsdom` | `npm i -g mermaid jsdom` | 243 MB | official parser, no browser; a project's `node_modules` works too |
| `mermaid-cli` | `npm i -g @mermaid-js/mermaid-cli` | 1.3 GB | includes Chromium |
| none | | | the script prints `SKIPPED` and the skill relays the warning in chat |

With nothing installed, the check is manual: open the `--html` digest in a
browser or paste the block into [mermaid.live](https://mermaid.live). A broken
diagram shows the error on screen.

## Evals

`evals/evals.json` contains four cases with the documents in `evals/files/`: a
short ADR (digest with no diagram), an SDD in evolution mode with a contract
inconsistency the Box must catch, a 900-line greenfield plan with `--html`, and
an agent reply pasted as text, with a contradiction between cache TTL and
freshness the Box must catch. All four sources are in Portuguese, which also
covers the rule that the digest keeps the document's language while the skill
itself is in English.
Format compatible with Anthropic's
[skill-creator](https://github.com/anthropics/skills).

## Install

Clone the repository and link it into each agent's skills directory:

```bash
SRC=~/workspace/pessoal/skills/doc-digest   # adjust to where you cloned it
for d in ~/.claude/skills ~/.agents/skills ~/.codex/skills ~/.gemini/config/skills; do
  mkdir -p "$d" && ln -sfn "$SRC" "$d/doc-digest"
done
```

| Directory | Agent |
|---|---|
| `~/.claude/skills` | Claude Code |
| `~/.codex/skills` | Codex |
| `~/.gemini/config/skills` | Antigravity |
| `~/.agents/skills` | shared default (Cursor, OpenCode and others) |

Optional, to validate Mermaid: `npm i -g mermaid jsdom` (see Verification).

## Usage

```
# Claude Code / Antigravity
/doc-digest docs/adr/0001-new-database.md
/doc-digest docs/specs/auth-service-sdd.md --html
/doc-digest 42            # PR/MR by number, via gh or glab

# Codex
$doc-digest docs/superpowers/plans/2026-09-19-feature.md
```

Non-interactive:

```bash
claude -p "/doc-digest docs/specs/sdd-feature.md"
codex exec "\$doc-digest docs/specs/sdd-feature.md"
agy --print "/doc-digest docs/specs/sdd-feature.md"
```

Pasted text works too: "resume isso: <text>", or "mastiga sua última
resposta" for a reply from the same conversation.

It also triggers from natural language, in any language: "summarize this SDD
visually", "walk me through this plan with diagrams", "what are the hidden
risks and assumptions in this document?", "mastiga esse plano com diagramas".

## License

[MIT](LICENSE). Built by [Antonio Rafael Ortega](https://github.com/antrafa).
