# Building a complete app from scratch

The full path, from idea to a monitored release — what you type, what the agent does, and, more usefully, **where it stops and asks you**, because that is where the quality comes from.

The example throughout is **Sarau**, a book-club app. Small enough to follow, large enough to exercise most of the library: a hierarchical domain, accounts, offline reading, scheduled reminders, and a handful of capabilities deliberately marked "never" so you can watch the plan get cut.

Substitute your own app and the shape holds.

> **Not your starting point?** [Thirty minutes and no accounts](quickstart.md) · [users see each other's content](social-app.md) · [the data is behind someone else's API](external-api.md) · [a project you already started](existing-project.md) · [an app already in the stores](legacy-app.md). Full index: [TUTORIALS.md](../TUTORIALS.md).

---

## Before you start

**Have these ready.** Not having them is the most common reason a session stalls halfway.

| | Why |
|---|---|
| A physical device, iOS or Android | A simulator proves nothing about fonts, shadows, permissions or push. Several `Done when` items cannot be ticked without one. |
| 30–40 minutes of undivided attention for discovery and design | These two phases are conversation. Answering them while distracted produces a plausible product definition, which is worse than none. |
| Accounts for the services you will actually use | Auth provider, backend, error tracking. The agent will tell you which ones when the plan is cut — you do not need them on day one. |
| An Apple Developer and/or Google Play account, eventually | Only needed at `ship`. Push notifications and purchases also need them. |

**One thing to internalize.** The agent is not going to guess. If you answer "the usual settings" it will ask one follow-up and then write `UNDECIDED — ask before assuming` into a file, and every later step will stop on it. That is the mechanism working, not the agent being difficult.

---

## How the whole thing works, in three facts

**1. Three markdown files are the state.** There is no database, no `.mobilekitrc`, nothing hidden. `docs/PRODUCT.md`, `docs/DESIGN.md` and `docs/BUILD-PLAN.md` in your project *are* the workflow's memory. You can read them, edit them by hand, review them in a pull request, and hand them to a colleague who has never heard of this tool.

**2. Every command refuses rather than improvises.** Ask for a screen before `DESIGN.md` exists and you get told which command writes it. This is the single most valuable behaviour in the library: an agent that fills gaps confidently is an agent that builds the wrong app quickly.

**3. Reports have three outcomes, not two.** Every step ends by walking its `Done when` checklist and marking each item **met**, **not met**, or **not verifiable**. That third one is the honest one — "I could not test push on a device" is information, and burying it inside a tick is how a broken build reaches a store.

---

## Phase 0 — Prepare the project

```bash
mkdir sarau && cd sarau && git init
```

```
/mobilekit:init
```

The agent reads the directory, finds no `expo` dependency, and asks whether to scaffold, whether this is a legacy app, or whether you are in the wrong folder. Confirm it is new. It writes `AGENTS.md` with what is true regardless of the product — nothing else, because there is no product yet — and marks the domain sections `TBD`.

**Working in an existing project?** `init` reads your `package.json`, your folder layout and your existing `AGENTS.md` or `CLAUDE.md`, and extends rather than replaces. It copies nothing into your repo.

---

## Phase 1 — Discovery

```
/mobilekit:discovery
```

This is an interview, one question at a time, each with a recommended default so most of your answers are a confirmation. Seven blocks. **Block B is the one that pays for the whole session**: it replaces the generic `Item` that would otherwise appear in forty files.

A real exchange from Sarau:

> **What is the one thing this app is mostly about?**
> Default: I cannot infer this — a book club has at least three candidates (the club, the meeting, the book). Which is the object a user opens the app to interact with?
>
> — The meeting. People open it to see what to read before Thursday.
>
> **What is the real vocabulary? List the 3–7 nouns you would use talking to a colleague, and how they relate.**
>
> — Club has many Meetings. A Meeting covers one Reading, which is a range of a Book. Members leave Notes on a Reading.
>
> **Does content get authored by you, created by users, or both?**
> Recommended: both, given Notes — confirm.
>
> — Both. Books come from a catalogue I curate; Notes are the members'.

From here on, the code says `Meeting`, `Reading`, `Note`. Not `Item`, not `Event`, not `Data`. That is the entire point of the block.

Then Block F, capabilities. Each one is now / later / never:

| | Sarau's answer | Consequence |
|---|---|---|
| Payments | never | No purchase prompt runs, no dependency installed |
| Push | now — reminder before a Meeting | `push-notifications.md` enters the plan, and so does `deep-linking.md` |
| AI | never | — |
| Analytics & errors | errors now, analytics later | `error-tracking.md` in, `analytics.md` out |
| i18n | later | Out of the plan, but `design-system.md` still avoids baking English into layout widths |
| Media upload | never | No camera, no storage, no signed URLs |
| Dark mode | now | — |

**What you get:** `docs/PRODUCT.md`, under 100 lines, with a `## Open questions` section listing anything you deflected. It is read before every subsequent task, which is why it stays short.

> **The failure this prevents.** Skip discovery and the agent infers a domain from your folder name. `sarau/` reads as an events app, and you get `Event`, `Attendee` and `Venue` — plausible, coherent, and wrong in a way that takes a week to unpick because it is spread across every file.

---

## Phase 2 — Design

```
/mobilekit:design
```

Three steps. The second waits for the first.

**Step 1 — structure.** The screen inventory is derived from your core journey and then challenged: every screen must trace to a journey step or to a capability marked "now", and one that traces to neither gets dropped with the reason stated. Sarau lost a "Discover clubs" screen this way — nothing in the journey reached it.

Then the four states, per core screen. This is the part people skip and the part that decides whether the app feels finished:

| State | Sarau's Meeting list |
|---|---|
| Empty | "No meetings scheduled yet." One action: *Schedule the first one*. |
| Loading | Skeleton rows shaped like a meeting row, not a spinner |
| Error | "Could not load meetings." Retry. Already-loaded rows stay visible. |
| Populated | Next meeting pinned at top, past ones below, dimmed |

Most bugs reported as "the app is broken" are one of those four missing. Deciding them now costs minutes; retrofitting them costs a rewrite of every screen.

**Step 2 — visual system.** If you have a Figma export or screenshots, attach them: `@design/sarau.png`. The agent extracts palette, type rhythm, density and corner style and confirms before anything becomes a token. If you have nothing, it proposes two or three *directions* in one line each — "calm and dense, like a reading app: muted surface, tight spacing, one accent" — and **you pick**. It will not choose a palette for your product.

**Step 3 — identity assets.** Icon, adaptive icon, splash. It records what is missing rather than shipping a placeholder, because a placeholder icon is a rejected submission.

**What you get:** `docs/DESIGN.md`.

---

## Phase 3 — Cut the plan

```
/mobilekit:plan
```

59 prompts go in, your app's steps come out. Four things happen:

1. Every capability marked later/never is removed, and appears in a **Skipped** table with the reason — so six months later you can see it was a decision, not an oversight.
2. Generic screen steps are replaced by your real screens, core first.
3. Mutually exclusive prompts get decided with a one-line reason.
4. **Your repo is read.** Anything already installed is marked done, not queued.

Sarau's plan, abbreviated:

```markdown
## Foundation
- [x] expo-setup · already present
- [ ] dev-environment · push and permissions need a development build
- [ ] nativewind
- [ ] design-system
- [ ] domain-model
- [ ] ui-components
- [ ] app-shell · boot: session and fonts behind the splash; the auth gate lives here

## Platform
- [ ] auth-clerk · managed, because there is no backend team here
- [ ] supabase
- [ ] react-query
- [ ] zustand

## Screens
- [ ] tab-navigation · Meetings · Readings · Notes · Profile
- [ ] list-screen · Meetings
- [ ] detail-screen · Meeting
- [ ] account-recovery

## Features
- [ ] dark-mode
- [ ] native-permissions
- [ ] push-notifications
- [ ] deep-linking
- [ ] offline · cached reads only

## Release
- [ ] testing
- [ ] accessibility
- [ ] performance
- [ ] security-review
- [ ] store-compliance
- [ ] error-tracking
- [ ] eas-build
- [ ] beta-and-review
- [ ] release-rollback

## Skipped
| Step | Why |
|---|---|
| media-upload | PRODUCT.md: media = never |
| monetization, in-app-purchases, payments, ads | PRODUCT.md: payments = never |
| ai-features | PRODUCT.md: AI = never |
| analytics | PRODUCT.md: analytics = later |
| i18n | PRODUCT.md: i18n = later |
| content-moderation | Notes are visible only inside a private Club — confirm if that changes |
```

Note the last row. Moderation was skipped **conditionally**, with the condition written down. Make Sarau's clubs public and that skip becomes wrong — and the plan says so rather than leaving you to remember.

**One box is always one prompt file.** Two never share a box, because the next phase runs one at a time on purpose.

---

## Phase 4 — The build loop

```
/mobilekit:next
```

Repeat until the plan is empty. Each run: announces the step and gives you a chance to skip, grills its questions one at a time, resolves versions and gets that version's docs, builds, walks the checklist, ticks the box.

**Expect it to stop.** Here is what stopping looks like, and what to do:

| It says | Why | You |
|---|---|---|
| "I need the NativeWind 5 install guide — paste it, give me a link, or save it to `docs/vendor/nativewind@5.md`" | It read your `package.json`, and it will not write setup from memory. Config layout moved between majors and stale steps are the most common failure in agent-built mobile apps. | Paste the page. Saved under `docs/vendor/`, it is read automatically next time — the ask happens once. |
| "`PRODUCT.md` marks Note visibility `UNDECIDED`. Club-only, or public?" | `domain-model` cannot write a row-level policy without knowing. A table with per-user data and no policy is a data leak, not a TODO. | Answer. It writes the answer back into `PRODUCT.md`. |
| "Here is the entity table. Approve before I write the migration." | Schema is expensive to unwind. | Read it properly. This is the highest-leverage five minutes of the build. |
| "Blocked: this needs a Clerk publishable key." | It will not invent a credential or stub one to keep moving. | Create the account, paste the key. The box stays unchecked until it works. |
| "Recommended default: A — single welcome screen. Confirm or change." | An option is a question. | Confirm, or pick another. |

**Order matters and the plan encodes it.** `domain-model` before any screen, because screens built on `Item` get retrofitted and that retrofit is the most expensive rework in the build. `app-shell` before the first screen, so auth, onboarding and any lock plug into one gate instead of fighting over the root layout. `native-permissions` before `push-notifications`. `secure-backend` before anything holding a secret. `privacy-consent` before any analytics SDK, because an SDK that initializes on launch has already collected before your consent screen renders.

**Checking progress:**

```
/mobilekit:status
```

```
Phase:      build
PRODUCT.md  ok · 1 UNDECIDED
DESIGN.md   ok
BUILD-PLAN  9/24 · next: detail-screen
Drift:      plan says zustand done, zustand not in package.json
Next:       /mobilekit:next
```

That `Drift` line is the most useful output in the tool. A ticked box with no dependency installed is a lie in a file, and this is what catches it. It tells you which side is wrong and leaves the fix to you.

**Adding something out of order:**

```
/mobilekit:build media-upload
```

Runs one prompt regardless of the plan, and names the prerequisites it is missing instead of working around them.

---

## Phase 5 — Ship

```
/mobilekit:ship
```

A gate, not a step. Nine prompts in a fixed order, because each finds problems that are cheaper before submission than after: tests → accessibility → performance → security review → error tracking → consent → store compliance → build → beta and the review loop. That last one treats a first-submission rejection as the normal case: testers before the public, review notes a stranger can follow, and the resolution-center loop planned rather than improvised.

Plus three checks that belong to the gate itself:

- **The Expo project doctor.** A dependency mismatch caught in one command is a crash someone else finds in production.
- **The secret leak sweep.** `git ls-files` for anything credential-shaped, `.gitignore` confirmed, then a real build grepped for each secret value. If something is found: the key has to be **rotated**, not deleted — it is in git history now.
- **A physical device.** If a preview build never ran on real hardware, the report says so instead of implying it passed.

**Budget real time for `store-compliance`.** It is the phase that surprises people. The privacy manifest and required-reason API declarations are a hard rejection; the data-safety declaration has to match what the app actually sends rather than what you intended; the reviewer needs a working account with any second factor they cannot receive; and screenshots must come from the build you are submitting. None of this is code, all of it blocks.

---

## Phase 6 — After real users

```
/mobilekit:build post-release
```

Run this **after** a production build has been out long enough to produce a baseline. Not before — a threshold set on a number you have never seen is a noise generator, and an alert that cries wolf twice gets muted for the rest of the app's life.

Four numbers, and everything else is diagnostic:

1. **Crash-free session rate** — alert on a drop *relative to the previous release*, never an absolute floor.
2. **The success action, per day** — if this falls and nothing crashed, something in the funnel broke silently, which is worse.
3. **Drop-off at the worst funnel step.**
4. **New unhandled error signatures in the current release** — new is what matters.

Then, before you need it:

```
/mobilekit:build release-rollback
```

Because mobile has no rollback. A binary already installed on a phone cannot be recalled. What you have instead is a set of levers with different reach, and this writes the runbook while nobody is panicking.

---

## The four mistakes that cost the most

**Skipping discovery because you "know what you're building".** You do; the agent does not, and it will build from what it can see, which is your folder name. Twenty minutes here or a week of unpicking `Item` later.

**Answering the grill in a hurry.** Every vague answer becomes either an `UNDECIDED` that blocks a step later or, worse, a plausible default nobody chose. The questions come one at a time specifically so you can think about each one.

**Building screens before `domain-model`.** The plan orders it correctly; overriding that order with `/mobilekit:build home-screen` is how you get a home screen wired to a shape that changes next week.

**Ticking boxes yourself.** The checklist is not paperwork — items like "read another user's row and be denied" or "airplane mode: cached screens render, uncached ones explain themselves" are the actual test. A box ticked without running it converts a known unknown into an unknown unknown.

---

## Where to look next

- [`COMMANDS.md`](../COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../prompts/README.md`](../../prompts/README.md) — all 59 prompts with a description each, and the reference build order
- [`../prompts/RULES.md`](../../prompts/RULES.md) — the rules every prompt inherits. Worth reading once yourself.
- [`../CONTRIBUTING.md`](../../CONTRIBUTING.md) — adding a prompt, or a whole vertical the library does not cover

**Already have an app in production?** None of the above is your entry point. A shipping app has a domain, users and links that outrank any interview, so inventory replaces discovery — [legacy-app.md](legacy-app.md) walks that path, across all four starting points.

**Building something with a shape this example did not cover?** [social-app.md](social-app.md) for an app where members see each other's content, and the authorization and moderation work that comes with it. [external-api.md](external-api.md) for data behind an API you cannot change.
