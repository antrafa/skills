# Entry Format Reference

Conventions for every vault artifact: frontmatter, the vault's own files and
naming. Read this before writing; the ten body templates live beside it in
[TEMPLATES.md](TEMPLATES.md).

- [Frontmatter](#frontmatter) — the block every entry carries, and the tag rule that breaks vaults
- [Entry bodies by type](TEMPLATES.md) — the ten body templates, in their own file
- [Vault files](#vault-files) — MOC, daily note, index, profile, core memory
- [Naming](#naming) — slugs, links, tags

`scripts/vault.py write` generates frontmatter for you and is the recommended
path — it cannot get the field values wrong. The reference below matters when you
edit an existing entry by hand.

---

## Frontmatter

Every entry opens with the same block. Only the values in the table below vary by
type:

```yaml
---
type: note
date: 2026-01-15
tags: [type/note, lang/typescript]
project: myapp
summary: "One line describing what the entry gives you"
salience: 100
usage_count: 0
last_accessed: 2026-01-15
decayed_at: 2026-01-15
status: open
related: ["[[2026-01-04-api-gateway-timeout]]"]
---
```

| Field | Meaning |
|---|---|
| `type` | Decides permanence and which MOC indexes the entry |
| `date` | Creation date; also the filename prefix. Never changes |
| `tags` | Bare paths, `type/<type>` first. **No `#`** — see below |
| `project` | Project slug, or empty for cross-project knowledge |
| `summary` | The one line the MOC, daily note and index all show. Always quoted — see below |
| `salience` | Current strength. Grows on use, decays while idle |
| `usage_count` | Times the entry proved useful. Monotonic |
| `last_accessed` | Last time the entry was used |
| `decayed_at` | Last time Groom applied decay. Keeps Groom cadence-insensitive — do not remove it |
| `status` | `open`, `resolved` or `superseded` |
| `related` | Quoted wiki-links to sibling entries |

### The `#` rule

**Frontmatter tags must not start with `#`.** In YAML, `#` is a comment
indicator, so `tags: [#type/bug]` does not parse — Obsidian then drops the whole
entry from every tag query and Dataview view. Write bare paths:

```yaml
tags: [type/bug, infra/nginx]     # correct
tags: [#type/bug, #infra/nginx]   # breaks the entry
```

The `#` belongs in two places only: inline tags inside the body text, and search
or graph queries such as `tag:#type/bug`.

### Why `summary` is quoted

`summary` is free text, and free text collects colons: `summary: fixed CORS: only
on 502` is not valid YAML either, and fails the same way — Obsidian drops the
entry from every tag query and Dataview view. `vault.py` quotes it for you. Keep
the quotes if you edit the field by hand.

`summary` is also the source of truth for the one-liner repeated in the MOC, the
daily note and the index. Change it here and run `vault.py reindex --slug <slug>`
to push it out, rather than editing the copies.

### Starting values by type

| Type | Permanence | Starting `salience` | Default `status` |
|---|---|---|---|
| `bug` | permanent | 100 | `resolved` |
| `decision` | permanent | 100 | `open` |
| `feature` | permanent | 100 | `resolved` |
| `learning` | permanent | 100 | `open` |
| `snippet` | permanent | 100 | `open` |
| `schema` | permanent | 200 | `open` |
| `note` | fadeable | 100 | `open` |
| `idea` | fadeable | 100 | `open` |
| `journal` | fadeable | 100 | `open` |
| `episodic` | fadeable | 100 | `resolved` |

Permanent types never fade — they hold knowledge whose value does not expire with
attention. Fadeable types decay while idle and archive once spent. Schema starts
at double salience because it is distilled from several entries, so it should
outrank each of them in recall.

The authoritative numbers live in `scripts/vault.py`; this table mirrors them for
reading convenience.

---

## Entry bodies by type

The ten body templates live in [TEMPLATES.md](TEMPLATES.md) — one section per
type. Read the one you are about to write rather than the whole file; the
templates are independent of each other, and the rules that are not are here.

---

## Vault files

### Map of Content — `~/.mentat/maps/{type}s.md`

```markdown
# {Type}s

## Recent

- [[YYYY-MM-DD-slug]] — one-line summary

## By Project

### [[project-name]]

- [[YYYY-MM-DD-slug]] — one-line summary
```

`vault.py write` puts each new entry at the top of `## Recent`, newest first, and
never trims it — so `## Recent` is the complete index for that type, and reading a
MOC bottom-up is reading that type's history. Only `index.md` is capped.

`## By Project` is an empty heading the vault ships with, for grouping by hand in
Obsidian when a type accumulates enough entries to be worth splitting. Nothing
maintains it automatically, and nothing depends on it being filled.

### Daily note — `~/.mentat/daily/YYYY-MM-DD.md`

```markdown
# {YYYY-MM-DD}

## Entries

- [[YYYY-MM-DD-slug]] — summary ({type})
```

### Index — `~/.mentat/index.md`

```markdown
# Mentat Vault

## Maps of Content

- [[notes]] — General notes and logs
- [[ideas]] — Loose ideas and future projects
- [[journals]] — Reflections and journals
- [[bugs]] — Fixed bugs and debug sessions
- [[decisions]] — Architecture and design decisions
- [[features]] — Built features
- [[learnings]] — Things learned
- [[snippets]] — Code patterns and recipes
- [[episodics]] — Recorded events and actions
- [[schemas]] — Synthesized abstract patterns

## Recent Entries

- [[YYYY-MM-DD-slug]] — one-line summary
```

`## Recent Entries` is capped — newest first, oldest dropped. `vault.py write`
enforces the cap; the MOCs remain the complete index.

### Profile — `~/.mentat/profile.md`

One per vault, created by the **Profile** operation.

```markdown
# Profile

## Identity

- **Name:** {name}
- **Role:** {role or profession}
- **Language:** {preferred communication language}

## Stack

- **Languages:** {e.g. [[typescript]], [[python]]}
- **Frameworks:** {e.g. [[nextjs]], [[fastapi]]}
- **Tools:** {editors, CLI tools, OS}

## Preferences

- {working style, communication preferences, conventions to respect}
```

### Core memory — `~/.mentat/core-memory.md`

One global file plus optional `core-memory-{project}.md`, both on this template.
`init-vault.sh` writes the first one; this template governs edits after that. Read
on demand via **Load**, never automatically.

```markdown
# Core Memory & Intent

## Intent Anchor

{the current overarching objective}

## Rules & Constraints

- {constraint}

## World State

{brief summary of current context, max 500 words}
```

---

## Naming

| Element | Format | Example |
|---|---|---|
| Entry file | `YYYY-MM-DD-slug.md` | `2026-01-15-fix-auth-token-refresh.md` |
| Slug | kebab-case, max 6 words | `fix-auth-token-refresh` |
| Wiki-link | `[[kebab-case]]` | `[[react]]`, `[[retry-with-backoff]]` |
| Frontmatter tag | `category/subcategory` | `lang/typescript`, `infra/docker` |
| Inline tag | `#category/subcategory` | `#lang/typescript` |

Slugs describe the finding, not the topic: `fix-auth-token-refresh` tells you what
you will get, `auth-notes` does not.

### Tag categories

Consistency here is what makes tags searchable — a category used two ways is worse
than no category:

- `type/` — entry type, always first (`type/bug`, `type/schema`)
- `lang/` — languages (`lang/typescript`, `lang/python`)
- `framework/` — frameworks (`framework/nextjs`, `framework/fastapi`)
- `infra/` — infrastructure (`infra/docker`, `infra/aws`)
- `pattern/` — patterns (`pattern/retry`, `pattern/circuit-breaker`)
- `domain/` — business domain (`domain/auth`, `domain/payments`)
- `tool/` — tools (`tool/git`, `tool/obsidian`)
