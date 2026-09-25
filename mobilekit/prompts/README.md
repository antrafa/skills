# mobilekit — prompt library

59 prompts for building production-quality React Native apps with Expo, organized by phase. Drive them with the [phases](../workflow/) — or paste one by hand.

Folders are the phase order. **Filenames are the ids**: a prompt keeps its name wherever it moves, so `BUILD-PLAN.md` entries and cross-references between prompts survive reorganization.

---

## How to use

1. Read [**RULES.md**](./RULES.md) once yourself. It is short, and every prompt starts by reading it. It exists because the common failure is not bad code — it is an assistant deciding something you never chose.
2. **An app that already ships starts at [`9-maintain/legacy-modernization.md`](./9-maintain/legacy-modernization.md).** It inventories what exists and derives `PRODUCT.md` from it, instead of interviewing you about a product that is already live.
3. **A new app starts at [`1-discovery/product-discovery.md`](./1-discovery/product-discovery.md).** It writes `docs/PRODUCT.md`, which every other prompt reads instead of guessing what you are building.
4. Create `AGENTS.md` from `PRODUCT.md` with [`1-discovery/agents-md.md`](./1-discovery/agents-md.md).
5. Decide screens and navigation with [`2-design/design-conception.md`](./2-design/design-conception.md) → `docs/DESIGN.md`. Screens built before this get rewritten.
6. Define the domain with [`3-foundation/domain-model.md`](./3-foundation/domain-model.md) → `docs/DOMAIN.md`.
7. Then follow the build order below, or pick individual prompts for an existing project.

Outputs live in the project's `docs/` — `PRODUCT.md`, `DESIGN.md`, `DOMAIN.md`, `BUILD-PLAN.md`, and `MODERNIZATION.md` for a legacy app. The library lives here. They are deliberately separate: the outputs are documentation someone reads without knowing this skill exists.

Where a prompt offers a menu ("Option A / B / C"), that is a question for you, not a choice for the assistant to make silently.

---

## Index

### `1-discovery` — what are we building
| Prompt | Description |
|---|---|
| [Rules](./RULES.md) | Read before every prompt: grill one question at a time, request docs, invent nothing |
| [product-discovery](./1-discovery/product-discovery.md) | **Start here for a new app.** Interview that defines the product → `docs/PRODUCT.md` |
| [monetization](./1-discovery/monetization.md) | Concept round: how the app earns — model, free/paid boundary, trial → `PRODUCT.md §Monetization` |
| [market-signal](./1-discovery/market-signal.md) | Optional, recurring: the product in front of real people at each phase boundary → `docs/LAUNCHES.md` |
| [agents-md](./1-discovery/agents-md.md) | Build a project-specific AGENTS.md from `PRODUCT.md` |

### `2-design` — what does it look like
| Prompt | Description |
|---|---|
| [design-conception](./2-design/design-conception.md) | Screen inventory, navigation shape, per-screen states → `docs/DESIGN.md` |
| [design-system](./2-design/design-system.md) | Color, type, spacing, radius, elevation — centralized as tokens |

### `3-foundation` — the base everything sits on
| Prompt | Description |
|---|---|
| [expo-setup](./3-foundation/expo-setup.md) | Initialize Expo with TypeScript and Router |
| [dev-environment](./3-foundation/dev-environment.md) | Dev build vs Expo Go, devices, env per environment, repo hygiene |
| [nativewind](./3-foundation/nativewind.md) | Install and configure NativeWind (Tailwind CSS) |
| [domain-model](./3-foundation/domain-model.md) | Entities, schema or existing-table mapping, types, fixtures |
| [ui-components](./3-foundation/ui-components.md) | Only the shared set `DESIGN.md` identified — nothing speculative |
| [app-shell](./3-foundation/app-shell.md) | Root layout, boot sequence, splash gating, app-wide error boundary |

### `4-platform` — auth, data, and the server side
| Prompt | Description |
|---|---|
| [auth-clerk](./4-platform/auth-clerk.md) | Managed authentication |
| [auth-backend](./4-platform/auth-backend.md) | Supabase Auth or your own API |
| [biometric-lock](./4-platform/biometric-lock.md) | Face ID / fingerprint as a local gate, with a mandatory fallback |
| [native-permissions](./4-platform/native-permissions.md) | Every OS permission the app asks for, and all three denial paths |
| [supabase](./4-platform/supabase.md) | Database, auth, and storage |
| [api-integration](./4-platform/api-integration.md) | An API you do not own: OpenAPI, undocumented REST, or GraphQL |
| [zustand](./4-platform/zustand.md) | Global state with persistence |
| [react-query](./4-platform/react-query.md) | Data fetching with TanStack Query |
| [secure-backend](./4-platform/secure-backend.md) | API routes, token generation, keeping secrets out of the bundle |

### `5-screens` — the app itself
| Prompt | Description |
|---|---|
| [onboarding](./5-screens/onboarding.md) | Welcome / intro experience |
| [tab-navigation](./5-screens/tab-navigation.md) | Bottom tab bar |
| [home-screen](./5-screens/home-screen.md) | Main dashboard / feed |
| [list-screen](./5-screens/list-screen.md) | Lists with search and filtering |
| [detail-screen](./5-screens/detail-screen.md) | Item detail view |
| [form-screens](./5-screens/form-screens.md) | Create / edit forms |
| [modals-sheets](./5-screens/modals-sheets.md) | Reusable modals and bottom sheets |
| [profile-screen](./5-screens/profile-screen.md) | User profile and account |
| [settings-screen](./5-screens/settings-screen.md) | App preferences and configuration |
| [account-recovery](./5-screens/account-recovery.md) | Password reset, credential and email changes |

### `6-features` — capabilities, only if `PRODUCT.md` marks them "now"
| Prompt | Description |
|---|---|
| [push-notifications](./6-features/push-notifications.md) | Local and remote notifications |
| [deep-linking](./6-features/deep-linking.md) | Custom schemes, universal links, protected destinations |
| [media-upload](./6-features/media-upload.md) | Camera, library, compression, signed uploads |
| [content-moderation](./6-features/content-moderation.md) | Report, block, review — required for user-generated content |
| [animations](./6-features/animations.md) | Motion that clarifies state changes |
| [dark-mode](./6-features/dark-mode.md) | Light/dark theme support |
| [i18n](./6-features/i18n.md) | Multiple languages, locale formatting, RTL |
| [offline](./6-features/offline.md) | Cached reads, queued writes, honest degradation |
| [ai-features](./6-features/ai-features.md) | Text, streaming, and realtime voice/video — via your own server |
| [in-app-purchases](./6-features/in-app-purchases.md) | Store billing for digital content, subscriptions, and consumable credits |
| [payments](./6-features/payments.md) | Stripe, for physical goods and services |
| [ads](./6-features/ads.md) | AdMob behind the consent chain — formats, placement, kids categories |

### `7-ship` — the release gate
| Prompt | Description |
|---|---|
| [testing](./7-ship/testing.md) | Risk-driven test scope, from domain logic to one E2E path |
| [accessibility](./7-ship/accessibility.md) | Cross-app sweep before first submission |
| [performance](./7-ship/performance.md) | Startup, lists, images, re-renders — measured on a low-end device |
| [security-review](./7-ship/security-review.md) | Adversarial sweep: re-test ticked checks, the joints between features, storage, logs |
| [store-compliance](./7-ship/store-compliance.md) | Privacy declarations, reviewer access, listing — what rejects builds |
| [ci-cd](./7-ship/ci-cd.md) | What runs on every PR, on merge, and on a release tag |
| [eas-build](./7-ship/eas-build.md) | Build, environment variables, store submission, OTA updates |
| [beta-and-review](./7-ship/beta-and-review.md) | TestFlight / Play tracks, exit criteria, and the store rejection loop |

### `8-observability` — knowing what happens after
| Prompt | Description |
|---|---|
| [privacy-consent](./8-observability/privacy-consent.md) | **Runs before analytics.** GDPR / LGPD consent, deferred SDK init, withdrawal |
| [analytics](./8-observability/analytics.md) | Event tracking, feature flags, and A/B testing |
| [error-tracking](./8-observability/error-tracking.md) | Crash and error reporting with readable stack traces |
| [post-release](./8-observability/post-release.md) | The four numbers you watch once real users are in it |
| [next-feature](./8-observability/next-feature.md) | The plan ran out: turn the four numbers into the next cycle of `BUILD-PLAN.md` |
| [release-rollback](./8-observability/release-rollback.md) | The levers when a release goes bad, prepared before it does |

### `9-maintain` — keeping it alive
| Prompt | Description |
|---|---|
| [legacy-modernization](./9-maintain/legacy-modernization.md) | **Entry point for an app that already ships.** Inventory, parity list, migration path |
| [sdk-upgrade](./9-maintain/sdk-upgrade.md) | One major at a time, verified between each |

---

## Suggested build order (new project)

```
product-discovery   → docs/PRODUCT.md          (nothing runs before this)
monetization        → PRODUCT.md §Monetization (only if the app earns money — model and boundary)
agents-md           → AGENTS.md from PRODUCT.md
design-conception   → docs/DESIGN.md           (before any screen)
expo-setup
dev-environment                                (dev build vs Expo Go, devices, env files)
nativewind
design-system
domain-model        → docs/DOMAIN.md           (before any screen)
ui-components                                  (only the shared list from DESIGN.md)
app-shell                                      (root layout and boot sequence — before any screen or auth)
onboarding
auth-clerk | auth-backend                      (skip if PRODUCT.md says no accounts)
supabase | api-integration                     (whichever backend applies)
zustand
react-query                                    (if data comes from a remote source)
tab-navigation
home-screen
list-screen
detail-screen
form-screens                                   (if users create data)
modals-sheets
profile-screen
settings-screen
deep-linking                                   (routes exist now; account-recovery, push, payments and OAuth need it)
account-recovery                               (if the app has passwords)
native-permissions                             (before any feature that asks for one)
secure-backend                                 (before any service with a secret — signed uploads included)
media-upload                                   (if the app handles photos, video or audio)
content-moderation                             (if users publish anything others see)
animations
dark-mode
i18n                                           (if multiple languages)
ai-features                                    (if AI is in scope)
in-app-purchases | payments | ads              (the ones PRODUCT.md §Monetization selects)
privacy-consent                                (before any analytics SDK initializes)
analytics
error-tracking
push-notifications
biometric-lock                                 (if the data justifies it)
offline                                        (if required)
testing                                        (earlier if the app handles money or auth)
accessibility                                  (before first submission)
performance
security-review                                (the joints, the storage dump, the red audit)
store-compliance                               (before first submission)
ci-cd                                          (once more than one person commits)
eas-build
release-rollback                               (prepared before the first release — beta executes its staged rollout)
beta-and-review                                (testers before the public; the rejection loop)
post-release                                   (after real users, not before)
next-feature                                   (when the plan is empty — the four numbers pick the next cycle)
sdk-upgrade                                    (every SDK cycle, forever)
```

The [`plan`](../workflow/plan.md) phase generates this list cut down to only the steps your `PRODUCT.md` and `DESIGN.md` justify. Every step whose capability is marked "later" or "never" is skipped.

---

## Customization

- **Replace placeholders**: `[bracketed text]` is yours to fill — or let `PRODUCT.md` answer it
- **Never let the assistant guess the domain**: a decision marked `UNDECIDED` gets asked, not invented
- **Attach designs**: where a prompt says "attach design", provide the Figma export or screenshot
- **Skip what you don't need**: not every app needs payments or push notifications
- **Override the rules per project**: `docs/mobilekit-overrides.md` is read after `RULES.md` and wins on conflict
- **Extend**: see [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Stack covered

Expo · React Native · TypeScript · Expo Router · NativeWind · Zustand + AsyncStorage · Clerk / Supabase / custom auth · Supabase · OpenAPI / REST / GraphQL clients · TanStack Query · PostHog · Sentry · Expo Notifications · Reanimated · RevenueCat · Stripe · AdMob · Expo API Routes for anything holding a secret · provider-agnostic AI, always proxied server-side · EAS Build + EAS Update.

Cross-cutting concerns with their own prompts: permissions, media, moderation, i18n, offline, deep linking, biometrics, testing, performance, accessibility, consent, store compliance, CI/CD, rollback, post-release observability, SDK upgrades.

**Not covered.** The library is opinionated about a segment: content, productivity and SaaS-style apps. It has no prompts for maps and geofencing, Bluetooth, health platforms, media streaming, cart-based commerce, or widgets and Live Activities. It also does not build a standalone backend: the assumed shapes are a managed backend (`supabase`), Expo API Routes for anything holding a secret (`secure-backend`), or an API that already exists (`api-integration`) — a custom server's architecture, deployment and monitoring need a toolkit of their own, and here it is treated as an API the app consumes. Those verticals need prompts of their own — the shape to write them in is in [CONTRIBUTING.md](../CONTRIBUTING.md).
