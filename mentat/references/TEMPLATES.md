# Entry Body Templates

The ten body templates, one per type. Read the one you need — the frontmatter,
naming and tag rules live in [FORMAT.md](FORMAT.md), and `scripts/vault.py write`
writes the frontmatter for you, so this file is only about what goes under it.

> **Atomic bullets.** Prefer direct, self-contained bullets over paragraphs. A
> bullet can be scanned, moved, merged and reused; a paragraph has to be reread
> every time. Prose is worth it only where the reasoning is the content — a
> `decision` rationale, for instance.

Permanent: [bug](#bug) · [decision](#decision) · [feature](#feature) ·
[learning](#learning) · [snippet](#snippet) · [schema](#schema)
Fadeable: [note](#note) · [idea](#idea) · [journal](#journal) · [episodic](#episodic)

---

### note

```markdown
# {title}

## Main Topics

- {topic}

## Details

- {detail}
```

### idea

```markdown
# {title}

## What it is

- {quick description}

## Why it matters

- {value it brings or problem it solves}

## Next Steps

- {what needs to happen}
```

### journal

```markdown
# {title}

## Daily Reflection

- {what happened, thoughts, mental state}

## Highlights

- {item}

## Challenges

- {challenge}
```

### bug

```markdown
# {title}

## Symptoms

- {what was observed — error, unexpected behavior}

## Root Cause

- {why it happened}

## Fix

- {what was changed}

## Changed Files

- `path/to/file.ext`

## Lessons Learned

- {what to watch for next time}
```

### decision

```markdown
# {title}

## Context

- {situation that forced the decision}

## Options Considered

1. **{option A}** — {pros and cons}
2. **{option B}** — {pros and cons}

## Decision

- {which option was chosen}

## Rationale

{why this and not the others — prose is fine here, the reasoning is the content}

## Consequences

- {what changes, and which tradeoffs were accepted}
```

### feature

```markdown
# {title}

## What was built

- {what it does}

## Approach

- {architecture, patterns used}

## Key Files

- `path/to/file.ext` — {role}

## Points of Attention

- {edge cases, known limits, debt}
```

### learning

```markdown
# {title}

## Insight

- {the core lesson in one or two lines}

## Context

- {how or where it emerged}

## Details

- {deeper explanation, examples, references}

## Application

- {when and how to use it}
```

### snippet

````markdown
# {title}

## When to use

- {situation where this applies}

## Code

```{language}
{code}
```

## Notes

- {variations, caveats, alternatives}
````

### episodic

```markdown
# {title}

## Event

- **When:** {YYYY-MM-DD HH:MM}
- **Who:** {Claude / Codex / User}
- **Action:** {what was done}

## Result

- {impact}
```

### schema

```markdown
# {title}

## Abstract Pattern

- {the general rule derived from the related entries}

## Application

- {how to apply it in future}
```

A schema must list its source entries in `related` — an abstraction whose
evidence is untraceable cannot be re-examined when it stops holding.
