# Quickstart — your first 30 minutes

For someone who has just installed the skill and wants proof it does something before spending an afternoon on it. It runs the loop once — `init`, `discovery`, `design`, `plan`, one `next` — and stops at the first green step. Not a finished app.

The example is **Feira**, a shared shopping list for a household: the domain needs no explanation, and its nouns are obviously not `Item` — List, Entry, Member, Aisle. The full path, with accounts, a backend, push and a store submission, is [`new-app.md`](new-app.md).

---

## Before you start

| | Why |
|---|---|
| 30 minutes, uninterrupted | Two of the five commands are conversation. Answering them while distracted produces a plausible product definition, which is worse than none. |
| A phone with Expo Go, or a simulator | `nativewind`'s checklist says a `className`-styled component renders **on a device — not just in web**. Web only, and that item comes back "not verifiable" and the box stays unticked. |
| A browser tab you can copy from | If your agent has no docs tool it will ask you for the install guide of the major in your `package.json`. That request is the most common thing that stalls this path, and it takes a minute to satisfy if you are ready for it. |
| Nothing else | No Apple or Google account, no auth provider, no database, no paid anything. This path deliberately touches none of it. |

Five commands: `init` (2 min) · `discovery` (12) · `design screens` (8) · `plan` (2) · `next` (6). Three markdown files come out — `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/BUILD-PLAN.md`. They are the entire state of the workflow: no database, no config file, diffable in review.

---

## Phase 0 — `init`

```bash
mkdir feira && cd feira && git init
```
```
/mobilekit:init
```

It reads `package.json`, finds no `expo` dependency, and asks the only question it can ask: scaffold, is this a legacy app to modernize, or are you in the wrong directory. Confirm scaffold — that routes through `expo-setup`, which grills you on app name, slug, bundle identifiers, deep-link scheme, target platforms, and whether source sits under `src/` or at the root. That last one is recorded, and every later prompt reads it from the repo rather than assuming. It then writes `AGENTS.md` with only what is true regardless of the product, marking the product sections `TBD — run discovery` rather than inventing a domain to fill them. Nothing from the skill is copied into your repo — the prompt library is read from where it lives, so a fix to a prompt reaches every project at once.

## Phase 1 — `discovery`

```
/mobilekit:discovery
```

Seven blocks, one question per message, each with a recommended default so most answers are a confirmation. Block B is the block that pays for the session.

> **What is the one thing this app is mostly about?**
> Default: I cannot infer this — a shopping list has at least two candidates, the list itself and the thing written on it. Which one does a user open the app to interact with?
>
> — The List. You open it standing in the shop.
>
> **What is the real vocabulary? The 3–7 nouns you would use talking to a colleague, and how they relate.**
>
> — A List has many Entries. A Member belongs to a List. An Entry sits in an Aisle, so the shop order makes sense.

Those four nouns are now the code's vocabulary, recorded verbatim. Nothing downstream says `Item`.

Then Block D, where this path gets cheap:

> **Does the data already live somewhere?**
> Recommended: **D — no backend yet, ship local content first**. Nothing in the journey you described needs a second device today, and a schema is the most expensive thing to get wrong early. Confirm or change.

Confirm. That single answer is why the rest of the run is short. Scenario D sends `domain-model` down its local-content branch: types in `types/`, typed fixtures in `data/`, access through the same `getX()` / `getXById()` shapes a real backend would use, and **the swap point written into `docs/DOMAIN.md`** — which files change when a backend arrives and which do not. No migration, no row-level policy, no credentials. It is the cheapest honest start available, and it is not a dead end, because the swap is recorded rather than remembered.

Block F, capabilities, each now / later / never:

| | Feira's answer | Consequence |
|---|---|---|
| Payments, AI, media upload, deep links | never | No dependency installed, no prompt run |
| Push | later | Nothing would trigger one until Lists sync across devices |
| Analytics / errors | analytics never, errors later | Both out; `privacy-consent` has nothing left to gate |
| i18n, dark mode | later | Out of the plan |

Accounts (Block E): **no**. Members are names typed on the device. That removes four more prompts.

### The one decision worth watching

Question 15 asks whether the app needs to work offline. Yes — shops have no signal. The answer is trivially true today, because the data is local. But "shared" is in the first sentence of the product, so the agent asks one follow-up:

> When this List is genuinely shared, two Members will both edit it while disconnected and reconnect with different versions. What wins?
>
> — I have not thought about it.
>
> Then I am recording it as undecided rather than picking one. Last-write-wins is a decision with data loss attached, not a default.

Into `PRODUCT.md`'s `## Open questions` goes, verbatim: `Merge rule when two Members edit one List offline — UNDECIDED — ask before assuming`.

The skill will not resolve this now and will not resolve it later either — the `offline` prompt's grill exists to ask it, per entity if necessary, and until it is answered any step depending on it stops. An agent that had quietly chosen last-write-wins would have handed you a working app that silently eats somebody's groceries. What comes out of the phase is `docs/PRODUCT.md`, under 100 lines, read before every later task.

## Phase 2 — `design screens`

```
/mobilekit:design screens
```

The argument runs step 1 only. The visual-system step needs a palette decision the agent will not make for you, and this run does not need tokens to prove anything — `design-system` stays in the plan as its own step. Every screen must trace to a core-journey step or a capability marked "now". Feira came out at three core screens: **Lists**, **List** (Entries grouped by Aisle), **Add an Entry**. A Members screen was dropped — nothing in the journey reaches it while there are no accounts — and the reason is written down.

Then navigation, where it recommends **single stack** — tabs are for 3–5 destinations a user switches between freely, and you have one job. Confirm and `tab-navigation` never enters the plan. An option offered is a question, not a decision already taken.

Then the four states, per core screen. For the **List** screen:

| State | Decision |
|---|---|
| Empty | "Nothing on this list yet." One action: *Add the first Entry*. |
| Loading | No spinner — local data is already there on first paint |
| Error | Nothing can fail today. Recorded anyway: retry, existing Entries stay visible |
| Populated | Unticked Entries grouped by Aisle, ticked ones collapsed at the bottom |

The loading and error rows look like paperwork on a local-only app. They are the two states the backend swap would otherwise invent from scratch, and inventing them later means touching every screen.

## Phase 3 — `plan`

```
/mobilekit:plan
```

59 prompts in, this out:

```markdown
# Build Plan

## Foundation
- [x] expo-setup · scaffolded during init
- [ ] nativewind
- [ ] design-system
- [ ] domain-model
- [ ] ui-components

## Screens
- [ ] list-screen · Lists
- [ ] detail-screen · List — Entries by Aisle
- [ ] form-screens · Add an Entry (sheet)

## Release
- [ ] testing
- [ ] accessibility

## Skipped
| Step | Why |
|---|---|
| auth-clerk, auth-backend, account-recovery | PRODUCT.md: accounts = no |
| app-shell | Single stack, no auth, no boot gate to own yet — re-add when accounts or onboarding land |
| dev-environment | Expo Go carries this prototype — re-add with the first native dependency |
| supabase, api-integration, react-query | Data scenario D — no remote source to fetch from |
| monetization, in-app-purchases, payments, ads, ai-features, media-upload, secure-backend | PRODUCT.md: payments = never, and nothing here holds a secret |
| push-notifications, deep-linking | later — no trigger exists until Lists sync |
| analytics, error-tracking, privacy-consent | analytics = never, errors = later |
| i18n, dark-mode, animations | later · tab-navigation: shape is a single stack |
| offline | Local data is already offline. The merge rule is UNDECIDED in PRODUCT.md — decide it before a backend lands, not after |
| content-moderation | A List is visible only to Members typed into it. Re-add if Lists become shareable by link |
| security-review, store-compliance, eas-build, beta-and-review, ci-cd, release-rollback, post-release | PRODUCT.md: stage = prototype, no submission planned. Re-add before the first one |

```

**Ten boxes, and the plan is short because your answers were short.** That is the lesson of this phase: most of those skips are one line in `PRODUCT.md`, and each is a dependency not installed and a prompt not run. Read the two conditional rows — `offline` and `content-moderation` — carefully: they are skipped *with the condition that would un-skip them written down*. Make Lists shareable by link and both become wrong, and the plan says so instead of leaving you to remember six months later. One box is always one prompt file; two never share a box, because `next` runs one at a time on purpose.

## Phase 4 — one `next`

```
/mobilekit:next
```

It announces the step and the prompt file and offers you the chance to skip before anything starts. Say no. Then, on this path, it almost certainly stops:

> I need the NativeWind install guide for the major in your `package.json`. Paste it, give me a link I can fetch, or save it to `docs/vendor/nativewind@<major>.md`.

Satisfy it. Setup written from memory is the single most common failure in agent-built mobile apps — whether a `tailwind.config.js` is required at all, which directives the CSS entry needs, whether a Babel plugin is still involved: all of that moved between majors. Anything you save under `docs/vendor/` is read first on later runs, so the ask happens once.

Then it builds, and walks the prompt's own `Done when` checklist — each item **met**, **not met**, or **not verifiable**:

```
Step: nativewind · prompts/3-foundation/nativewind.md
  met   className renders on the device
  met   className type-checks in .tsx with no editor error
  met   no existing screen was modified
  met   followed the guide you supplied; the Babel step in the prompt
        no longer applies at this major — noted
Box ticked. Next unchecked step: design-system
```

That third outcome is what makes the report worth reading. Run this on web only and the first item comes back **not verifiable**, the box stays unticked, and you have a known unknown instead of a lie in a file.

Then `/mobilekit:status`:

```
Phase:      build
PRODUCT.md  ok · 1 UNDECIDED
DESIGN.md   ok · tokens not run
BUILD-PLAN  2/10 · next: design-system
Drift:      none
Next:       /mobilekit:next
```

**That is the loop.** You have seen it turn answers into a cut plan and a cut plan into one verified step. Everything after this is the same five commands with more of them.

---

## The ways a step stops on this path

| It says | Why | You |
|---|---|---|
| "No `expo` dependency — scaffold, legacy app, or wrong directory?" | `init` routes before it writes | Confirm scaffold |
| "I need the install guide for the installed major" | It will not write setup from memory, and has no docs tool | Paste it, or save it under `docs/vendor/` once |
| "`PRODUCT.md` says data scenario D — confirming before I proceed" | `domain-model` states the scenario back before choosing a branch | Confirm |
| "Here are the types and the fixture set. Approve before I write files." | Names and shapes are cheap now, expensive across ten screens | Read it. Check every name is one of yours |
| "Recommended: single stack. Confirm or change." | An option offered is a question | Confirm, or pick another |
| A checklist item comes back **not verifiable** | You had no device, or something was untestable | Fix the gap, or accept that the box stays unticked |

---

## The mistakes that cost the most on this path

**Answering discovery fast because it is "only a quickstart".** The plan above is short because the answers were specific, not because the app is small. Rush them and you get the same ten boxes with the wrong nouns inside them — the one thing this path cannot recover from cheaply, because `domain-model` and every screen after it are built on those nouns.

**Letting the merge rule get decided for you.** If you had answered "just do the usual" to the offline follow-up, the honest outcome is still `UNDECIDED`. Anywhere else — an agent without this rule — the usual is last-write-wins, and you find out when someone's Entries vanish.

**Picking data scenario A because it feels more real.** Scenario A means a schema, a migration with a rollback, and a row-level policy on anything per-user, none of which fits in 30 minutes. D gets you the same types and a recorded swap point.

**Ticking `nativewind` yourself after seeing it work in the browser.** The checklist item names a device on purpose. A box ticked without the check converts a known unknown into an unknown unknown, and the styling failure surfaces two screens later where it is much harder to attribute.

---

## Where to go next

- [`new-app.md`](new-app.md) — the same loop run to a monitored release: accounts, a backend, push, `ship`, and what `store-compliance` actually costs. This is your next read.
- [`existing-project.md`](existing-project.md) — adopting the skill in a repo that already has screens
- [`COMMANDS.md`](../COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../prompts/RULES.md`](../../prompts/RULES.md) — the rules every prompt inherits. Short, and worth reading yourself once. [`../prompts/README.md`](../../prompts/README.md) lists all 59 prompts and the reference order the plan cuts down from.
