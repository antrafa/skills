# Secure Backend Integration

The pattern for any third-party service that has a secret: AI providers, video/realtime SDKs, payment processors, email, signed storage, anything billed per call.

Run this **before** the prompt for the specific service. Every one of them fails the same way — the key ends up in the app.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Set up secure server-side integration for [service].

### The rule this prompt exists for

`RULES.md` §6, applied without exception: anything the provider calls a secret stays server-side. `EXPO_PUBLIC_*` is extracted from a published bundle in minutes, so a key that can spend money, read other users' data, or impersonate the service **never** goes in the app — no matter how convenient, and no matter that it "works in development".

### Grill

- **Where does server-side code run?** Expo API routes in this repo, an existing backend, or a separate service? Expo API routes require a server output target and real hosting — a static export has no routes. Confirm the deployment target before writing one.
- Which operations genuinely need the secret? Anything else can stay client-side.
- **Who is allowed to call this?** Almost always: an authenticated user, and only for their own data.
- Is the service billed per call or per minute? If yes, an unauthenticated route is an open tab on your account — quota and rate limiting are part of this step, not a follow-up.
- Does the client SDK need a **short-lived token** (common for realtime, video, chat) rather than proxied calls? Those are two different architectures; pick one deliberately.
- What should the app do when the service is down or slow?

### Build

**The route**

- Secrets in non-`EXPO_PUBLIC_` variables, available only to the server runtime
- **Authenticate every request.** Verify the caller's session server-side, then derive the user identity from that verification — never from a field in the request body
- Authorize the specific action: this user may act on this resource. A route that accepts a resource id without an ownership check is a data leak with a login screen in front of it
- Accept identifiers, not consequences. The client says *what* it wants, the server decides amount, scope, model, permissions, and role. Anything cost-bearing sent by the client is a value the user can edit
- Rate limit per user, and cap usage where each call costs money
- Validate the request body at the boundary; reject malformed input with a clear error
- Log enough to debug — never the secret, the token, or the user's content

**Short-lived tokens** (when the client SDK connects directly)

- Generate server-side, scoped to this user and this resource, with the shortest viable lifetime
- Grant the minimum role the feature needs. Do not issue admin-level tokens because it made a permission error go away
- Define renewal before expiry, and what the UI does when renewal fails mid-session

**The app side**

- One typed client module for these endpoints; screens never call the service directly
- Explicit connection states — `idle`, `connecting`, `connected`, `failed` — surfaced in the UI. "Nothing is happening" is the worst state to ship
- Timeouts on every call, and retry only what is safe to retry
- **Clean up on both paths**: when the user ends the interaction *and* when the screen unmounts or the app backgrounds. Sessions left open are the standard way per-minute billing surprises people
- Errors mapped to actionable messages; never surface the provider's raw error

### Done when

- [ ] Building and grepping the bundle for each secret value returns nothing
- [ ] The route rejects an unauthenticated call, and rejects an authenticated caller asking for another user's resource
- [ ] Tampering with a cost- or scope-bearing field in the request changes nothing
- [ ] Rate limit verified by exceeding it
- [ ] A token expires and either renews or fails visibly — not silently
- [ ] Killing the app mid-session leaves no session open server-side
- [ ] Provider downtime shows a real message and the app stays usable
