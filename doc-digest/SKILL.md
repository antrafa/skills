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
| `# Digest:` | `# Resumo:` |
| `**Bottom line:**` | `**Em uma linha:**` |
| `Implementation Plan` / `Reply` (types; SDD, ADR, Spec/RFC, PR/MR stay) | `Plano de implementação` / `Resposta` |
| `Source` · `Type` · `Mode` | `Origem` · `Tipo` · `Modo` |
| `evolution` / `greenfield` / `in-place` | `evolução` / `greenfield` / `in-place` |
| `## Visual overview` | `## Visão visual` |
| `Legend:` | `Legenda:` |
| `## Decision and change matrix` | `## Matriz de decisões e mudanças` |
| `## Anti-Vibe-Coding Box` | `## Caixa Anti-Vibe-Coding` |
| `## Your move` | `## Sua vez` |
| `**Asked of you:**` | `**Pedem a você:**` |
| `Questions to send back to the agent:` | `Perguntas para devolver ao agente:` |
| `## Quick reference index` | `## Índice de consulta rápida` |
| `Gaps (the document does not cover)` | `Lacunas (o documento não fala de)` |

Two things are never translated: `Anti-Vibe-Coding` stays as a proper name
inside the translated heading, and Mermaid `classDef` names stay in English.

## Procedure

1. **Get the source as a file**; every cited line refers to it. Everything
   this skill writes goes to the output folder `<out>`, never into a
   repository, because a digest is disposable: `~/.doc-digest/<project>/`,
   where `<project>` is the repository containing the document, or the
   current one for text. Get `<out>` and `<commit>` from the script, which
   also creates the folder; pass the document, or `.` for text:
   ```bash
   <skill-folder>/scripts/source-info.sh <doc | .>
   ```
   Use its `out=` and `commit=` lines as printed, rather than recomputing them
   with inline `git` commands: a shell hook that rewrites git output corrupts
   them. `<name>` is the original file name without extension.
   - Local path: use it directly.
   - PR/MR by number or URL: save title and description to a file.
     ```bash
     gh pr view <n> --json title,body -q '"# " + .title + "\n\n" + .body' > <out>/<name>.md
     glab mr view <n> > <out>/<name>.md
     ```
   - Pasted text, or a reply from this conversation ("your last answer"):
     write it verbatim, with nothing added or trimmed, to `<out>/<name>.md`,
     where `<name>` is 3 to 5 kebab-case words naming its subject.
   - A previous version or round of the same text also given (`--since
     <previous>`, "what changed since the last round"): this is a **delta**;
     follow [references/delta.md](references/delta.md), which changes steps
     1, 5 and 6.
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
   it rests on; each mismatch is an internal contradiction. Next, explain
   the central mechanism to yourself in plain words, as to a newcomer
   (Feynman test): every step you can only fill in by guessing is an
   assumption or a gap. Then
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
   `<out>/<name>-digest.md`.
7. **Verify before showing**, with the script in this skill's folder:
   ```bash
   <skill-folder>/scripts/verify-digest.sh <out>/<name>-digest.md <doc>
   ```
   Fix every `ERROR` and re-run until it exits with code 0. Only then proceed.
   If the output contains `SKIPPED`, the diagram was not validated: relay those
   script lines, with the install commands, to the user in chat.
8. **In chat, show only the generated path, the bottom line, the TL;DR, the
   Anti-Vibe-Coding Box and Your move:** the digest's absolute path on one
   line, then those four copied verbatim from the file, so the questions can
   be pasted straight back to the agent. Mermaid does not render in a
   terminal; the file is the visual output.

## Budget

The digest is read in layers: the bottom line in ten seconds; TL;DR, diagram,
Box and Your move in a minute; matrix and index are reference. The step 7
script enforces these limits:

| Block | Limit |
|---|---|
| Bottom line | 30 words |
| TL;DR | 70 words |
| Anti-Vibe-Coding Box | 3 items per block, 1 sentence each |
| Your move | the asked line + 3 questions, 1 sentence each |
| Matrix | 6 rows |
| Index | 10 rows |
| Whole digest, excluding Mermaid | 600 words, and always smaller than the original |

The count includes tables, headings and the legend: a full matrix and index eat
half the budget, so write short cells from the first draft. For a short
document the ceiling becomes the size of the original itself.

Short text (under ~300 words, `wc -w`; lines mislead, since a prose paragraph
is one line): omit diagram and matrix, unless it describes a flow with four
or more steps. TL;DR, Box and Your move are enough.

Under 100 lines, omit the index as well: the reader reaches any line of a
text that short without it, and the words go to Your move.

## Digest template

The template is in English for readability only: keep its structure and
order, and translate its headings and labels as described in Language.

````markdown
# Digest: <document title>

- **Source:** [<name>.md](<absolute path of the original>) · <N> lines · <commit>
- **Type:** <type> · **Mode:** <evolution | greenfield | in-place>

**Bottom line:** <what the text asks you to accept, and its single most damaging
problem from the Box>

## TL;DR
<1 paragraph in SCQA order: what exists today, the problem or pressure, what
the text proposes, and for whom.>

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

## Your move
**Asked of you:** <the approval or decision the text is waiting on> (L<n>)

Questions to send back to the agent:
1. <question whose answer resolves the most damaging Box item>

## Quick reference index
| Section | Line | Why open it |
|---|---|---|
| <title> | L45 | <reason in 5 words> |
````

Filling rules:

- **`<commit>` pins the version the line numbers refer to:** the `commit=`
  line from step 1, with `+ local edits` when the file differs from it. Empty
  (outside a repository, a file never committed, pasted text): omit it.
- **The bottom line is the conclusion, not an introduction:** a reader who
  stops there knows what is being asked and what could go wrong with it.
- **Explain every acronym and term of art on first use**, in plain words
  (`TTL (how long a cached entry lives)`); a reader outside the project
  understands the TL;DR without opening the original.
- **Never invent what the document does not say.** An absence becomes a gap in
  `[!CAUTION]`, not a guess.
- **Every matrix row and every assumption and decision item cites `(L<n>)` or
  `(L<a>-<b>)`** from the original; with no material, the section gets
  shorter. An implicit assumption counts, as long as it cites the excerpt
  that implies it. A gap cites a line when some excerpt touches on the
  subject; a subject that is entirely absent gets no line.
- The `[!CAUTION]` header lists the same 3 gaps detailed below it.
- **Your move turns the Box into the next prompt.** The asked line names
  what the text waits on from the reader (approve, choose, answer); a text
  that asks nothing gets `—`. Each question resolves one Box item, most
  damaging first, and stands alone when pasted into another session: it
  names the subject and carries no reference to this digest ("item 2", "the
  Box").
- In the Reply matrix, `Based on` names the kind of evidence: measured (log,
  metric, test), estimated, or only asserted.
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
| Implementation Plan | `flowchart LR` of phases in execution order, edges = dependencies; a phase with no way back gets class `irreversible`: one that deletes, migrates data or publishes, or that delivers code doing so when run | Phase · Delivers · Depends on · Way back (rollback) |
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

- The per-type table fixes the diagram for an ADR and a plan; for the other
  types, choose by the question the reader brings to the text. Skeletons for
  the last five rows are in [references/diagrams.md](references/diagrams.md).

  | The reader asks | Diagram |
  |---|---|
  | What happens, in what order? | `flowchart LR\|TD` |
  | Who calls whom, in what order? | `sequenceDiagram` |
  | What states can it be in? | `stateDiagram-v2` |
  | How is it organized? | `flowchart TB` with `subgraph`, one zoom level per diagram: system context, containers or components (C4) |
  | What happened, and when? | timeline |
  | What is settled, what is still open? | mind map |
  | Why did it happen? | Ishikawa |
  | How do these ideas relate? | concept map |
  | Which option wins on two criteria? | quadrant |
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
