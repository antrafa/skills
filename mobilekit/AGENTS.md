# mobilekit

Cross-agent entry point. Claude Code loads `SKILL.md`; Codex, Antigravity, Cursor, Zed and anything else following the `AGENTS.md` convention land here.

## If you are using mobilekit to build an app

**Read [`SKILL.md`](./SKILL.md) now.** It holds the phase map, the state model, and the procedure for executing a prompt. Then read [`prompts/RULES.md`](./prompts/RULES.md) — the single source of truth for how prompts are run. Everything below is a map, not a substitute.

The phases are files in [`workflow/`](./workflow/), one per phase — read the one you are running. The library they execute is [`prompts/`](./prompts/README.md).

```
1-discovery      what are we building        → docs/PRODUCT.md
2-design         screens, navigation, states → docs/DESIGN.md
3-foundation     Expo, NativeWind, domain model, shared components
4-platform       auth, permissions, APIs, database, state, server-side secrets
5-screens        the app itself
6-features       push, media, moderation, payments, AI, i18n, offline, deep linking
7-ship           testing, a11y, performance, store compliance, CI, EAS build
8-observability  consent, analytics, error tracking, what you watch, how you roll back
9-maintain       legacy modernization, SDK upgrades
```

Slash commands in [`commands/`](./commands/) are thin aliases for the phase files, for hosts that support them. Codex reads a second set of the same aliases from [`codex/`](./codex/README.md), because it discovers commands as nested skills rather than as prompt files. Without either, read the phase file directly — that is the whole mechanism, and nothing is lost.

Two things hold regardless of which agent you are:

1. **`docs/PRODUCT.md` gates everything.** Absent → run discovery. An app that already ships runs [`prompts/9-maintain/legacy-modernization.md`](./prompts/9-maintain/legacy-modernization.md) instead.
2. **Everything else you need is in [`prompts/RULES.md`](./prompts/RULES.md)** — grill one question at a time, look facts up, request documentation you do not have, invent nothing, keep secrets server-side, report honestly. It is not restated here; a copy would drift.

## If you are working on mobilekit itself

This repo is the skill, not an app built with it. See [CONTRIBUTING.md](./CONTRIBUTING.md).

- `prompts/RULES.md` is the single source of truth for prompt behaviour; `SKILL.md` owns the phase model. Everything else points at them.
- **Filenames in `prompts/` are the ids.** A prompt keeps its name wherever it moves; `BUILD-PLAN.md` entries and the cross-references between prompts depend on it.
- Folder numbers (`1-discovery`) are phase order and may be reorganized; `prompts/README.md`, `SKILL.md` and the `workflow/` files carry links to fix — `grep -rl 'prompts/' workflow/ SKILL.md AGENTS.md prompts/README.md` finds them all.
- A new prompt goes in the folder matching its phase and gets a row in `prompts/README.md`.
- A new command is written twice: `commands/<name>.md` for Claude Code, `codex/<name>/SKILL.md` for Codex. Both hosts read a `name:` key and want different values in it, so one file cannot serve both — [`codex/README.md`](./codex/README.md) has the detail. `install.sh --check` fails when one side is missing a command the other has.
