# Biometric App Lock

Only if `docs/PRODUCT.md` justifies it: money, health records, private messages, corporate data. On a to-do list an app lock is friction with a fingerprint icon — skip it and say so.

Prereqs: authentication already working (`auth-clerk.md` or `auth-backend.md`), and a physical device — simulators enrol fake biometrics and prove nothing about the real failure paths.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DESIGN.md` and AGENTS.md first.

Add a biometric lock in front of [the app / the screens named in `PRODUCT.md`].

### The distinction this prompt exists for

Biometrics are a **local gate in front of an already-authenticated session**, not an authentication method. The server never learns that a fingerprint matched. A successful scan only unlocks a credential the device already holds; a failed scan leaves that credential encrypted. Nothing about the lock changes who the API thinks the caller is.

An agent that treats Face ID as a login has built a bypass: any path that skips the scan still has a valid session behind it. If a scan is the only thing standing between a user and someone else's data, the design is wrong — the session, not the sensor, is what must be scoped.

Consult the biometrics and secure-storage APIs for the installed versions before writing setup (`RULES.md §3`).

### Grill

- **What exactly is behind the lock?** **A** the whole app on foreground — **B** one action, such as confirming a payment or revealing a recovery code — **C** both, with different re-arm rules. Recommended default: A for anything holding a balance or a medical record, because a locked screen inside an unlocked app leaks the surrounding list; B alone only when a single action carries the risk.
- **When does it re-arm?** **A** every time the app foregrounds — **B** after a background timeout — **C** cold start only. Recommended default: B with a short timeout, because A punishes anyone who switches out to read an SMS code, and C leaves the app open all day on a lost phone.
- **Opt-in or mandatory?** Recommended default: opt-in from the settings screen, off by default, unless a compliance requirement in `PRODUCT.md` says otherwise — a mandatory lock on first launch loses users who have no enrolled biometric.
- What happens on repeated failure — unlimited retries, or a cooldown after N attempts? Say what the user sees.
- Does anything need to stay visible while locked — a scan-to-pay code, an emergency contact, a support number?

### Build

**The gate**

- One place decides locked vs unlocked, read by the gate `app-shell.md` built in the root layout. A per-screen check gets forgotten on the screen added next month
- Re-arm from real app-state transitions, and record the time the app left the foreground — a timer that only runs while the app is alive never fires
- **A mandatory PIN or passcode fallback.** Biometrics fail on wet hands, a changed face, a cracked sensor, and every device with nothing enrolled. A lock with no fallback locks the user out of their own data, and the only remaining fix is a reinstall that also destroys local state
- Device with no biometric hardware or nothing enrolled: fall back to the passcode, or leave the feature unavailable and say why in settings. Never show a scan prompt that cannot succeed
- **Enrolment changes invalidate the stored secret.** A new fingerprint added to the device must break the unlock, otherwise a second person's finger opens the app. Bind the secret to the current enrolment set and treat invalidation as an expected event: fall back to the passcode and re-arm the lock, not a crash

**Where the secret lives**

- The unlock credential goes in device secure storage, encrypted and bound to biometrics, so the scan is what makes it readable
- **Never a boolean.** `lockEnabled: true` in `AsyncStorage` is flipped by anyone who can read the store, and the gate opens with no scan at all
- Nothing sensitive is decrypted or fetched before the gate passes. Rendering the real screen under a covering overlay means the data is already in memory and already on screen for one frame

**The lock screen**

- Must not leak what it protects: obscure the app-switcher and screenshot preview on both platforms, and check the result by actually opening the switcher
- Decide whether notification previews may show balances or message content while locked — that is a `PRODUCT.md` decision, not a default
- One clear action to scan, one to use the fallback, one to sign out. A locked user with no way out reinstalls

**Interactions**

- A deep link arriving at a locked app must survive the unlock and resume at its destination, not drop the user on the home screen (`deep-linking.md`)
- Sign-out clears the stored secret and the lock preference. A stale secret left behind belongs to the previous account
- Expose the toggle, the timeout, and the fallback change in `settings-screen.md`, with copy that says what the lock does and does not protect

### Done when

- [ ] Unlock succeeds with a valid biometric and fails with an invalid one, on a physical iOS and Android device
- [ ] The passcode fallback is reachable from the lock screen and unlocks the app
- [ ] A device with no enrolled biometric can still install, sign in, and use the app
- [ ] Enrolling a new biometric on the device invalidates the stored secret and forces the fallback
- [ ] The app-switcher preview and a screenshot show no protected content while locked
- [ ] A deep link opened while locked lands on its intended screen after unlock
- [ ] Signing out and back in with a different account leaves no unlock secret from the first
