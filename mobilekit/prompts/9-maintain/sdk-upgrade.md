# Expo SDK Upgrade

Run this on a schedule, not when something breaks. The stores raise their minimum target platform version every year, and an app that cannot build against a current SDK eventually cannot be updated at all — not with a fix, not with a rollback.

Prereq: a physical device per platform you ship to, a clean working tree, and the app currently building so there is a known-good baseline to compare against.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Upgrade this project to Expo SDK [target], one major version at a time.

### One major at a time

Skipping four SDKs does not save four upgrades. It buys one much harder upgrade, because every breaking change lands in a single diff where the same red screen has four candidate causes and no way to bisect them. An app four versions behind is **four sequential upgrades**, each one committed and verified on a device before the next begins.

### Grill

- **What is the target?** A: the current SDK. B: the oldest SDK that still satisfies the stores' present minimum target platform version. C: a single major, to unblock one specific dependency. Recommended default: A — every major you stop short of is an upgrade you will do anyway, later, with more drift around it.
- **Is a release deadline in the way?** If yes, the upgrade stops at a major boundary that builds and ships from there. A half-finished major is not a state you release from.
- **What happens to hand edits in the native projects?** The repo says whether `ios/` and `android/` are committed and which config plugins are declared — read that. The decision is what happens to each hand edit found there: promoted to a config plugin, or dropped. A patch applied directly to a generated file vanishes at the next regeneration, silently, and the symptom shows up in a store build weeks later.
- **Where does verification happen?** Name the physical devices and OS versions. A simulator-only pass does not exercise push, biometrics, deep links or store signing (`testing.md`).
- **When a native dependency does not support the target, what gives?** A: replace the library. B: cut the feature it powers. C: stay on the current SDK until upstream ships. Recommended default: A if a maintained equivalent exists — C is only viable while the current SDK still satisfies the stores.

### Build

**Before touching anything**

- A dedicated branch off a clean tree, and the current version built and run on a device first. Without that baseline, every post-upgrade failure is unattributable
- Read the release notes and upgrade guide for the target major per `RULES.md` §3 — ask the developer for them if this agent cannot fetch them. Ask for the guide of the **target version specifically**; that document is the job, and working from memory here is how a prompt produces config for an SDK that no longer exists
- Record the current SDK, the New Architecture status, and every native dependency with its declared support, before changing a line

**Upgrade in the supported order**

- The SDK first, then the packages it pins, using the tool the SDK provides for exactly this. Hand-bumped dependencies produce version combinations nobody tests
- Resolve the toolchain's own complaints about mismatched packages until it is quiet. A warning ignored at this step is the crash at the next one

**The native side**

- Where the project uses managed configuration, regenerate the native projects from config rather than patching them; anything that has to live in there is expressed as a config plugin or it is lost. Where `ios/` and `android/` are maintained by hand, reconcile deliberately and record what changed

**Breaking changes, one library at a time**

- Work the release notes, not memory. The recurring ones across this library: styling and config file layout (`nativewind.md`), animation worklet and layout APIs (`animations.md`), monitoring transaction versus span APIs (`error-tracking.md`), notification handler fields (`push-notifications.md`), and persistence adapters (`zustand.md`)
- Each library's change traced to a line in the release notes. An API "fixed" by guessing compiles and then behaves differently

**The New Architecture**

- Establish whether the target requires it, then check every native dependency for support **before starting**. This is the most common hard blocker, and discovering it mid-upgrade means unwinding rather than deciding
- Interop layers are a bridge, not a destination — record anything relying on one as debt (`legacy-modernization.md`)

**Verify**

- A real build on a real device per platform, and the core journey from `PRODUCT.md` walked by hand — not just a bundler that starts
- The test suite green, and the silent breakers checked deliberately: fonts, shadows and elevation, safe areas, keyboard avoidance, deep links, push registration and tap handling, and persisted-store hydration from a build of the previous version
- Startup and list scrolling compared against the baseline (`performance.md`); a major regresses both without erroring

**Ship carefully**

- One commit per major, each building and running on its own
- A staged rollout, and `release-rollback.md`'s levers confirmed available *before* submission. An upgrade regression is not one feature failing, it reaches every user at once
- CI updated to the new toolchain in the same branch (`ci-cd.md`), so the first green build is not a local-machine artefact

### Done when

- [ ] One major per commit, each with the app building and launching on a device before the next began
- [ ] Every breaking change traced to a line in the target's release notes, with the `RULES.md` §3 step named
- [ ] Native projects regenerate cleanly, with no hand patch left orphaned in a generated directory
- [ ] The core journey from `PRODUCT.md` walked by hand on a real device, both platforms
- [ ] A build of the previous version upgraded in place, with persisted state still readable and the user still signed in
- [ ] Test suite green, push and deep links exercised on device, CI building the upgraded project, and the rollback levers confirmed available before submission
- [ ] Anything left unverified stated explicitly, per `RULES.md` §7
