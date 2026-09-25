# Legacy App Modernization

The entry point for an app that already ships. Run it **instead of** `product-discovery.md`: an app in production has a domain, users and constraints that outrank any interview, so discovery is replaced by inventory.

Prereq: the repo, access to both store listings, and the current version building from a clean checkout — or the fact that it does not, which is already the first finding.

---

## Prompt

Read `RULES.md` (this library) and AGENTS.md first. There is no `docs/PRODUCT.md` yet — this prompt produces one.

Inventory the shipping app, then agree a modernization path before changing anything.

### Hard rules

1. **The shipping app is the specification.** Where the code and the developer's memory disagree, the code is right and the disagreement is a finding to record, not a detail to smooth over.
2. **Nothing is rewritten before it is inventoried.** A rewrite estimated from a folder listing is the estimate that becomes a two-year project.
3. **Feature parity is a list, not an adjective.** Produce the list. An unnamed feature is a feature that gets dropped and then discovered by a user.
4. **The users are already there.** Any migration path preserves their sessions, their local data and their deep links — or states plainly what breaks, who it affects, and what the recovery is.
5. **A big-bang rewrite is a decision the developer makes explicitly**, with the parity list in front of them. It is never a default the agent slides into because the code was unpleasant to read.

### Grill

Look up before asking: what runs in production and what the store listing says it does are both facts — read them in the repo and in the two listings first.

- **What actually hurts?** Crashes, a toolchain that no longer builds, a store deadline, hiring, or a feature that cannot be built on the current stack. Modernization with no named pain is refactoring with a budget — if nothing hurts, recommend stopping here.
- **Is there a hard deadline**, specifically a store minimum target platform version with a date (`store-compliance.md`)? That date, not taste, sets the scope of everything below it.
- **Who maintains this now, and what can they still build?** A path needing two native platforms plus a JS stack from one part-time maintainer is a plan that stalls half-migrated.
- **Is there a test suite, a CI pipeline, or a reproducible build?** If none, the first delivery is a characterisation harness over the core journey, because without one parity is unfalsifiable (`testing.md`, `ci-cd.md`).
- **How many users, on which app versions?** A long tail on an old build constrains every path: server contracts and stored data must keep working for versions you cannot update.

### Step 0 — Confirm the scenario

State which applies, from what you read in the repo, and get it confirmed:

- **A** — React Native, bare or ejected, several versions behind.
- **B** — Expo, several SDKs behind.
- **C** — Hybrid: Cordova, Ionic, or a WebView wrapper.
- **D** — Native Swift/Kotlin, considering React Native incrementally.

Then follow only that scenario's section.

---

## Scenario A — Bare or ejected React Native, behind

1. **Inventory the native projects.** Every hand modification in `ios/` and `android/`: build settings, entitlements, manifest entries, patched pods and gradle files, `patch-package` entries. Each one either becomes a config plugin or is lost at the next regeneration — silently, with the symptom arriving as a failed store build weeks later.
2. **Dependency compatibility matrix**, one row per native dependency: installed version, current version, last release date, New Architecture support, and either a named replacement or "no equivalent". Unmaintained native modules are the hard blockers; find them before choosing a target, not mid-upgrade.
3. **Stay bare, or adopt managed native configuration?** Managed makes every future upgrade cheap and requires every hand-patch to have a config-plugin path. Recommended default: adopt managed where the matrix shows a path for each patch, and stay bare while even one has none — a patch with nowhere to go is a regeneration that quietly drops a feature.
4. **Navigation.** If routing predates the current router, decide whether it migrates now or later. Its URL contract is a published API; read `deep-linking.md` before changing a single path.
5. **Then upgrade with `sdk-upgrade.md`, one major at a time.** Upgrade in place *before* restructuring: two variables at once is one undebuggable diff.

---

## Scenario B — Expo, several SDKs behind

The cheapest path of the four, and mostly `sdk-upgrade.md`. The work that belongs here is the decision-making around it.

1. **Compatibility check across the whole range you must cross**, not just the target. A dependency that breaks two majors in is a blocker discovered on day one, not on day six.
2. **Sequence plan**: which majors, in which order, what each unblocks, and which boundaries a release can ship from.
3. **Architecture work during or after?** Recommended default: after. A failed upgrade attributable to the SDK is a day of work; the same failure tangled into a refactor is a week of bisecting your own diff.
4. Everything else is `sdk-upgrade.md`. Do not re-derive it here.

---

## Scenario C — Hybrid (Cordova, Ionic, WebView wrapper)

1. **Inventory screen by screen** which screens are genuinely web and which depend on native plugins. **The plugins are the real cost**, not the HTML.
2. **Keep the WebView, or rebuild screen by screen?** A WebView screen embedded in a native shell is a legitimate intermediate state, not a failure — it is what lets each rebuilt screen ship on its own instead of waiting for all of them.
3. **Map plugin to native equivalent**, one row per plugin, and name explicitly those with none so it becomes a decision rather than a surprise. Permission prompts and their copy change on the way across: `native-permissions.md`.
4. **Session, storage and cookie migration.** WebView cookies, `localStorage` and plugin-owned storage do not carry across on their own. Migrate them, or every user is signed out on update day and support hears about it before you do.
5. **Preserve the link contract already in the wild.** Every URL and universal link the old app claimed still resolves after the change (`deep-linking.md`); links live in emails and messages you cannot edit.

---

## Scenario D — Native app adopting React Native incrementally

1. **Brownfield, not replacement.** React Native renders inside existing native screens; the native app stays the host and the shell is untouched.
2. **The boundary decision**: which screens cross, and in what order. Recommended default: one low-risk, high-churn screen first, as a tracer through the entire toolchain — build, signing, crash symbolication, release — before a critical flow depends on it.
3. **State and session cross once, in one place.** A single boundary module exposes the session and the minimum shared state. Two ad-hoc bridges become two sources of truth and a sign-out that only half works.
4. **Two build systems and two release trains now coexist.** CI, signing, symbolication, review time and on-call knowledge all double (`ci-cd.md`, `error-tracking.md`). State that cost out loud, against the team you actually have.
5. **Ask whether adopting React Native is justified for this app at all.** If the team is native, the app is stable, and the named pain is not shared-code velocity, the honest recommendation is to stay native and stop here.

---

## Contracts — keep or replace (all scenarios)

The parity list covers what users see; this covers what the app talks to. One row per technical contract, each marked **keep / replace / wrap**, decided by the developer with the inventory in front of them — never defaulted:

- **API endpoints** — the backend contract. Old app versions in the wild pin it harder than taste does; a replaced endpoint breaks every build you cannot update.
- **Authentication** — mechanism and credential store. Replacing it signs everyone out unless the old credential is read once and exchanged.
- **Sync / offline model** — queues, drain triggers, conflict rules. Usually the least documented and the most load-bearing part of the inventory.
- **Local storage** — schemas the new code must still read at least once, or the data on updating devices is gone.
- **Push** — provider and token registration; a replaced sender is silent until every device re-registers.
- **Deep links** — the URL contract (hard rule 4 says it survives; this row records how).

**Wrap** means keep the contract behind one adapter so screens migrate now and the contract is replaceable later — the honest middle when "keep" blocks the target stack and "replace" breaks users you cannot update.

---

## The plan (all scenarios)

Write `docs/MODERNIZATION.md`:

- **Inventory** — features, screens, native capabilities (push, camera, location, biometrics, background work, payments), and every dependency with its support status.
- **Parity list** — one row per user-visible behaviour, each marked keep / drop / defer. Confirm it with someone who uses the app, not only against the code; the code does not know which behaviours users depend on.
- **Contract decisions** — the keep / replace / wrap table above, with a reason per replace.
- **The chosen path and its reason**, plus the paths rejected and theirs.
- **The sequence**, in verifiable steps that each end in something shippable. A step ending in "the migration is half done" is not a step, it is a stall.
- **What is deliberately dropped**, and who approved each drop, by name.
- **Risks with a trigger** — the observable that says the risk has arrived, not a severity adjective.

Then derive `docs/PRODUCT.md` from the inventory, using the output structure in `product-discovery.md`: domain vocabulary taken from the existing code and store copy, capabilities marked from what actually ships, journey taken from the screens that exist. Ask **only about the gaps**. A live app has already answered its audience, its central object and its core journey — re-interviewing a maintainer on questions their app answers is how they stop trusting the process.

From here the normal flow continues, with one difference at each step: run `domain-model.md` next; the design phase derives `docs/DESIGN.md` from the screens that ship and the parity list, grilling only where the redesign deliberately changes something; the plan phase builds `docs/BUILD-PLAN.md` **from the sequence in `docs/MODERNIZATION.md`**, using the greenfield reference order only for what the sequence does not cover. Two competing plans is a stall — the migration sequence is the spine.

---

### Done when

- [ ] The current app builds and runs on a device from a clean checkout, before anything changed
- [ ] The parity list is complete enough that the developer confirms nothing is missing from it
- [ ] Every dependency has a stated support status, and every blocker is named with its replacement or the absence of one
- [ ] The chosen path is the developer's decision, recorded in `docs/MODERNIZATION.md` with its reason
- [ ] The first step of the sequence is shippable on its own
- [ ] User sessions, local data and existing links each have a stated fate: preserved, migrated, or broken with a named recovery
- [ ] Every external contract — endpoints, auth, sync, storage, push, links — carries a recorded keep / replace / wrap decision
- [ ] `docs/PRODUCT.md` exists, derived from the app rather than invented, so the normal flow can continue
- [ ] Anything unverified stated explicitly, per `RULES.md` §7
