# Sentry Error Tracking

Crash and error reporting. Skip if `PRODUCT.md` marks error tracking "later" or "never" — a prototype does not need it.

Prereq: a Sentry project and DSN. For any app shipping to the EU or Brazil, `privacy-consent.md` decides whether crash reporting may initialize before consent — it is the exception commonly argued for, not an exemption. Run it first.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Integrate Sentry for error and performance monitoring.

**Check the installed `@sentry/react-native` version and follow its docs** (RULES.md §3 · canonical: https://docs.sentry.io/platforms/react-native/). The API changed substantially at v8 — the old transaction API (`startTransaction` / `transaction.finish()`) was replaced by spans, and Expo integration moved to a config plugin. Do not paste either from memory. Prefer the official wizard for setup, then review what it changed.

### Grill

- Environments to separate (development, preview, production)?
- Sample rates: performance tracing at 100% is fine at low volume and expensive later. Confirm the intent.
- Should Sentry run in development? Default: off, so local noise stays out of the dashboard — but then verify the integration once against a real build before trusting it.
- Is any data in this app sensitive enough to require scrubbing beyond the defaults?

### Build

- Install and initialize as the installed version's docs specify, DSN via env
- Set `environment` and `release`/`dist` so an error can be traced to a build. Without these, production stack traces are unreadable
- **Upload source maps** as part of the build. This is the step most often skipped, and skipping it makes every production report useless minified noise
- Wrap the root component so render errors are captured
- Wire reporting into the error boundary `app-shell.md` built at the root — build it there if it does not exist yet, never as a second one. Its fallback stays plain-language with a retry; no stack trace reaches a user
- Set user context after auth (id only — not email, unless you have decided to send it) and clear it on sign-out
- For caught errors that do not crash: report with context, then show an actionable message. Never swallow silently
- Custom spans only around operations you actually intend to optimize, using the installed version's span API

### Done when

- [ ] A deliberately thrown error appears in Sentry from a release-configured build
- [ ] The stack trace is readable — source maps confirmed working
- [ ] The error boundary renders the fallback instead of a white screen
- [ ] User context set after login, cleared on logout, no PII beyond what was approved
- [ ] Users never see raw error text
