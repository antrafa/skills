# Zustand State Management

Global client state with persistence.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Set up Zustand for the state this app actually shares.

### Grill — what belongs in a global store?

Do not create a store with placeholder fields. Derive the fields from `PRODUCT.md`, then confirm:

- Which values are read by more than one screen and must survive a restart? (onboarding completed, chosen preference, local progress)
- Which are **server** data? Those belong in React Query (`react-query.md`), not here. A store that caches server responses is a second, staler cache.
- Which are UI-only? Those stay in component state — modal visibility and form drafts do not belong in a global store.
- Anything sensitive? Tokens go in `expo-secure-store`, never in a persisted AsyncStorage store.

State the resulting field list and wait for confirmation before writing the store.

### Build

- Install `zustand` and `@react-native-async-storage/async-storage`
- One store per domain concern rather than a single god store — split when two areas have nothing to do with each other
- Persist through the `persist` middleware with the AsyncStorage JSON adapter; check the installed Zustand major's docs for the current middleware and adapter names
- Persist selectively: exclude derived values and anything re-fetchable
- Typed state interfaces, actions named for intent (`selectX`, `completeX`), and a `reset` used by sign-out
- A `version` and migration function on the persisted store. Adding a field later without one leaves existing installs with stale shapes — cheap now, painful after release

**Hydration** — persisted state loads asynchronously. Add hydration to the boot list `app-shell.md` gates behind the splash, or the first render sees defaults and redirects a returning user to onboarding. Once, in that gate — not per screen.

**Dev affordance** — a way to clear persisted state while developing (a debug action or a screen button), visible only in development builds.

### Done when

- [ ] State survives a restart, and hydration causes no flash of the wrong route
- [ ] No server data and no tokens in the persisted store
- [ ] Every field traces to a need in `PRODUCT.md` — no speculative fields
- [ ] Sign-out clears everything user-specific
- [ ] Store has a version and a migration path
