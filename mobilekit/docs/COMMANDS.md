# Command reference

Eight commands, one per phase of the workflow. Each is a thin alias for a file in [`workflow/`](../workflow/) — an agent with no slash-command support reads that file directly and behaves identically.

Invocation differs by host: `/mobilekit:next` in Claude Code, `/mobilekit-next` in Codex, and "run the mobilekit next phase" in anything else. This page uses the Claude Code form.

New to the workflow? [TUTORIALS.md](TUTORIALS.md) has six walkthroughs by starting point; this page is the reference.

**Reading order if you are new:** [`init`](#mobilekitinit) → [`discovery`](#mobilekitdiscovery) → [`design`](#mobilekitdesign) → [`plan`](#mobilekitplan) → [`next`](#mobilekitnext) until the plan is empty → [`ship`](#mobilekitship).

---

## The state machine

There is no database and no config file. **Three documents in the project's `docs/` are the state**, and every command reads them to decide whether it can run:

| Document | Written by | Its absence means |
|---|---|---|
| `docs/PRODUCT.md` | `discovery` | Nothing else may run |
| `docs/DESIGN.md` | `design` | Screen work is guesswork |
| `docs/BUILD-PLAN.md` | `plan` | There is no "next step" to run |

A fourth, `docs/DOMAIN.md`, is written during the build by the `domain-model` prompt. A legacy app also gets `docs/MODERNIZATION.md`, and a project running the optional `market-signal` prompt keeps its launch log in `docs/LAUNCHES.md` — neither gates anything.

This is deliberate: the documents are readable by a person who has never heard of this tool, and they are diffable in review. A command that cannot find its prerequisite says so and names the command that produces it, rather than filling the gap with a plausible guess.

---

## `/mobilekit:init`

Prepares a project. Run once, in the project root.

**Reads** `package.json`, the existing `AGENTS.md` or `CLAUDE.md`, the folder layout, and `docs/`.
**Writes** `AGENTS.md`.
**Copies nothing** — the prompt library stays in the skill and is read from there, so a fix to a prompt reaches every project at once.

It routes before it writes:

- No `expo` dependency → asks whether to scaffold, whether this is a legacy app, or whether you are in the wrong directory.
- An app that already ships → routes you to `legacy-modernization`, because an interview cannot tell you what a live app does. The code can.
- An existing `AGENTS.md` → extends it. Yours is not replaced.

Without `docs/PRODUCT.md` it writes only what is true regardless of the product — the stack from `package.json`, the layout as actually found, conventions read from existing code — and marks the product sections `TBD`.

```
/mobilekit:init
```

---

## `/mobilekit:discovery`

The product interview. This is the command that makes every later prompt possible, and the one people are most tempted to skip.

**Prerequisite** none.
**Writes** `docs/PRODUCT.md`, and nothing else. No code, no dependencies.

Seven blocks: the product and its user, **the central object** (the single most valuable block — it is what replaces `Item` with `Lesson` everywhere in your codebase), the core journey, data and backend, identity, capabilities marked now/later/never, and constraints.

What it will not do:

- **Infer your domain.** Not from the folder name, not from a scaffold, not from a repo cloned off a tutorial. That is exactly the situation where an agent invents a plausible product and builds it.
- **Fill a gap.** An unresolved answer is written down as `UNDECIDED — ask before assuming`, and every later prompt stops on it.
- **Dump the questionnaire.** One question per message, each with a recommended default, so your answer can be "yes" instead of an essay.

Running it a second time asks whether you are revising specific sections or starting over; a document you filled in by hand is never silently overwritten.

```
/mobilekit:discovery
```

---

## `/mobilekit:design`

Decides which screens exist, how you move between them, and what each one shows when it has nothing to show.

**Prerequisite** `docs/PRODUCT.md`.
**Writes** `docs/DESIGN.md`.

Three steps, and the second only starts once the first has recorded a visual direction:

1. **Structure** — the screen inventory, where every screen traces to a journey step or a capability marked "now" (a screen that traces to neither is dropped, and you are told why); the navigation shape; which screens are modals; where the app opens on cold start for a new, a signed-in and a signed-out user; and **four states per core screen** — empty, loading, error, populated. Most bugs reported as "the app is broken" are one of those four missing.
2. **Visual system** — tokens for colour, type, spacing, radius, elevation. If you have a Figma export or screenshots, it asks for them first. If you do not, it proposes directions and **you choose the palette**. It will not pick one for your product.
3. **Identity assets** — icon, adaptive icon, splash. A placeholder shipped to a store is a rejected build, so the gap is recorded rather than discovered later.

Pass an argument to run one step only: `/mobilekit:design screens`.

```
/mobilekit:design
/mobilekit:design tokens
```

---

## `/mobilekit:plan`

Cuts 59 prompts down to the ones your app actually needs, in order.

**Prerequisite** `docs/PRODUCT.md`. `docs/DESIGN.md` strongly preferred — without it, screen steps are guesses.
**Writes** `docs/BUILD-PLAN.md`, a checklist of unchecked boxes.

How the cut is made:

- Every step whose capability `PRODUCT.md` marks "later" or "never" is removed, and appears in a **Skipped** table with the reason. No payments step for an app with no payments.
- Generic screen steps are replaced by your real screens from `DESIGN.md`, core screens first.
- Mutually exclusive prompts are decided with a one-line reason: managed auth or your own, a managed backend or an existing API; store billing, a payment gateway or ads follow `PRODUCT.md`'s Monetization section.
- Steps a store submission requires stay in whatever the product is — permissions, consent, accessibility, compliance.
- **The repo is read.** Anything already done is marked done, not queued.

One box is one prompt file, always. Two prompts never share a box, because `next` runs one at a time on purpose.

```
/mobilekit:plan
```

---

## `/mobilekit:next`

Runs the first unchecked box. This is the command you spend the build in.

**Prerequisite** `docs/BUILD-PLAN.md`.
**Writes** code, and ticks one box.

The loop, per step:

1. Announces which step and which prompt file, and gives you a chance to skip it before anything starts.
2. Reads `RULES.md`, `PRODUCT.md`, `DESIGN.md`, `AGENTS.md`, then the prompt.
3. Works the prompt's `Grill` block **one question at a time**, recommending an answer to each.
4. Resolves the installed version of anything it configures, and gets that version's documentation — from a docs tool if it has one, from you if it does not.
5. Builds.
6. Walks the `Done when` checklist and reports each item met, not met, or **not verifiable** — the third one matters, because "I could not test this on a device" is information.
7. Ticks the box only if the checklist passed. Partially done stays unchecked with a note.

**When it blocks** — a missing account, an `UNDECIDED`, a credential it must not create — it stops and says exactly what it needs from you. It does not substitute a placeholder and tick the box; a bug shipped with a tick beside it is worse than an unfinished step.

```
/mobilekit:next
```

---

## `/mobilekit:build <topic>`

Runs one prompt out of order. The escape hatch for existing projects and one-off additions.

**Prerequisite** none, but it tells you what is missing before it starts.

Resolution: a filename matches directly, a word matches by subject. Ambiguity is a question — "auth" maps to three prompts, so it lists them and asks. A topic with no match lists the nearest three rather than improvising a prompt that does not exist.

Prerequisites it will name rather than silently work around:

| Topic | What it will tell you first |
|---|---|
| Anything with a secret — AI, payments, realtime | `secure-backend` has not run |
| Camera, photos, mic, location, notifications | `native-permissions` has not run |
| Analytics or error tracking, shipping to the EU or Brazil | `privacy-consent` gates it |
| `post-release` | Needs real users; thresholds invented before data are noise |
| Any screen, with no `DESIGN.md` | The screen's states are undefined — it asks for them inline |

```
/mobilekit:build auth
/mobilekit:build media-upload
/mobilekit:build legacy
```

---

## `/mobilekit:ship`

The release gate. A gate, not a step: it runs several prompts in a fixed order, because each one finds problems that are cheaper before submission than after.

**Prerequisite** an app that builds.

Order, and why it is this order:

1. `testing` — risk-driven scope. Not optional for money or auth.
2. `accessibility` — store review rejects on this; users leave over it.
3. `performance` — measured on a low-end device, the only device whose numbers matter.
4. `security-review` — re-test every ticked security check, the joints between features, storage, logs.
5. `error-tracking` — shipping without it makes the first production crash invisible.
6. `privacy-consent` — if any analytics ships to the EU or Brazil.
7. `store-compliance` — privacy manifest, data-safety declarations, reviewer account, listing. This is what rejects builds.
8. `eas-build` — profiles, environment variables, submission.
9. `beta-and-review` — testers before the public, review notes, and the rejection loop a first submission usually meets.

Plus three checks that belong to the gate rather than to any prompt:

- **The toolchain check.** The Expo project doctor. A dependency mismatch it catches in one command is a crash someone else finds in production.
- **The secret leak sweep.** `git ls-files` for anything credential-shaped, `.gitignore` confirmed, then a real build grepped for each known secret value. A committed secret is not fixed by deleting the file — it is in history, and the key has to be rotated.
- **A physical device.** A simulator build proves nothing about fonts, shadows, permissions or push. If a preview build never ran on real hardware, the report says so.

A skipped step is reported as skipped, never as passed.

```
/mobilekit:ship
```

---

## `/mobilekit:status`

Where the project is. Read-only; changes nothing.

**Its most useful output is drift** — where the plan and the repo disagree. A checked box with no dependency installed is a lie in a file, and this is what finds it. It reports which side is wrong and leaves the correction to you.

```
Phase:      build
PRODUCT.md  ok · 2 UNDECIDED
DESIGN.md   missing
BUILD-PLAN  7/24 · next: tab-navigation
Drift:      plan says zustand done, zustand not in package.json
Next:       design
```

```
/mobilekit:status
```

---

## Two entry points

**A new app** starts at `discovery`. There is no product yet, so it gets interviewed into existence.

**An app that already ships** starts at `prompts/9-maintain/legacy-modernization.md`, reachable with `/mobilekit:build legacy`. A live app has a domain, users, and constraints that outrank any interview, so discovery is replaced by inventory: what the code does, what the store listing claims, which dependencies are unmaintained, what feature parity actually consists of. It produces `docs/MODERNIZATION.md` and derives `docs/PRODUCT.md` from what it found — asking only about the gaps. From that point the normal flow works: design derives screens from the app that ships, and plan takes `MODERNIZATION.md`'s sequence as the spine of `BUILD-PLAN.md`.

It covers four starting points: React Native bare or ejected and several versions behind, Expo several SDKs behind, a hybrid Cordova/Ionic/WebView app, and native Swift/Kotlin adopting React Native incrementally.

---

## Working without slash commands

The commands carry no logic. Each one says "run `workflow/<phase>.md`", and that file is the phase. So in any agent:

> Read `workflow/ship.md` in the mobilekit skill and follow it.

Or point the agent at `AGENTS.md` in the skill directory and describe what you want in words — "we're ready to submit this to the App Store" reaches the same file. The slash command is a keystroke saver, not the mechanism.
