# PostHog Analytics

Event tracking, feature flags, A/B tests. Skip if `PRODUCT.md` marks analytics "later" or "never".

Prereq: a PostHog project and API key. **`privacy-consent.md` runs first** for any app shipping to the EU or Brazil — it owns the gate this SDK initializes behind; nothing below fires before consent resolves.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Add PostHog to this app.

**Check the installed `posthog-react-native` version and follow its docs** (RULES.md §3 · canonical: https://posthog.com/docs/libraries/react-native). Whether the provider takes an API key directly or a pre-constructed client, and how autocapture is configured, differ across versions — do not paste initialization from memory.

### Grill — what is worth measuring?

An event list copied from a template produces dashboards nobody reads. Derive it instead:

- What is the **success action** in `PRODUCT.md`? That is the one event that must exist.
- What are the 2–3 steps immediately before it? Those are the funnel — `DESIGN.md`'s Activation path, if recorded, names them in order.
- Which drop-off do you actually suspect? Instrument that, and add an abandonment event where the user leaves before succeeding.
- A/B tests: is there a real decision waiting on data? If not, skip them — an unused experiment is dead code.
- Feature flags: **the kill switch is not speculative.** `release-rollback.md` counts on a remote flag as the only lever that reaches an already-installed native build immediately. Ask which shipped features would be turned off in an incident — payments, uploads, AI calls are the usual candidates — and wrap those. Flags beyond the kill switches need a real decision waiting on them.

Present the proposed event list with properties and get approval. Cap it: **5–8 events to start.**

### Build

- Install and initialize once; key via `EXPO_PUBLIC_POSTHOG_API_KEY`, host via env if self-hosted
- Wrap the app with the provider in the root layout, and never re-initialize elsewhere
- Identify the user after authentication resolves, using the auth provider's stable user id. Set changing traits on identify; set immutable ones (signup date) once
- Reset on sign-out, or the next user on that device inherits the previous identity
- Capture the approved events at the moments named in the list. `snake_case`, past tense, consistent property names across events
- Duration metrics: capture the start timestamp in a ref on mount so the value is real rather than re-rendered
- **No PII in properties.** No email, no free-text user input, no auth tokens
- Screen-view tracking: prefer the library's automatic navigation integration over a manual call per screen
- Kill-switch flags evaluated at the feature's entry point, each with a hard-coded safe default for when the flag service is unreachable — a kill switch that fails open is not a switch. Flag names documented next to the event list

### Done when

- [ ] Events appear in PostHog from a device, with the expected properties
- [ ] The success-action funnel is visible end to end
- [ ] Identify fires once after auth; sign-out resets
- [ ] No UI changed, no PII sent, no keys hard-coded
- [ ] Event list documented so the next event follows the same naming
- [ ] Each kill-switch flag flipped in the dashboard disables its feature on a device without a new build; with the flag service unreachable, the feature sits on its safe default
