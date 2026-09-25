# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.0] — 2026-08-11

### Added

- **`codex/` — one nested skill per command, so the Codex `$` picker shows descriptions.**
  Codex reads no frontmatter from custom prompts, so the eight commands listed under
  `/prompts:` appear bare; its skills surface reads `name`, `description` and
  `metadata.short-description`, and discovers nested `SKILL.md` files recursively.
  `codex/<name>/SKILL.md` mirrors each command onto that surface as `$mobilekit-<name>`,
  description in the picker and matchable by intent. Both hosts read a `name:` key and
  demand different values in it, so each command exists twice on purpose —
  `install.sh --check` now fails when the two sets drift apart. Skills get no template
  substitution, so the two commands that take an argument say so in prose instead of
  `$ARGUMENTS`. The `/prompts:` entries stay linked: they are the only `/`-invoked route
  Codex has.
- The root `SKILL.md` carries `metadata.short-description`, the field the Codex `$`
  picker prefers over the long description.

### Changed

- **The next step is named by its command, never by a file.** Phase reports were pointing
  developers at internal prompt files (`domain-model.md`, `design-conception.md`) they do
  not know how to invoke. `prompts/RULES.md` now binds the developer-facing edge to the
  phase command or `/mobilekit:build <id>`, in the host's invocation form; filenames stay
  the internal ids.

## [2.4.0] — 2026-08-10

### Added

- **`1-discovery/market-signal.md`** — the check the rest of the library cannot perform:
  whether anyone outside the repo wants the app. An optional, recurring ritual that closes
  each phase with real-market contact — the pitch after `PRODUCT.md`, what it looks like
  after `DESIGN.md`, the beta invite, the public release — logged in `docs/LAUNCHES.md`
  with the responders who carry across moments. It never gates a phase: workflows offer it
  in their reports, and `status` shows the signal line only when the log exists. Hard
  rules: the developer sends everything, silence is a result, a friend's reply is
  labelled, and missing the same target twice means rereading `PRODUCT.md`, not a third
  rewrite.
- **`8-observability/next-feature.md`** — closes the post-release loop. When
  `BUILD-PLAN.md` empties and real users are in, it turns the weakest of the four numbers,
  `PRODUCT.md`'s "later" column and the qualitative signal into the next cycle, appended
  to `BUILD-PLAN.md` one prompt per box — so `next` runs it with no new mechanics.
  Candidates without a number are recorded as bets, never dressed up as data.
- **Activation recorded in `DESIGN.md`** — `PRODUCT.md` already named the success action;
  nothing said which screen carries it or the shortest first-run path to it.
  `design-conception.md` now records the activation path; `beta-and-review.md` uses it as
  the beta's pass bar and invites `market-signal` responders first; `analytics.md` derives
  the funnel from its steps. 59 prompts now.

### Changed

- The README's Quick start became **How to use it**: the whole loop in one listing —
  through `ship`, `post-release` and `next-feature` back to `next` — the three entry
  points, the refuse-and-name navigation rule, and every command with when to run it,
  what it needs and what it writes.

### Fixed

- The README claimed nine phase commands; there are eight.

## [2.3.0] — 2026-08-10

### Added

- **Contract decisions in `legacy-modernization.md`** — the parity list covers what users
  see; a new all-scenarios step covers what the app talks to. One row per technical
  contract — API endpoints, authentication, sync/offline model, local storage, push, deep
  links — each marked **keep / replace / wrap** by the developer with the inventory in
  front of them, never defaulted. "Wrap" keeps a contract behind one adapter so screens
  migrate now and the contract stays replaceable later. The table lands in
  `docs/MODERNIZATION.md` and the `Done when` checklist enforces it.

### Fixed

- **The legacy handoff was one-sided.** `legacy-modernization.md` said "the rest of the
  library works normally", but the design phase invented screens a live app already
  answers, and the plan phase built `BUILD-PLAN.md` from the greenfield reference order,
  competing with `MODERNIZATION.md`'s migration sequence. Both phases now recognise
  `docs/MODERNIZATION.md`: design derives `DESIGN.md` from the screens that ship and the
  parity list, grilling only where the redesign deliberately changes something; plan takes
  the migration sequence as the spine and uses the reference order only for what it does
  not cover. Contracts marked keep/wrap rule out competing prompts — a kept backend is
  `api-integration`, never `supabase`. The tutorial and the command reference reflect it.
- `install.sh` linked Antigravity skills into `~/.gemini/antigravity/skills`, a directory
  Antigravity does not read. Global skills live in `~/.gemini/config/skills`
  (antigravity.google/docs/skills); detection now keys on `~/.gemini/antigravity`, since
  `~/.gemini` alone can mean only Gemini CLI is installed.

## [2.2.0] — 2026-08-08

### Added

- **Six prompts closing critical-path gaps** found by a full audit of the library (57 prompts now):
  - `3-foundation/app-shell.md` — the root layout had no owner: auth, onboarding, hydration and
    the biometric lock all fought for it. Now they plug into one gate with a boot list behind
    the splash and the app-wide error boundary.
  - `3-foundation/dev-environment.md` — dev build vs Expo Go, devices, env files per
    environment, repo hygiene. Decided once, right after `expo-setup`, instead of discovered
    when Expo Go stops being enough.
  - `1-discovery/monetization.md` — a concept round that derives how the app earns from
    `PRODUCT.md` signals and teaches as it asks. Writes `PRODUCT.md §Monetization`, which
    `plan`, `in-app-purchases`, `payments` and `ads` read instead of re-asking.
  - `6-features/ads.md` — AdMob behind the consent chain; ads leave the not-covered list.
  - `7-ship/beta-and-review.md` — TestFlight / Play tracks with exit criteria, and the store
    rejection loop treated as the normal case.
  - `7-ship/security-review.md` — the adversarial sweep: re-test every ticked security check
    on the release build, the joints between features, the device storage dump, the logs, the
    red dependency audit. The ship gate is now nine steps.
- Consumable credits in `in-app-purchases.md` — server-side balance, granted exactly once,
  spent where the metered action runs.
- The README states the backend boundary explicitly: managed backend, API routes for
  secrets, or an existing API — building a standalone server is out of scope.

### Fixed

- Cross-prompt contracts that never landed at their target: the permission and biometric rows
  in `settings-screen`, storage and realtime in `supabase`, cache persistence in
  `react-query`, saved methods and refunds in `payments`, the consent gate ahead of
  `analytics` and `error-tracking`, and the kill switch `release-rollback` depends on.
- Release gaps in `eas-build` and `ci-cd`: recommended defaults on every grill question,
  Android keystore backup, and a `runtimeVersion` policy so an OTA update cannot land on an
  incompatible binary.
- Four prerequisite inversions in the reference build order (`deep-linking`,
  `secure-backend`, `account-recovery`, `release-rollback`), and the ship order divergence
  between `prompts/README.md` and `workflow/ship.md`.

### Changed

- Deduplication throughout: prompts point at the `RULES.md` section that owns each rule
  instead of restating it, and the screen state blocks defer to `DESIGN.md`, keeping only
  their screen-specific states.
- Checklist headings normalized to `Done when` across the library.
- All six tutorials and the command reference reflect the new flow.

## [2.1.0] — 2026-08-08

### Added

- **Six tutorials, indexed by starting point** in `docs/TUTORIALS.md`. The reference in
  `docs/COMMANDS.md` answers "what does `ship` do" but not "what does building an app with
  this feel like", and the second question is the one that decides whether the workflow gets
  used correctly. Each tutorial shows the commands typed, the documents produced, and where
  the agent stops and asks — with a worked example whose domain needs no explanation.
  - `tutorials/quickstart.md` — shared shopping list. Thirty minutes, no paid accounts, no
    backend. Ends at the first green step. Teaches why the plan comes out short: because the
    answers were short.
  - `tutorials/new-app.md` — book club. The full path to a monitored release.
  - `tutorials/social-app.md` — plant-swap community. Auth, row-level authorization,
    moderation as a store requirement, consent before any SDK initializes.
  - `tutorials/external-api.md` — transport timetables. The documentation ask, DTO versus
    domain, and how the source's limits decide what a screen can promise.
  - `tutorials/existing-project.md` — half-built workout journal. Adoption without
    restarting: `plan` ticking what already exists, and `status` catching drift.
  - `tutorials/legacy-app.md` — time-clock app in Cordova. The second entry point, where
    inventory replaces the interview, plus shorter treatments of the other three scenarios.

### Changed

- `README.md` and `docs/COMMANDS.md` point at the tutorial index rather than at a single
  walkthrough.

## [2.0.0] — 2026-08-08

A structural release. The workflow engine moved into the skill so the whole thing works
when installed by a skills registry, prompt filenames became the ids, and 13 prompts
closed gaps that could block a store submission.

### Breaking

- **Prompt filenames replace numeric prefixes.** `05b-domain-model.md` is now
  `domain-model.md`, `27-secure-backend-integration.md` is `secure-backend.md`, and so on
  for all 38 existing prompts. The numbering had already collided — two `00`s, a `00c`
  with no `00a`, and a `05` and `05b` in different phases — and it never ordered anything,
  since the order lives in `prompts/README.md` and in `BUILD-PLAN.md`. An existing
  `docs/BUILD-PLAN.md` referring to numbers must be regenerated with the `plan` phase.
- **`init` no longer copies the prompt library into the project.** Prompts are read from
  the installed skill, so a fix reaches every project at once. A project that needs its own
  rules writes `docs/mobilekit-overrides.md`, read after `prompts/RULES.md` and winning on
  conflict. An existing `mobilekit/` directory in a project can be deleted.
- **The workflow engine moved from `commands/` to `workflow/`.** Slash commands are now
  three-line aliases. This was a correctness fix: skills registries install `SKILL.md` and
  its directory but not a host's command directory, so the `BUILD-PLAN` format, the secret
  leak sweep and the `status` drift check were unreachable for anyone who installed the
  skill rather than cloning it.
- **`prompts/RULES.md` is the single source of truth for prompt behaviour.** The three
  rules previously duplicated across `SKILL.md`, `AGENTS.md` and `README.md` now live in
  one place and are pointed at.

### Added

- **`native-permissions.md`** — every OS permission the app asks for, with all three
  denial paths including permanently-denied and its route to the settings screen. It was
  previously improvised inline by three separate prompts.
- **`media-upload.md`** — camera and library capture, compression, EXIF handling, signed
  uploads, the pending state in the domain, and orphan cleanup. Discovery had asked about
  media since the first version and no prompt answered.
- **`content-moderation.md`** — report, block, review queue and the developer contact
  route. An app with user-generated content and none of these is rejected by store review.
- **`store-compliance.md`** — privacy manifest and required-reason APIs, data-safety
  declarations, tracking permission, policy URL, reviewer account, age rating, listing
  assets. `eas-build.md` produced a binary; this is what decides whether it is accepted.
- **`privacy-consent.md`** — GDPR/LGPD consent, deferred SDK initialization, withdrawal
  that actually stops collection. Ordered **before** `analytics.md`: an SDK that collects
  on launch has already collected before any consent screen appears.
- **`api-integration.md`** — an API you do not own, across OpenAPI, undocumented REST and
  GraphQL, with the auth, pagination, error-taxonomy and environment questions.
- **`account-recovery.md`** — password reset, credential and email changes. Both auth
  prompts assumed these screens existed and neither built them.
- **`biometric-lock.md`** — Face ID and fingerprint as a local gate over an existing
  session, with the mandatory fallback and the enrollment-changed case.
- **`performance.md`** — startup, lists, images, re-renders and bundle, measured on a
  low-end device before and after each fix.
- **`ci-cd.md`** — what runs per pull request, per merge and per release tag, and where
  store credentials live.
- **`release-rollback.md`** — the levers when a release goes bad, ordered by reach, and
  prepared before they are needed rather than improvised during an incident.
- **`sdk-upgrade.md`** — one major at a time, verified between each.
- **`legacy-modernization.md`** — a second entry point, for an app that already ships.
  Inventory replaces the interview, across four starting points: bare React Native behind,
  Expo behind, hybrid Cordova/Ionic/WebView, and native Swift/Kotlin adopting React Native
  incrementally.
- **`docs/COMMANDS.md`** — a reference for every command: what it reads, what it refuses,
  what it produces.
- `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE`.

### Changed

- **Every prompt grills one question at a time.** `### Ask first` is now `### Grill`, and
  `prompts/RULES.md` §1 makes the conduct binding: one question per message with a
  recommended answer, facts looked up rather than asked, decisions put to the developer.
  Previously only discovery and design carried that rule and the other 31 prompts listed
  their questions, which an agent reads as permission to ask all of them at once.
- **Documentation is requested rather than assumed.** `prompts/RULES.md` §3 replaces the
  ten references to a specific documentation MCP server with a cascade: read the installed
  version, use a docs tool if the agent has one, otherwise ask the developer — with
  `docs/vendor/<lib>@<version>.md` as the place an answer is kept so the ask happens once.
  Proceeding from memory is allowed only with the unverified steps named in the report.
- `ship` now includes the performance pass, the consent check, store compliance and the
  Expo project doctor.
- `install.sh` reads the skill name from `SKILL.md` frontmatter instead of the directory
  name, so cloning the repo under its GitHub name still produces `/mobilekit:*`. It also
  links Antigravity and Cursor.
- `SKILL.md` frontmatter carries `license` and `metadata.version`.

### Removed

- `agents/openai.yaml` — three lines, referenced by nothing.

## [1.0.0]

Initial release: 38 prompts across eight phases, eight slash commands, `install.sh` for
Claude Code and Codex.
