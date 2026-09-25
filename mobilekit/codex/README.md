# codex/

One `SKILL.md` per command, because Codex discovers commands differently than Claude Code does.

Codex has two surfaces and they are not the same thing:

| Surface | Invoked as | Reads frontmatter |
|---|---|---|
| Custom prompts (`~/.codex/prompts/`) | `/prompts:mobilekit-build` | no — `description` and `argument-hint` are ignored |
| Skills (`~/.codex/skills/`) | `$mobilekit-build` | yes — `name`, `description`, `metadata.short-description` |

`commands/` targets the first surface, so in Codex those entries appear without their
descriptions. This directory targets the second: Codex walks a skill directory and treats
every nested `SKILL.md` as its own skill, so `codex/build/SKILL.md` becomes `$mobilekit-build`
with its description in the picker.

The walk is implementation behaviour, not documented contract — the source (`ext/skills`
loader, recursive up to six levels) and Codex 0.142.5 confirm it, while the official skill
docs describe only one `SKILL.md` per skill folder. If a Codex update drops the recursion,
the symptom is these eight vanishing from the `$` picker; nothing else breaks.

## Why this cannot be one file

Both hosts read a `name:` key, and they demand different values for it.

Codex requires `name:` in a nested `SKILL.md` — without it the skill is dropped silently, not
even reported as an error — and the value is the whole invocation, flat across every skill
installed. So it has to be `mobilekit-build`; a bare `build` would collide with anything else
named `build`.

Claude Code also honours `name:`, but as a *replacement for the last segment* of a command that
is already namespaced by its directory. `name: mobilekit-build` under `commands/mobilekit/`
produces `/mobilekit:mobilekit-build`. The value it wants is a bare `build`.

One key, two required values. Hence two files. `install.sh --check` verifies the two sets stay
in step; it cannot verify that their descriptions still say the same thing.

## What the frontmatter carries

Two constraints shape the files here:

- **`argument-hint` does not exist in Codex.** It is accepted and discarded. The hint is folded
  into `description` instead ("Argument is the topic — for example auth, offline, payments").
- **`description` is the triggering mechanism**, not just a label — Codex matches user intent
  against it. Each one names both what the phase does and when it applies.
- **Skills get no template substitution.** `$ARGUMENTS`, `$1` and `{{…}}` are prompt-only —
  Codex's own command-to-skill migrator flags them as unsupported. The text typed after
  `$mobilekit-build` reaches the model as part of the message, so the files that take an
  argument say so in prose instead.

Each file is a pointer to the matching `workflow/` phase, the same way `commands/` is. The
phase files stay the single source of truth; nothing about the workflow is duplicated here.

Adding a command means adding it in both places — `commands/<name>.md` for Claude Code and
`codex/<name>/SKILL.md` here.

## Other hosts

`install.sh` symlinks the whole repo into Cursor's and Antigravity's skill directories too.
A host that recurses the way Codex does would surface these eight as extra skills there —
untested on both. Claude Code does not recurse and never sees this directory.
