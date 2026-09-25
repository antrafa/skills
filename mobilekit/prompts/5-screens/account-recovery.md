# Account Recovery & Credential Changes

Run this whenever the app has passwords. Skip it entirely if sign-in is OAuth-only, passkey-only, or magic-link-only — there is no credential to recover.

`auth-clerk.md` and `auth-backend.md` both assume these screens exist and neither builds them. Ship without them and the first support ticket is "I can't get back in", with no in-app path to fix it.

Prereqs: auth is working (`auth-clerk.md` or `auth-backend.md`), `deep-linking.md` for the link back into the app, and a real device with a real mailbox for verification.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DESIGN.md` and AGENTS.md first.

Build the account recovery and credential-change flows.

### Grill

- **Forgot password: link or code?** **A** — emailed link that opens the app via `deep-linking.md`; fewest taps, but needs universal links working on both platforms. **B** — 6-digit code typed into the app; works even when the link opens the wrong browser. **C** — both. Recommended default: **B**, because a code has no way to fail on a device with no association file, and it can be upgraded to a link later.
- **After a successful reset, are the user's other sessions invalidated?** Recommended default: yes — the reason a person resets a password is that someone else may have it, and leaving the attacker's session alive defeats the reset. Signing the user out of their tablet is the cost.
- **Change password while signed in — required, or is reset-by-email enough?** Recommended default: required, and it demands the current password. Without that, a stolen unlocked phone is a permanent account takeover, not a lost phone.
- **Change email — in scope?** If email is the login identifier, changing it is changing the account, and the flow needs verification of the new address plus notification of the old. If it is only a contact field, say so in `PRODUCT.md` and it stays a plain form field.
- **Does the app use phone sign-in?** If yes, phone change and re-verify are the same flow shape as email and need building; if no, skip them.
- **Who owns rate limiting on the request endpoints?** Managed provider (Clerk, Supabase Auth) has it; a custom backend does not until you write it, and that is `secure-backend.md` work, not a screen concern.

### Build

**Forgot password**

- Request screen reachable from the sign-in screen without signing in — an entry point behind the login wall is useless to the person who is locked out
- The confirmation message reveals nothing: "if that address is registered, a link is on its way". "No account with that email" is an account-enumeration oracle — anyone can test a list of addresses against it. Same copy, same timing, whether or not the address exists
- The link or code arrives back into the app via `deep-linking.md` — do not build a second URL handler here
- New-password screen: the same strength rules as sign-up, a reveal toggle, and confirmation only after the server accepts. Then apply the session decision from the Grill
- **Expired or already-used token gets its own screen** with a "request a new link" action. This is the state everyone forgets, and its default is a blank screen or a raw provider error

**Change password (signed in)**

- Current password, new password, confirm. Wrong current password is an inline field error, not a toast
- Notify the account by email that the password changed, so an unauthorized change is visible

**Change email**

- Verification goes to the **new** address; the account is not moved until that address is confirmed. Meanwhile the old address stays the login identifier
- Notify the old address that a change was requested, with a way to object. An unnoticed email change is how accounts are silently stolen — the attacker owns the reset path from that moment on
- Show the pending state in the UI, and allow cancelling it

**Phone change / re-verify** — only if the app uses phone sign-in. Same shape: verify the new number before it replaces the old one.

**Credential change and the rest of the app**

- Queued offline writes (`offline.md`) and cached sessions hold tokens that a credential change may have just invalidated. Decide whether the queue is flushed before the change, retried against the new session, or dropped — a queue that retries with a dead token silently loses the user's work
- Clear any cached identity that no longer matches: biometric-unlock state, stored email, analytics identity

**Entry points** — forgot-password from the sign-in screen; change password, change email and change phone as rows in `profile-screen.md` or `settings-screen.md`. A flow that is implemented but unreachable is not shipped.

### Done when

- [ ] Full reset completed end to end on a device from a real email, including the expired-link path reaching its own screen
- [ ] The request confirmation is identical for a registered and an unregistered address
- [ ] Email change requires confirming the new address, and the old address receives a notification
- [ ] Password change rejects a wrong current password with an inline error
- [ ] After a reset with session invalidation on, a second signed-in device is signed out
- [ ] Repeated reset requests for one address are throttled
- [ ] Every entry point is reachable by tapping through the UI, with no deep link typed by hand
