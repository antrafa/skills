# Native Permissions

Run this once, before the first feature that touches the camera, photo library, microphone, location, contacts, calendar, or notifications. It owns permissions for the whole app so `push-notifications.md`, `media-upload.md`, `ai-features.md` and any location feature inherit one flow instead of inventing three.

Skipped, each feature ships its own prompt at its own moment, and the app collects denials it can never undo — **a denied iOS permission cannot be re-prompted; only the OS Settings app can reverse it.**

Prereqs: physical device (simulators lie about camera, microphone and location); a development build — permission dialogs in Expo Go carry Expo Go's own usage strings, not yours.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DESIGN.md` and AGENTS.md first.

Establish the app's permission inventory, request timing, and denial handling.

### Grill

- **Which permissions does `PRODUCT.md` actually justify?** List each one against the capability that needs it. A permission with no feature behind it is a prompt the user denies for nothing — and on iOS that denial poisons the feature you add later. Anything traced to a capability marked "later" or "never" is not declared now.
- **For each permission, what is the exact user action that triggers the request?** "Taps *Add photo*", "taps *Use my location*". If there is no such moment, the permission is requested on launch, and that is the design being ruled out here.
- **Does a pre-permission explainer screen earn its place?** Recommended default: only where the reason is not visible from the action itself — background location, contacts, microphone. For a camera prompt fired by a camera button, the explainer is a tax on the obvious.
- **Is a reduced grant enough?** iOS offers limited photo-library access, approximate location, and provisional notifications; Android offers coarse location. **A / B:** ask for the reduced grant and work within it, or ask for full access and justify it. Recommended default: reduced, because it is granted more often and never blocks review — escalate only where the feature is genuinely impossible without full access.
- **What does each feature do with the permission denied?** Every one needs a real answer: manual address entry instead of location, file picker instead of camera, in-app inbox instead of push. "Feature unavailable" is an answer only if the developer chose it.
- **Does any of these need extra store justification?** Background location, "always" location, full photo library, contacts, and microphone draw review questions and, on Android, a Play Console declaration. Confirm with `store-compliance.md` before shipping.

### Build

**Inventory and configuration**

- One table in `docs/PRODUCT.md` or the permissions module: permission → feature → trigger → behaviour when denied. This is the artefact; the code follows it
- iOS usage-description strings in the app config for **every** permission the build can reach, written for the person reading the dialog: what the app does with it, in their words. "This app needs camera access" is vague enough to be rejected, and App Store review reads these strings
- Android: distinguish manifest declarations from runtime requests. Declaring a dangerous permission in the manifest without ever requesting it at runtime silently fails at the call site; declaring one no feature uses is a Play Console question
- Strip permissions Expo config plugins add by default that no feature uses — audit what the built manifest and `Info.plist` actually contain, not what the config file says
- If the app is localised, usage strings are localised too (`i18n.md`)

**Timing**

- Request at the moment of use, after the user has acted. Never during onboarding, never on first launch, never speculatively at login
- One prompt per user action. Never chain two OS dialogs back to back — the second reads as a malfunction and gets dismissed
- Provisional notification authorisation, where chosen, is granted without a dialog; the upgrade to full authorisation is requested only after the user has engaged with a delivered notification

**The three states**

- **Granted** — proceed, and re-check on every use rather than caching a boolean across app launches. The user can revoke in Settings while the app is backgrounded
- **Denied** — the feature's fallback path, stated plainly, with a way to retry. On Android a first denial can be re-requested; on iOS it cannot, so the retry affordance must lead to Settings
- **Blocked / permanently denied** — deep link to the OS settings screen for this app, and re-check permission state when the app returns to the foreground so the screen updates without a manual refresh. A "Go to Settings" button that leaves the user staring at a stale denied state is the common bug here
- Partial grants are their own state, not a denial: limited photo access shows the picker and an "add more photos" affordance; approximate location skips the features needing precision instead of erroring

**Central ownership**

- One module owns permission state and exposes check, request, and open-settings per permission. Screens read it; no screen calls the OS permission API directly, or timing and denial handling drift per screen
- Foreground re-check on app resume, so state changed in Settings is reflected
- `settings-screen.md` surfaces the current state of each permission with a route into OS settings — the only place a user can discover why a feature is dark

### Done when

- [ ] Every declared permission traces to a feature in `PRODUCT.md`, and the built `Info.plist` and Android manifest contain nothing else
- [ ] Each usage string names what the app does with the data and reads as a sentence, not a placeholder
- [ ] Denying every permission on a fresh install leaves the app fully usable, with no crash, dead screen, or empty state that lies
- [ ] The permanently-denied path walked on both platforms: deep link opens Settings, granting there and returning updates the UI without a restart
- [ ] Reduced grants exercised on a device — limited photo selection and approximate location each produce working behaviour, not an error
- [ ] No permission dialog appears before the user has taken an action that explains it
- [ ] Revoking a granted permission in Settings mid-session degrades the feature instead of crashing it
