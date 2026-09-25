# App Shell & Boot Sequence

The root layout is the most contested file in the app: auth wants to route on session state, onboarding wants first-launch detection, the store wants hydration, the biometric lock wants to cover everything. Run this once, after `ui-components.md` and before any screen or auth prompt, so each of those plugs into a gate that already exists instead of fighting for the file.

Skip only if the root layout already has a deliberate owner — read it before assuming it does.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DESIGN.md` and AGENTS.md first.

Build the app shell: root layout, boot sequence, and the app-wide error boundary.

### Grill

- **What must resolve before the first screen shows?** Fonts, store hydration, a stored session, onboarding-seen — and the stored consent decision, where `privacy-consent.md` will apply. List it from what is actually installed and planned, then confirm. Everything on the list resolves behind the splash screen, in one place; everything off it loads after first render.
- **What are the cold-start destinations?** `DESIGN.md` records them — new user → ?, signed-out → ?, signed-in → ?. If it does not, ask and write the answers back to it.
- **Route groups?** Recommended default: `(auth)` and `(app)`, plus `(onboarding)` where that flow exists — the redirect then lives in one layout per group instead of one check per screen.
- **What does the user see when boot fails** — a corrupted store, a hydration error? Recommended default: a plain-language screen with a retry, never a splash that hangs forever.

### Build

**Splash gating** — keep the splash visible until everything on the boot list resolves, then hide it once. Two failure modes to rule out on a device: the flash of the wrong screen (splash hidden before the session resolved), and the splash that never hides (a boot step that can fail must settle the gate anyway).

**Routing on state** — the root layout reads session and onboarding state and redirects between groups. No screen checks "am I signed in" itself. Later prompts — `auth-clerk.md`, `auth-backend.md`, `onboarding.md`, `biometric-lock.md` — plug their state into this gate rather than adding a second one.

**Error boundary** — at the root, above navigation: a plain-language fallback with a retry action, and the single point where `error-tracking.md` will later report. A render error with no boundary is a white screen with no exit.

**Deep links land through the gate** — a link into a protected route while signed out goes to auth and survives it; the destination is not eaten. `deep-linking.md` builds the full matrix later; the shell only guarantees the gate is transparent to it.

### Done when

- [ ] Cold start on a device: first-run, signed-out, and signed-in each land on the destination `DESIGN.md` names, with no flash of another screen in between
- [ ] The splash hides exactly once, and a deliberately failing boot step reaches the failure screen instead of an eternal splash
- [ ] A thrown render error shows the fallback, and its retry works
- [ ] No screen outside the root layouts contains its own auth or onboarding redirect
