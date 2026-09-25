# Settings Screen

App preferences. Skip this screen if `profile-screen.md` already hosts them — two screens of settings is worse than one.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Build the Settings screen.

### Grill

**Only include a setting that changes real behavior.** A toggle wired to nothing is a bug with a nice UI. For each candidate, confirm it applies:

- Theme (light / dark / system) — only if dark mode is built or being built (`dark-mode.md`)
- Display language — only if i18n is in scope; `PRODUCT.md` records this
- Notification preferences — only if notifications exist, and the toggle must reach the real permission and subscription state, not just a local boolean
- Biometric lock — only if `biometric-lock.md` is built; it places its toggle, timeout, and fallback change here
- Analytics / crash-reporting opt-out — only if those SDKs are installed. If a privacy policy or regional law promises an opt-out, the toggle must actually stop collection
- Clear cache — only if there is a cache whose clearing helps
- Data export or account deletion — deletion is required for App Store apps with accounts; place it here or on Profile, not both

Also ask: which of these are per-device and which follow the account to another device? That decides local storage vs. server.

### Build

- Sectioned rows with headers, using the common components from `ui-components.md`
- Toggles that write to the persisted store **and** call through to the underlying system — permission request, SDK opt-out, theme application. Verify the effect, not the switch position
- One row per OS permission the app requests, showing its current state with a route into OS settings, re-read when the app returns to the foreground. `native-permissions.md` owns the state module; this screen is where a user discovers why a feature is dark
- Destructive rows visually distinct and confirmed before acting
- About section: version and build number read from the app config, not hard-coded. Include licenses if any dependency requires attribution
- Every setting applies immediately. A setting that needs a restart to take effect must say so

### Done when

- [ ] Every toggle produces an observable effect, verified one by one
- [ ] Preferences survive a restart, and account-level ones follow the account
- [ ] An opt-out toggle actually stops the collection it claims to stop
- [ ] Destructive actions confirm first
- [ ] A permission changed in OS settings is reflected in its row after returning to the app, without a restart
- [ ] No setting present that nothing consumes
