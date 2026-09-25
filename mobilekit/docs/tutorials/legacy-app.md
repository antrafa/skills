# Modernizing an app that already ships

The skill's second entry point. For a reader whose app is in the stores, has users, and cannot be restarted — where discovery is the wrong first move because the product has already answered every question an interview would ask.

The example is **Ponto**, a time-clock app built in Cordova in 2019. Employees clock in and out; each punch takes a photo and a location and syncs to a corporate API. Three native plugins: camera, geolocation, background sync. The toolchain no longer builds on a current machine, and a store platform-version deadline is approaching.

That is scenario C, the hybrid case. The other three starting points are covered in shorter form near the end.

> **Not your situation?** An Expo project you started but never shipped is [existing-project.md](existing-project.md) — it has no users, which changes everything. A new app is [new-app.md](new-app.md). Full index: [TUTORIALS.md](../TUTORIALS.md).

---

## Before you start

| | Why |
|---|---|
| The repo, and the current version building — or the fact that it does not | "It does not build on a current machine" is not a blocker to starting. It is the first finding, and it goes in the inventory. |
| Access to **both** store listings | The listing is a specification the maintainer did not write and cannot argue with. It says what the app promises users. |
| Someone who actually uses the app | The code knows every behaviour and knows which ones matter to nobody. Parity gets confirmed against a user, not a grep. |
| The number of live users, per app version | A long tail on an old build constrains every path below it: server contracts and stored data must keep working for versions you cannot update. |
| A physical device, per platform | Unchanged from every other path, and more important here — you are comparing new behaviour against shipped behaviour. |

**What you do not need:** a decision about the target stack. Making that decision before the inventory is the mistake this whole prompt exists to prevent.

---

## Why not discovery

Run `/mobilekit:discovery` on Ponto and it will ask you what the app is for, who uses it, and what its central object is. You know all three. Worse, so does the app — and being interrogated about facts your own product answers is how a maintainer stops trusting the process by question four.

So the entry point is different:

```
/mobilekit:build legacy
```

`RULES.md` §1 splits every question into two kinds: **a fact is looked up, a decision is asked.** On a greenfield app almost everything is a decision. On Ponto almost everything is a fact — sitting in the repo, in the listing, in the plugin manifest. The prompt reads those and asks you only about the gaps.

It also states its own governing rule up front, and it is worth reading twice:

> **The shipping app is the specification.** Where the code and the developer's memory disagree, the code is right and the disagreement is a finding to record, not a detail to smooth over.

On Ponto that rule fired immediately. The maintainer's summary was "it photographs the punch and sends it". The code also writes a queued punch to local storage when the API is unreachable and drains it on next launch — a whole offline path nobody mentioned, because it was added in 2020 by someone who has left. Nobody would have carried it into a rewrite. Every user who clocks in from a basement garage depends on it.

That is what the inventory is for.

---

## Phase 1 — The shared grill

Five questions before it branches. They are short because most of the answers are facts it has already read.

**What actually hurts?**

> Recommended: name it, or stop. Modernization with no named pain is refactoring with a budget.
>
> — The toolchain does not build on a current macOS, and there is a store minimum-target deadline in four months.

Two named pains, one with a date. Everything below is scoped by that date.

**Who maintains this, and what can they still build?**

> — One developer, part-time, comfortable in JS. No iOS or Android native experience.

This answer eliminates a path before it is proposed. A plan needing two native platforms plus a JS stack from one part-time maintainer is a plan that stalls half-migrated, which is the worst state of the four.

**Is there a test suite, CI, or a reproducible build?**

> — None.
>
> Then the first delivery is a characterisation harness over the core journey, because without one, parity is unfalsifiable.

Read that consequence carefully. Without something that captures current behaviour, "we kept everything working" is an opinion. This is the one place where the prompt adds work before adding value, and it is the right call: you cannot verify a migration against an app you cannot run twice the same way.

**How many users, on which versions?**

> — About 900. Roughly 200 still on a 2021 build.

Those 200 mean the corporate API contract cannot change, punch payloads must stay readable, and any storage migration has to tolerate the old shape.

**Is there a hard deadline?** Already answered — four months, store minimum target.

---

## Phase 2 — Confirm the scenario

The prompt states which it read from the repo and asks you to confirm:

- **A** — React Native, bare or ejected, several versions behind
- **B** — Expo, several SDKs behind
- **C** — Hybrid: Cordova, Ionic, or a WebView wrapper ← **Ponto**
- **D** — Native Swift/Kotlin, considering React Native incrementally

It then follows only that scenario's section. The three you are not on are summarised at the end of this page.

---

## Phase 3 — Scenario C, the inventory

**Screen by screen, what is web and what is native.** For Ponto: six WebView screens and three plugins.

**The plugins are the real cost, not the HTML.** This is the sentence readers most need and least expect. Rewriting six screens of HTML into React Native is mechanical, estimable work. The plugins are where the unknowns live:

| Cordova plugin | Native equivalent | Note |
|---|---|---|
| camera | Expo camera / image picker | Permission copy changes on the way across — `native-permissions.md` |
| geolocation | Expo location | "While using the app" versus "always" is a decision the old plugin made implicitly |
| background sync | **No equivalent** | Cordova's background behaviour and a managed workflow's are not the same capability |

That third row is the point of the table. It does not get silently worked around and it does not get discovered in month three — it becomes a decision now: change the sync model to drain on foreground, or take on a native module and lose the managed workflow.

**Then the decision readers get wrong:**

> **Keep the WebView, or rebuild screen by screen?**
>
> Recommended: keep it, at first. A WebView screen embedded in a native shell is a legitimate intermediate state, not a failure — it is what lets each rebuilt screen ship on its own instead of waiting for all of them.

The alternative is a big-bang rewrite, and the prompt refuses to let that happen by drift:

> **A big-bang rewrite is a decision the developer makes explicitly**, with the parity list in front of them. It is never a default the agent slides into because the code was unpleasant to read.

Choose it deliberately if the app is small and the parity list is short. On Ponto, with 900 users and a four-month deadline, it is not the answer — and being asked forces you to say why rather than defaulting into eighteen months.

---

## Phase 4 — The parity list

> **Feature parity is a list, not an adjective.** Produce the list. An unnamed feature is a feature that gets dropped and then discovered by a user.

Abbreviated, from Ponto:

| Behaviour | keep / drop / defer | Approved by |
|---|---|---|
| Clock in / out with photo | keep | — |
| Location captured per punch | keep | — |
| Queue punches offline, drain on launch | keep | — the finding nobody remembered |
| Background sync while app closed | **drop** → drain on foreground | Named operations lead |
| Monthly timesheet PDF export | defer to phase 2 | Named operations lead |
| Portuguese-only interface | keep | — |
| "Shake to report a bug" | **drop** | Named operations lead — telemetry shows 4 uses in 2 years |

Two rules that make this table work rather than decorate a document:

**A drop needs a named approver.** Not "the team agreed" — a name. The background-sync row changes when a punch reaches the server, which is a payroll question, not an engineering one.

**Confirm it with someone who uses the app.** The code does not know which behaviours users depend on. The offline queue is in the code either way; only a user can tell you it is load-bearing.

---

## Phase 5 — What breaks for existing users

Every migration path either preserves these or states plainly what breaks, who it affects, and what the recovery is. There is no third option where it is not discussed.

**Sessions and storage.** WebView cookies, `localStorage` and plugin-owned storage do not carry across on their own. Get this wrong and every one of 900 employees is signed out on update morning — and support hears about it before you do, during the exact hour everyone clocks in.

**Queued punches in flight.** Some devices will update while holding unsynced punches in `localStorage`. If the new build cannot read that store, those punches are gone, and they are hours somebody worked. This has to be migrated, not assumed.

**The link contract already in the wild.** Every URL and universal link the old app claimed still has to resolve — `deep-linking.md`. Ponto's shift reminders link into the punch screen from emails sent months ago, and you cannot edit a sent email.

For Ponto:

| | Fate |
|---|---|
| Employee session | Migrated — read the old token store on first launch, exchange it, delete it |
| Queued punches | Migrated — one-time read of the old queue shape, then drained |
| Cached timesheet view | Broken, no recovery needed — regenerated from the API |
| Existing reminder links | Preserved — same paths, mapped through the new router |

---

## Phase 6 — The plan, and the handoff

`docs/MODERNIZATION.md` gets written with the inventory, the parity list, the chosen path and the paths rejected with their reasons, the sequence, the deliberate drops with their approvers, and risks each carrying a **trigger** — the observable that says the risk has arrived, rather than a severity adjective.

The sequence rule that matters:

> **The sequence, in verifiable steps that each end in something shippable.** A step ending in "the migration is half done" is not a step, it is a stall.

Ponto's first four:

```
1  Characterisation harness over clock in / clock out      ships nothing, unblocks everything
2  Expo shell hosting the existing WebView, all 6 screens  ships: same app, new toolchain, builds on a current machine
3  Punch screen rebuilt native, camera + location          ships: the one screen that needed the plugins
4  Offline queue rebuilt, old store migrated               ships: the finding, preserved
```

Step 2 is the one to notice. It ships an app that looks identical to users and does nothing new — and it is the highest-value step in the list, because it retires the dead toolchain and beats the store deadline on its own. A rewrite plan that could not ship until step 6 would have missed the date.

Then the handoff. `docs/PRODUCT.md` is **derived from the inventory** rather than interviewed: domain vocabulary taken from the existing code and store copy, capabilities marked from what actually ships, the journey taken from the screens that exist. You are asked only about the gaps.

From that point the rest of the library works normally, with one difference at each step — `domain-model.md` next; design derives `DESIGN.md` from the screens that ship instead of inventing them; and the plan phase takes `MODERNIZATION.md`'s sequence as its spine, so `BUILD-PLAN.md` is the migration order broken into prompt-sized boxes rather than the greenfield reference order. Then [new-app.md](new-app.md)'s build loop applies unchanged.

---

## The other three scenarios

**A — bare or ejected React Native, behind.** The inventory is of the native projects: every hand modification in `ios/` and `android/`, every patched dependency. Each one either becomes a config plugin or is lost at the next regeneration — silently, with the symptom arriving as a failed store build weeks later. Then the dependency matrix, one row per native dependency with its support status and New Architecture readiness, because unmaintained native modules are the hard blockers and you want them found before you pick a target. The recommendation: **upgrade in place before restructuring** — two variables at once is one undebuggable diff.

**B — Expo, several SDKs behind.** The cheapest of the four, and mostly [`sdk-upgrade.md`](../../prompts/9-maintain/sdk-upgrade.md). The work that belongs here is the compatibility check across the whole range you must cross rather than just the target — a dependency that breaks two majors in is a blocker you want on day one, not day six — plus the sequence plan and one decision: architecture work during the upgrade, or after? Recommended after. A failed upgrade attributable to the SDK is a day; the same failure tangled into a refactor is a week of bisecting your own diff.

**C — hybrid.** This page.

**D — native Swift/Kotlin adopting React Native.** Brownfield, not replacement: React Native renders inside existing native screens and the native app stays the host. The boundary decision is which screens cross and in what order — recommended is one low-risk, high-churn screen first, as a tracer through the entire toolchain (build, signing, crash symbolication, release) before a critical flow depends on it. State and session cross **once, in one place**, or two ad-hoc bridges become two sources of truth and a sign-out that only half works. And the honest question the prompt insists on asking: if the team is native, the app is stable, and the named pain is not shared-code velocity, the recommendation is to stay native and stop.

---

## The ways a step stops on this path

| It says | Why | You |
|---|---|---|
| "The current version does not build. That is finding one." | There is no baseline to compare against | Fix the build first, or accept that parity is unverifiable and say so |
| "The code does X; you described Y. Which is intended?" | The shipping app is the specification | Decide. It is a finding either way |
| "This plugin has no equivalent. Change the model, or take a native module?" | Silently working around it is how a capability disappears | Decide, with the parity consequence in view |
| "This drop needs a named approver." | "The team agreed" means nobody owns it | Give a name |
| "Confirm the parity list is complete." | The code cannot tell you what users depend on | Ask a user. This is not a formality |
| "What happens to queued data on devices that update?" | Unreadable local state is a second incident | State the fate: preserved, migrated, or broken with a recovery |
| "Recommended: stay native and stop here." | Sometimes migrating is not justified | Accept it, or say what pain it misses |

---

## The mistakes that cost the most on this path

**Choosing the target stack before the inventory.** The estimate made from a folder listing is the estimate that becomes a two-year project. Every hard cost on Ponto — the plugin with no equivalent, the undocumented offline queue, the 200 users on a 2021 build — was invisible until something read the repo.

**Treating the WebView as a failure state.** Wanting all of it native at once is what turns a four-month deadline into a missed one. Ponto's step 2 shipped an app users could not tell apart from the old one, and it was the step that saved the release.

**Letting parity stay an adjective.** "We'll keep everything working" is not a plan, it is a hope with a nice tone. The list is tedious to produce and it is the only thing that makes the migration verifiable.

**Forgetting that an upgrade regression reaches everyone at once.** A new feature fails for the users who touch it; a bad migration fails for all 900 employees at 8am. Put the migration build through [`beta-and-review.md`](../../prompts/7-ship/beta-and-review.md)'s internal track first — a dozen employees for a week is where the session migration gets to fail cheaply — and run [`release-rollback.md`](../../prompts/8-observability/release-rollback.md) *before* the first submission, remembering that mobile has no rollback, only levers with different reach. The one that matters here is whether the previous good bundle is identifiable by a recorded id, because a channel pointing at "latest" with no record of what was previous is not a lever, it is a hope.

---

## Where to go next

- [new-app.md](new-app.md) — the build loop, which applies unchanged once `PRODUCT.md` is derived
- [`../../prompts/9-maintain/sdk-upgrade.md`](../../prompts/9-maintain/sdk-upgrade.md) — the one-major-at-a-time procedure every scenario ends up running
- [`../COMMANDS.md`](../COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../../prompts/RULES.md`](../../prompts/RULES.md) — the rules every prompt inherits. Short, and §1 is why this path asks so little.
