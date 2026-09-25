# Authentication with Your Own Backend

Use this instead of `auth-clerk.md` when auth is handled by Supabase Auth or your own API.

For the auth **UI**, run Step 1 of `auth-clerk.md` first — it is provider-agnostic.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Implement authentication against our own backend.

### Grill

- **Supabase Auth or a custom API?** Recommended: Supabase Auth if the app already uses Supabase — session refresh, email verification, and password reset are solved there, and hand-rolling them is where custom auth usually breaks.
- If custom API: what are the real endpoints, request/response shapes, and token lifetimes? Get the contract — do not assume `/api/auth/login`.
- Access and refresh tokens, or a single long-lived session?
- Which methods: password, email code, magic link, OAuth?
- Roles or permission levels (`PRODUCT.md`, Block E)?

### Build

**Session state** — one auth context or store exposing `user`, `isLoading`, `isAuthenticated`, and `signUp` / `signIn` / `signOut` / `getToken`. Requirements that are easy to skip and expensive to add later:

- Tokens in `expo-secure-store`, never in AsyncStorage — AsyncStorage is unencrypted
- Restore and validate the session on launch, with an explicit loading state so no screen flashes
- Refresh before expiry, and handle concurrent requests hitting an expired token without firing parallel refreshes
- On refresh failure: sign out cleanly and clear persisted state

**API layer** — one module with the auth calls, typed against the real contract from the questions above. Errors are returned as domain results, not thrown strings; the UI needs to tell "wrong password" from "network down".

**Supabase path** — use the client's auth methods and its auth-state subscription as the single source of truth rather than mirroring session state by hand. Configure secure session storage per the installed `@supabase/supabase-js` version's docs (see `supabase.md`).

**Routing** — plug `isAuthenticated` and `isLoading` into the gate `app-shell.md` built in the root layout; the session joins the boot list behind the splash. No second gate.

**Wire the existing UI** — connect the auth UI from `auth-clerk.md` Step 1: loading on submit, inline errors, verification submission, navigate on success. Do not change the designs.

### Done when

- [ ] Sign up, verify, sign in, sign out, relaunch-signed-in, and expired-token refresh all verified on a device
- [ ] Tokens are in secure storage; nothing sensitive is in AsyncStorage or logs
- [ ] A failed refresh signs the user out instead of leaving a half-authenticated app
- [ ] Every error path shows an actionable message
