---
name: mobilekit
description: Guided end-to-end workflow for building and modernizing React Native / Expo mobile apps — product discovery, design conception, implementation, store release, and post-release observability. Use when starting a mobile app, deciding what to build next in an Expo project, modernizing a legacy or hybrid mobile app, adding one capability to an existing app (auth, payments, push, offline, AI, store release…), or on any /mobilekit command.
license: MIT
metadata:
  short-description: Build or modernize a React Native / Expo app
  version: 2.5.0
  tags: [react-native, expo, mobile, ios, android, product-discovery, app-store]
---

# mobilekit

A phase-driven workflow over a prompt library. Everything needed to run it lives in this skill: `workflow/` holds one file per phase, `prompts/` holds the library those phases execute.

The value over reading the files directly is that it knows **where the project is** and refuses steps whose prerequisites are missing.

## Read first, always

1. **`prompts/RULES.md`** — how prompts are run: grill one question at a time, look facts up, request documentation, invent nothing, report honestly. It is the single source of truth; nothing here restates it.
2. **`docs/PRODUCT.md`** in the target project — it gates everything. Absent → the answer to almost any request is "run discovery first".

## The phases

Each is a file in `workflow/`. Read the one you are running; skip the rest.

| Phase | File | Produces |
|---|---|---|
| Install into a project | [`workflow/init.md`](workflow/init.md) | `AGENTS.md`, `docs/` |
| Product discovery | [`workflow/discovery.md`](workflow/discovery.md) | `docs/PRODUCT.md` |
| Design conception | [`workflow/design.md`](workflow/design.md) | `docs/DESIGN.md` |
| Cut the plan | [`workflow/plan.md`](workflow/plan.md) | `docs/BUILD-PLAN.md` |
| Run the next step | [`workflow/next.md`](workflow/next.md) | ticks a box |
| Run one step out of order | [`workflow/build.md`](workflow/build.md) | — |
| Release gate | [`workflow/ship.md`](workflow/ship.md) | a submitted build |
| Where the project is | [`workflow/status.md`](workflow/status.md) | nothing |
| Watch production | [`prompts/8-observability/post-release.md`](prompts/8-observability/post-release.md) | the four numbers |
| Modernize an existing app | [`prompts/9-maintain/legacy-modernization.md`](prompts/9-maintain/legacy-modernization.md) | `docs/MODERNIZATION.md` |
| Market contact per phase (optional) | [`prompts/1-discovery/market-signal.md`](prompts/1-discovery/market-signal.md) | `docs/LAUNCHES.md` |
| Decide the next cycle after release | [`prompts/8-observability/next-feature.md`](prompts/8-observability/next-feature.md) | appends to `docs/BUILD-PLAN.md` |

Slash commands, where the host has them, are thin aliases: `/mobilekit:next` → `workflow/next.md`. Where it has none, read the phase file directly — that is the whole mechanism.

**A legacy app enters through modernization, not discovery.** An app that already ships has a domain; the job is to inventory it and choose a migration path, then join the normal flow.

## State

The presence of three documents *is* the phase. Never guess at a missing one.

| File | Written by | Means |
|---|---|---|
| `docs/PRODUCT.md` | discovery | The product is defined. Nothing else runs before this exists. |
| `docs/DESIGN.md` | design | Screens, navigation and per-screen states are decided. |
| `docs/BUILD-PLAN.md` | plan | The ordered checklist of only the steps this app needs. The progress tracker. |

## Executing a prompt

Prompts share a shape: a header saying when it applies, a `## Prompt` section, a `### Grill` block holding the developer's decisions, and a `### Done when` checklist. The ones that produce a document rather than code — `product-discovery.md`, `monetization.md` and `design-conception.md` — carry an `## Output` structure in place of the checklist, and are a grill from end to end.

1. Read `prompts/RULES.md`, `docs/PRODUCT.md`, `docs/DESIGN.md` (if present) and the project's `AGENTS.md`.
2. Read the prompt and follow its `## Prompt` section **as written** — it is the instruction, not a summary to paraphrase.
3. Work its `### Grill` block one question at a time, recommending an answer to each. Look facts up; put decisions to the developer.
4. Build.
5. Walk `Done when` and report each item met, not met, or not verifiable.
6. If `docs/BUILD-PLAN.md` exists, mark that step done in it.

## Finding a prompt

`prompts/` is organized by phase: the numbered folders are the phase order, filenames are the ids. The index — every prompt with its description — and the reference build order live in [`prompts/README.md`](prompts/README.md).

## Where the library is read from

Prompts are read from this skill, wherever it is installed. `workflow/init.md` writes documents into the project and copies nothing — a correction to a prompt reaches every project at once. A project needing its own rules writes `docs/mobilekit-overrides.md`, read after `prompts/RULES.md` and winning on conflict.
