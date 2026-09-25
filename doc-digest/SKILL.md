---
name: doc-digest
description: Digests long AI output — an agent reply, SDD, ADR, plan, spec, RFC, PR/MR — given as a file or pasted text into a one-minute visual read, and surfaces its hidden risks, assumptions and trade-offs. Use when the user asks to digest, summarize, visualize or extract risks from a long text, in any language — e.g. "mastiga essa resposta", "resume isso", "quais os riscos desse plano".
license: MIT
---

# Doc Digest

Produces a visual digest of a long text — a document or an agent reply — so
the developer decides consciously instead of skimming and coding blind.
Default output is Markdown; `--html` also generates a standalone page.

## Language

Two languages, decided separately:

- **The digest is written in the language of the source document** — not the
  language of the prompt, and not English merely because this skill is written
  in English. Never translate the document. A Portuguese document invoked by
  `/doc-digest <path>` still produces a fully Portuguese digest.
- **Chat replies follow the user's language**, whatever the document's
  language is.

This applies to every fixed string the template prescribes: section headings,
the metadata labels (`Source`, `Type`, `Mode`), the mode name, `Legend`, the
column headers and the bold titles inside the Box. English headings over
document-language content are a defect. For a Portuguese document:

| Template (English) | Portuguese |
|---|---|
| `Source` · `Type` · `Mode` | `Origem` · `Tipo` · `Modo` |
| `evolution` / `greenfield` / `in-place` | `evolução` / `greenfield` / `in-place` |
| `## Visual overview` | `## Visão visual` |
| `Legend:` | `Legenda:` |
| `## Decision and change matrix` | `## Matriz de decisões e mudanças` |
| `## Anti-Vibe-Coding Box` | `## Caixa Anti-Vibe-Coding` |
| `## Quick reference index` | `## Índice de consulta rápida` |
| `Gaps (the document does not cover)` | `Lacunas (o documento não fala de)` |

Two things are never translated: `Anti-Vibe-Coding` stays as a proper name
inside the translated heading, and Mermaid `classDef` names stay in English.

## Procedure

1. **Get the source as a file**; every cited line refers to it.
   - Local path: use it directly.
   - PR/MR by number or URL: save title and description to a file.
     ```bash
     gh pr view <n> --json title,body -q '"# " + .title + "\n\n" + .body' > docs/digests/<name>.md
     glab mr view <n> > docs/digests/<name>.md
     ```
   - Pasted text, or a reply from this conversation ("your last answer"):
     write it verbatim, with nothing added or trimmed, to
     `docs/digests/<name>.md` at the root of the current repository
     (`git rev-parse --show-toplevel`), or in the current directory outside
     one. `<name>` is 3 to 5 kebab-case words naming its subject.
2. **Map the headings with exact line numbers**, ignoring anything inside code
   blocks, and note the total line count N (`wc -l <doc>`):
   ````bash
   # $(0) and not the short form: Claude Code replaces the short form with the skill argument
   awk '/^```/{f=!f} !f && /^#+ /{print NR": "$(0)}' <doc>
   ````
3. **Read the whole document, up to line N.** Never digest from an excerpt.
   Over ~1500 lines, read it in blocks; the step is done when the last block
   read ends at line N.
4. **Classify type and mode.** Type: SDD | ADR | Implementation Plan |
   Spec/RFC | PR/MR | Reply (an ADR has Context/Decision/Consequences; a plan
   has phases/tasks; a PR has "what changed/how to validate"; Reply is
   everything else: an explanation, analysis, comparison or recommendation).
   The type decides the diagram and the matrix columns (see Per type). Mode
   applies only when the text changes a system; a Reply that changes none
   drops the Mode label. Mode:
   - **evolution**: a system exists and something changes in it (default case);
   - **greenfield**: nothing exists yet, everything is new;
   - **in-place**: the same component is both before and after (DDL, refactor).
   A mixed document (backend evolves, app is new) and a new system replacing a
   legacy one are both evolution. When the document does not make clear what
   already exists, record it as a gap.
5. **Select and rank.** First cross-check the text against itself: every
   requirement against the contract that serves it (endpoint, schema, field),
   every contract against a requirement, and every conclusion against what
   it rests on; each mismatch is an internal contradiction. Then
   list every assumption and decision you found, and classify each gap
   category as covered or gap: rollback, security,
   concurrency, observability, testing, data migration, external dependency
   mentioned but not specified. Covered means the document says **how**; a
   mention without the how is a gap. Keep the 3 most damaging of each block,
   in this order of damage: internal contradiction in the document
   (requirement without contract, contract without requirement) > what breaks
   in production or in the implementer's day-to-day, including the most
   fragile dependency > decision without justification > the rest. Whatever
   is left out is dropped, not moved to an appendix.
6. **Write the digest** using the template below, within budget, and save it to
   `docs/digests/<name>-digest.md` (create the folder), where `<name>` is the
   original file name without extension and `docs/digests/` sits at the root of
   the repository containing the document
   (`git -C <doc-dir> rev-parse --show-toplevel`). Outside a repository, save
   it next to the original.
7. **Verify before showing**, with the script in this skill's folder:
   ```bash
   <skill-folder>/scripts/verify-digest.sh docs/digests/<name>-digest.md <doc>
   ```
   Fix every `ERROR` and re-run until it exits with code 0. Only then proceed.
   If the output contains `SKIPPED`, the diagram was not validated: relay those
   script lines, with the install commands, to the user in chat.
8. **In chat, show only the generated path, the TL;DR and the Anti-Vibe-Coding
   Box:** the path relative to the repository root on one line, then the two
   sections copied verbatim from the file. Mermaid does not render in a
   terminal; the file is the visual output.

## Budget

The digest is read in about a minute: TL;DR, diagram and Box are the reading;
matrix and index are reference. The step 7 script enforces these limits:

| Block | Limit |
|---|---|
| TL;DR | 70 words |
| Anti-Vibe-Coding Box | 3 items per block, 1 sentence each |
| Matrix | 6 rows |
| Index | 10 rows |
| Whole digest, excluding Mermaid | 600 words, and always smaller than the original |

The count includes tables, headings and the legend: a full matrix and index eat
half the budget, so write short cells from the first draft. For a short
document the ceiling becomes the size of the original itself.

Short document (under ~60 lines): omit diagram and matrix, unless it describes
a flow with four or more steps. TL;DR, Box and index are enough.

## Digest template

The template is in English for readability only: keep its structure and
order, and translate its headings and labels as described in Language.

````markdown
# Digest: <document title>

- **Source:** [<name>.md](<path relative to the digest file>) · <N> lines · <commit>
- **Type:** <type> · **Mode:** <evolution | greenfield | in-place>

## TL;DR
<1 paragraph: what it proposes, for whom, why. No jargon.>

## Visual overview
```mermaid
<diagram>
```
Legend: <the one for the type or mode, only with the classes present in the diagram>

## Decision and change matrix
| Component / Area | What changes | How it changes (technique) | What does NOT change (protected scope) |
|---|---|---|---|
| <component> (L<n>) | ... | ... | ... or — |

## Anti-Vibe-Coding Box
> [!WARNING]
> **Assumptions the document makes that you need to validate:**
> - <assumption> (L<n>)

> [!IMPORTANT]
> **Decisions the document made for you:**
> - <decision> (L<n>)

> [!CAUTION]
> **Gaps (the document does not cover):** <only the categories actually missing>
> - <category>: <what would need to be there> (L<n> where the subject nearly
>   appears, if any)

## Quick reference index
| Section | Line | Why open it |
|---|---|---|
| <title> | L45 | <reason in 5 words> |
````

Filling rules:

- **`<commit>` pins the version the line numbers refer to:**
  `git -C <doc-dir> log -1 --format=%h -- <doc>`, followed by `+ local edits`
  when `git status --porcelain <doc>` is not empty. Outside a repository or
  for a file never committed, omit it.
- **Never invent what the document does not say.** An absence becomes a gap in
  `[!CAUTION]`, not a guess.
- **Every matrix row and every assumption and decision item cites `(L<n>)` or
  `(L<a>-<b>)`** from the original; with no material, the section gets
  shorter. An implicit assumption counts, as long as it cites the excerpt
  that implies it. A gap cites a line when some excerpt touches on the
  subject; a subject that is entirely absent gets no line.
- The `[!CAUTION]` header lists the same 3 gaps detailed below it.
- The matrix header above is the SDD one; other types use their columns from
  Per type.
- A cell with no material becomes `—`. In greenfield, "what does NOT change" is
  the scope the document protects (deny list, untouched folders), not a
  previous system.

## Per type

| Type | Diagram | Matrix columns |
|---|---|---|
| SDD, Spec/RFC | components and the flow between them, marked by mode | Component / Area · What changes · How it changes (technique) · What does NOT change (protected scope) |
| ADR | `flowchart LR`: the problem → each option considered, the chosen one with class `chosen`, the deciding criterion on its edge | Option · In favor · Against · Why chosen or dropped |
| Implementation Plan | `flowchart LR` of phases in execution order, edges = dependencies; a step with no way back (delete, migrate data, publish) gets class `irreversible` | Phase · Delivers · Depends on · Way back (rollback) |
| PR/MR | areas touched and the flow they affect, marked by mode | Area · What changes · What it may break · How to validate |
| Reply | chosen by content (see Diagram rules); none when the text has no flow, structure or comparison | Point · Conclusion · Based on · Still open |

```
classDef chosen stroke-width:3px
classDef irreversible stroke:#D4380D,stroke-width:2px
```

Legends: ADR "thick border = chosen option"; plan "arrow = depends on · red
border = no way back". The mode conventions below apply to component diagrams
(SDD, Spec/RFC, PR/MR, a Reply that changes a system); in an ADR or a plan
the mode only goes in the metadata.

## Diagram rules

- Choose by content: data/process flow → `flowchart LR|TD`; interaction between
  services/layers → `sequenceDiagram`; lifecycle → `stateDiagram-v2`;
  modules/architecture → `flowchart TB` with `subgraph`.
- Existing vs. new vs. modified convention in `flowchart`:
  ```
  classDef new stroke-dasharray: 5 5
  classDef modified stroke-dasharray: 5 5,stroke:#D4380D
  ```
  In `sequenceDiagram`, prefix new participants with `[NEW]`.
- External systems and environment (OS, database, stream, third-party API) are
  always a solid box. The legend names only the classes present in the diagram;
  a class with no node is dropped from both the legend and the `classDef`.
- Per mode:
  - **evolution**: legend "solid box = already exists · dashed = new · red
    dashed = modified", without the term whose class does not appear.
  - **greenfield**: everything the document creates is `new`. Legend "solid box
    = existing environment · dashed = new".
  - **in-place**: two nodes for the same component, `Before` solid and `After`
    with class `modified`, linked by an edge carrying the migration step.
- Labels containing `(`, `/`, `:` or quotes go inside `["..."]`, otherwise
  Mermaid breaks.
- Maximum ~12 nodes. If you need more, the document has more than one flow:
  draw two small diagrams.

## `--html` mode

Only when the user writes `--html`; "visual" or "page" in natural language do
not trigger it. Then follow [references/html.md](references/html.md).
