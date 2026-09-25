# Delta: what changed since the previous round

For iterated texts (concept rounds, SDD revisions, a plan re-issued after
review), the reader has already read the previous version and wants only the
change. The delta digest is the regular digest with three steps changed;
everything else in SKILL.md holds.

## Step 1: two sources

Save the previous version exactly like the current one (a file is used
directly; pasted text goes verbatim to `<out>/<name>-previous.md`). Every
`L<n>` points to the **current** version, which is what `verify-digest.sh`
checks. Cite the previous one as `(previous)`, translated, never with a line
number.

## Step 5: cross-check the two versions

Before ranking, list every item of the previous version (decision, open
question, discarded option, requirement) and find each one in the current
version. Each item lands in exactly one bucket:

- **Decided now**: open before, settled now.
- **Changed**: settled before, settled differently now.
- **Reopened**: settled or discarded before, open again now.
- **Vanished**: present before, absent now, with no word on why.

An item unchanged in both versions is not part of the delta, and neither is
a discarded option the current version simply does not repeat: it stays
discarded. The step is done
when every item of the previous version has a bucket or is unchanged.

**Vanished** ranks first in damage: an open question that disappears without
an answer is a decision nobody made. It goes into `[!CAUTION]` as a gap, and
into the first Your move question. A **Changed** decision whose effect
reaches something outside the text's scope (shared config, another team's
system) ranks right after it.

## Step 6: the delta template

Changes to the regular template, in the document's language:

- Metadata gains `- **Previous:** [<previous>.md](<absolute path>)` below
  `Source`.
- **Bottom line**: what this round settles, and its most damaging change.
- **TL;DR**: where the previous round stopped, what this one moves, what is
  still open.
- **Diagram**: a mind map with the four buckets as branches, only the
  non-empty ones, replacing the per-type diagram.
- **Matrix**: replaced by the change table below, under the heading
  `## What changed`. It is the matrix's slot, with the same 6-row limit.

```markdown
## What changed
| Item | Before | Now | Effect |
|---|---|---|---|
| <item> (L<n>) | <previous state> | <current state, or — when vanished> | <what it changes for the implementer> |
```

The Box and Your move describe the current version, weighted by the delta:
a risk the previous version already carried and the current one still does
stays in the Box only if it is among the 3 most damaging. The change table
already states each change, so a Box item says what the change hides, never
the change itself. A round is often short, and the digest must still come out
smaller than the current version.

| Template (English) | Portuguese |
|---|---|
| `Previous` / `(previous)` | `Anterior` / `(anterior)` |
| `## What changed` | `## O que mudou` |
| `Item` · `Before` · `Now` · `Effect` | `Item` · `Antes` · `Agora` · `Efeito` |
| `Decided now` · `Changed` · `Reopened` · `Vanished` | `Decidido agora` · `Mudou` · `Reaberto` · `Sumiu` |
