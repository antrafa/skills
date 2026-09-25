# Archive — `~/.alterego/`

Where decisions live after the session ends. It is what makes it possible to
answer, six months later, *"why did we pick this?"* without rebuilding the reasoning.

## Layout

```
~/.alterego/
├── INDEX.md                              # one line per dossier (memory lives in Mentat)
├── profile.md                            # only without Mentat (see SKILL.md)
├── journal.md                            # only without Mentat: /alterego wrap closings, one section per date
├── personas/                             # custom personas, created by /alterego persona new
└── decisions/
    └── 2026-09-11-queue-notifications/
        ├── adr.md                        # the record (canonical)
        ├── decision.md                   # the page for whoever signs off
        ├── script.md                     # the 5 minutes of meeting
        └── attachments/                  # optional: source report, diagram, data
```

**One folder per decision.** The name is `<YYYY-MM-DD>-<slug>`: the date sorts
chronologically in `ls` for free, the slug makes the folder greppable. The folder
is also the shareable unit — when the user says "send this to the team", the whole
folder is what goes.

If the decision did not produce all three documents (Phase 0 decided it was
lightweight), save only what exists. A folder with a short `adr.md` beats a
decision that was never recorded.

### Slug naming

Describes **the decision**, not the problem. `queue-notifications`, not
`slow-checkout`. You find a problem again by its text; you find a decision again
by its name. Lowercase, hyphens, no accents.

## ADR.md frontmatter

It is what makes the archive queryable by machine. Mandatory in every `adr.md`.

```yaml
---
decision: Take notification sending off the synchronous request path
project: notifications
context: north-client / production
date: 2026-09-11
status: accepted            # proposed | accepted | superseded | revoked
superseded-by: null     # slug of the superseding decision when status = superseded
quadrant: irreversible-expensive   # reversible-cheap | reversible-expensive | irreversible-cheap | irreversible-expensive
reopen-when: volume exceeds 1M notifications/day or the broker loses HA
sources:
  - docs/performance/analise-2026-09-04.md
  - ~/.alterego/decisions/2026-08-03-connection-pool-per-service/adr.md
mentat: 2026-09-11-queue-notifications   # matching entry, if any
---
```

- **`project`** is the main search axis. Use the name the user says out loud
  (`portal`, `billing`, `mobile-app`), not the repository path.
- **`context`** separates client and environment when the same codebase serves
  several — a recurring reality here.
- **`status`** takes a single value. Use `proposed` until whoever decides accepts
  it; `accepted` in the example presumes that acceptance. When a decision is
  superseded, use `superseded` and fill in **`superseded-by`** with the new
  decision's slug; in the other states, keep that field null.
- **`reopen-when`** is the field that makes the archive age well. Without it,
  every decision looks permanent.

## `INDEX.md`

Exists so Phase 2 does not have to open forty ADRs. One line per decision, most
recent on top.

```markdown
| Date | Decision | Project | Context | Status | Reopen when |
|---|---|---|---|---|---|
| 2026-09-11 | [Queue notifications](decisions/2026-09-11-queue-notifications/) | notifications | north-client / production | accepted | volume > 1M/day |
```

**Writing the folder without writing the line is the mistake that kills the
archive.** The folder exists, and the next session cannot find it.

## Lookup in Phase 2

**The lookup always starts in Mentat**, through the `mentat` skill — it is the
first source of memory. `INDEX.md` comes next, to locate the full dossier of the
decisions Mentat pointed to, or to sweep decisions that never produced an entry.
What to do with what you find, in either of the two:

| What you find | What to do |
|---|---|
| A still-valid earlier decision on the same topic | Cite it. This decision extends it, it does not reopen it |
| An earlier decision whose `reopen-when` has been met | Treat the reopening as part of this decision, and say so |
| A similar decision in **another** project | Use it as precedent, but check whether the context carries over. A different client usually does not |
| Nothing | Say there is no precedent. That is information, not lack of information |

If the archive does not exist yet, create `~/.alterego/decisions/` and `INDEX.md`
with the table header on the first write. Do not tell the user about it — it is
bootstrap, not an event.

## Split with mentat

The two coexist and do not duplicate each other:

| | Archive `~/.alterego/` | Mentat `~/.mentat/` |
|---|---|---|
| Is | a file of dossiers | **the memory** |
| Holds | the decision's full dossier | a short entry, linked into the graph |
| Answers | "why did we decide this way, and what did we give up" | "what do we already know about this topic" |
| Format | ADR + management page + script | note with `[[wiki]]` links |
| Order | consulted **after**, to open the dossier | consulted **first**, always |
| How to write | files, directly | **through the `mentat` skill**, never by hand |

Writing into `~/.mentat/` by hand skips the frontmatter, index and maps the skill
keeps in sync, and the graph drifts from the files.

Mentat is the front door; the archive is the cabinet behind it. Whoever looks for
precedent comes in through Mentat and only opens the archive folder when they need
the whole dossier. A dossier with no matching entry is a dossier the next session
will not find.

The mentat entry points to the archive folder. Never copy the ADR into mentat:
two copies drift apart, and the one in mentat is the one nobody updates.
