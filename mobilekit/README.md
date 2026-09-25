<div align="center">

# mobilekit

**A phase-driven workflow for building React Native / Expo apps with an AI coding agent — from "I have an idea" to "I know what broke in production".**

59 prompts · 8 phases · 8 commands · works with Claude Code, Codex, Antigravity, Cursor, and anything that reads `AGENTS.md`

[Install](#install) · [How to use it](#how-to-use-it) · [Tutorials](docs/TUTORIALS.md) · [Command reference](docs/COMMANDS.md) · [Prompt library](prompts/README.md) · [Contributing](CONTRIBUTING.md)

</div>

---

## Why this exists

An agent asked to "build a mobile app" produces a plausible app for a product nobody described. It infers the domain from the folder name, picks your auth provider silently, pastes setup steps from a version that shipped two years ago, and reports done on a screen that has never been opened without data in it.

mobilekit is the correction. It is not a template and it generates no boilerplate. It is a sequence of prompts, each one a checklist of the concerns that actually break mobile apps, wrapped in a workflow that **knows where your project is and refuses the steps whose prerequisites are missing**.

Four rules do most of the work:

|  |  |
|---|---|
| **Nothing runs before `PRODUCT.md`** | A repo scaffolded from a tutorial tells an agent nothing about the product being built — and that is exactly when agents confidently invent a domain. |
| **`UNDECIDED` is a value** | Discovery records what you did not answer instead of filling it with a plausible guess. Later prompts stop on it. |
| **Options are questions** | Where a prompt lists A / B / C, the agent recommends one and waits. It does not choose your auth provider or your palette. |
| **Documentation is an input, not a memory** | Before writing setup code, the agent reads the installed version, then gets *that version's* docs — from a docs tool if it has one, from you if it does not. Setup pasted from memory is the most common failure in agent-built mobile apps. |

---

## Install

### With the skills CLI (recommended)

```bash
npx skills add antrafa/skill-mobilekit
```

Detects the agents you have installed and links the skill into each. Nothing else is needed — the workflow, the phase files and the prompt library all travel with the skill.

### With the bundled script

Gives you the slash commands as well, for hosts that support them.

```bash
git clone https://github.com/antrafa/skill-mobilekit.git ~/.agents/skills/mobilekit
~/.agents/skills/mobilekit/install.sh
```

Idempotent, symlinks only. It copies nothing, overwrites no config, and refuses to clobber anything that is not its own — run `install.sh --check` to see what it would do.

### Manually

Clone anywhere and point your agent at the directory. `AGENTS.md` in the repo root is the entry point.

### What gets wired where

| Agent | Skill | Commands |
|---|---|---|
| **Claude Code** | `~/.claude/skills/mobilekit` | `~/.claude/commands/mobilekit/` → `/mobilekit:next` |
| **Codex** | `~/.codex/skills/mobilekit` | `~/.codex/prompts/mobilekit-*.md` → `/mobilekit-next` |
| **Antigravity** | `~/.gemini/config/skills/mobilekit` | — reads `SKILL.md` |
| **Cursor** | `~/.cursor/skills/mobilekit` | — reads `SKILL.md` |
| **Anything else** | any path | — reads `AGENTS.md` |

For an agent with its own command directory:

```bash
./install.sh --commands-dir ~/.config/<agent>/prompts --prefix mobilekit-
```

**Slash commands are optional.** Each one is a three-line alias for a file in `workflow/`; an agent with no command support reads that file directly and behaves identically. Nothing is lost.

---

## How to use it

Three things are all there is to know: the flow is a fixed spine of commands, you can join it at three different points, and two commands are safe at any moment — `status` says where you are, `build` runs one thing out of order.

### The whole flow, one example

A new app, from an empty folder to a monitored release:

```
cd my-app                        # 1. a folder, git init'd
/mobilekit:init                  # 2. inspects the repo, writes AGENTS.md
/mobilekit:discovery             # 3. the product interview → docs/PRODUCT.md
/mobilekit:design                # 4. screens, navigation, states → docs/DESIGN.md
/mobilekit:plan                  # 5. cuts 59 prompts to your checklist → docs/BUILD-PLAN.md
/mobilekit:next                  # 6. runs the first unchecked step — repeat until the plan is empty
/mobilekit:ship                  # 7. the release gate: tests, a11y, compliance, build, beta, submission
/mobilekit:build post-release    # 8. once real users are in: the four numbers you watch
/mobilekit:build next-feature    # 9. plan empty, data in: the numbers pick the next cycle → back to 6
```

Steps 2–5 produce documents and no code; the build happens inside step 6, one checklist box per run. Discovery is the ten to twenty minutes that decide whether everything after it is worth anything — one question at a time, each with a recommended default, so most answers are a confirmation.

And there is no "finish": after the first release the loop is 6 → 7 → 8 → 9, plus `/mobilekit:build sdk-upgrade` every Expo SDK cycle.

### Where to start

| Your situation | Start with | What happens |
|---|---|---|
| An idea, no code | `/mobilekit:init` → `discovery` | The interview defines the product before anything is scaffolded |
| A half-built Expo project, never shipped | `/mobilekit:init`, then the flow above | Discovery and design read what exists; `plan` marks what is already done as done instead of queueing it |
| An app already in the stores | `/mobilekit:build legacy` | Inventory replaces the interview: `docs/MODERNIZATION.md` is written, `PRODUCT.md` derived from the code and the store listing, and the flow continues from `design` — with the migration sequence as the plan's spine |

Joining works in one direction only: you can enter late with an existing codebase, but you cannot skip a document forward — every command checks its prerequisites and refuses with the name of the command that produces what is missing. That refusal is the navigation.

**When in doubt, run `/mobilekit:status`.** It reads the documents, says which phase the project is in, reports where the plan disagrees with the repo, and names the next command. It changes nothing, so it is never the wrong move.

Six walkthroughs with worked examples, by starting point, are in **[docs/TUTORIALS.md](docs/TUTORIALS.md)**.

### Every command

**The spine — run in this order, each once (`next` repeats):**

| Command | Run when | Needs | Writes |
|---|---|---|---|
| [`init`](docs/COMMANDS.md#mobilekitinit) | Once, first, in the project root | — | `AGENTS.md` |
| [`discovery`](docs/COMMANDS.md#mobilekitdiscovery) | Right after init, before any code | — | `docs/PRODUCT.md` |
| [`design`](docs/COMMANDS.md#mobilekitdesign) | After discovery, before any screen | `PRODUCT.md` | `docs/DESIGN.md` |
| [`plan`](docs/COMMANDS.md#mobilekitplan) | After design | `PRODUCT.md` (+ `DESIGN.md`) | `docs/BUILD-PLAN.md` |
| [`next`](docs/COMMANDS.md#mobilekitnext) | Repeatedly, until the plan is empty | `BUILD-PLAN.md` | code, one ticked box per run |
| [`ship`](docs/COMMANDS.md#mobilekitship) | Plan done, release intended | an app that builds | a submitted build |

**Any time, out of order — these never break the flow:**

| Command | What for |
|---|---|
| [`status`](docs/COMMANDS.md#mobilekitstatus) | Where am I, what drifted, what runs next. Read-only. |
| [`build <topic>`](docs/COMMANDS.md#mobilekitbuild-topic) | One prompt out of order — `build auth`, `build offline`, `build media-upload`… It names missing prerequisites instead of silently working around them. |

`build` is also how you reach everything that has no command of its own: `build legacy` (the third entry point above), `build post-release` and `build next-feature` (the after-release loop), `build market-signal` (optional: the product in front of real people at each phase boundary), `build sdk-upgrade`.

---

## The workflow

```
┌─ 1-discovery ────── what are we building         → docs/PRODUCT.md
├─ 2-design ───────── screens, navigation, states  → docs/DESIGN.md
├─ 3-foundation ───── Expo, styling, domain model, shared components
├─ 4-platform ─────── auth, permissions, APIs, database, state, server-side secrets
├─ 5-screens ──────── the app itself
├─ 6-features ─────── push, media, moderation, payments, AI, i18n, offline, links
├─ 7-ship ─────────── testing, a11y, performance, store compliance, CI, EAS build
├─ 8-observability ── consent, analytics, error tracking, what you watch, rollback
└─ 9-maintain ─────── legacy modernization, SDK upgrades
```

Full command reference, with what each one reads, refuses and produces: **[docs/COMMANDS.md](docs/COMMANDS.md)**.
Walkthroughs with worked examples, by starting point: **[docs/TUTORIALS.md](docs/TUTORIALS.md)**.

### State lives in documents, not in a database

Three markdown files in the project's `docs/` **are** the state. Every command reads them to decide whether it can run, and a missing one produces a refusal that names the command that writes it.

That is deliberate: the documents are readable by a person who has never heard of this tool, they are reviewable in a pull request, and they are yours. `PRODUCT.md` is the product definition, not a cache.

---

## What it covers

Expo · React Native · TypeScript · Expo Router · NativeWind · Zustand · Clerk / Supabase / custom auth · OpenAPI, REST and GraphQL clients · TanStack Query · PostHog · Sentry · Expo Notifications · Reanimated · RevenueCat · Stripe · Expo API Routes for anything holding a secret · provider-agnostic AI, always proxied server-side · EAS Build and EAS Update.

Cross-cutting concerns each with their own prompt: native permissions, media capture and upload, content moderation, i18n, offline, deep linking, biometrics, account recovery, testing, performance, accessibility, privacy consent, store compliance, CI/CD, release rollback, post-release observability and SDK upgrades.

The full index with a description per prompt: **[prompts/README.md](prompts/README.md)**.

### What it does not cover

The library is opinionated about a segment — content, productivity and SaaS-style apps. It has no prompts for maps and geofencing, Bluetooth, health platforms, media streaming, cart-based commerce, widgets and Live Activities, or advertising SDKs. Those verticals need prompts of their own, and [CONTRIBUTING.md](CONTRIBUTING.md) has the shape to write them in.

It is also not a legal or a security review. `store-compliance.md` and `privacy-consent.md` cover the engineering; the legal question belongs to your counsel.

---

## Design decisions worth knowing

**Filenames are the ids.** `domain-model.md` keeps that name wherever it moves. `BUILD-PLAN.md` entries and the cross-references between prompts are filenames, so a prompt can be reorganized without breaking either. Folder numbers are phase order and can be rearranged freely.

**`prompts/RULES.md` is the single source of truth.** Grill one question at a time, look facts up, request documentation, invent nothing, keep secrets server-side, report honestly. `SKILL.md` and `AGENTS.md` point at it rather than restating it, because a copied rule is a rule that drifts.

**Nothing is copied into your project.** The library is read from the skill, so a fix reaches every project at once. A project that needs its own rules writes `docs/mobilekit-overrides.md`, read after `RULES.md` and winning on conflict.

**`Done when` is verifiable or it is not there.** "Grep the built bundle for each secret value." "Read another user's row and be denied." "Airplane mode: cached screens render, uncached ones explain themselves." A checklist item you cannot run is a checklist item that gets ticked out of optimism.

**The report distinguishes three outcomes**, not two: met, not met, and *not verifiable*. "I could not test this on a device" is information, and hiding it inside a tick is how a broken build reaches a store.

---

## Contributing

Prompts are the product. Adding one, or a whole vertical, is the most useful contribution — the required shape, voice and checklist standard are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
