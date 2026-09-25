# API Integration

Connecting the app to an HTTP or GraphQL API that someone else owns — a corporate backend, a partner service, a system that predates this project. Skip it if the backend is managed by this team (`supabase.md`) or the data is local (`domain-model.md` Scenario D).

Skipped, every screen grows its own `fetch`, its own timeout, its own guess at the payload, and a field renamed upstream breaks four screens in four different ways.

Prereqs: `domain-model.md` Scenario C — the `types/dto/` → mapper → domain split is defined there and this prompt builds on it, it does not restate it. Also needs the real contract or real captured payloads (RULES.md §3), and a device on a network that can actually reach the API.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Wire this app to [API], an API this team does not own or design.

### Grill

- **What shape is the contract?**
  - **A** — REST with a formal spec (OpenAPI/Swagger). Types are generated, not written.
  - **B** — REST with no spec: captured payloads, a wiki page, or a person who remembers. Types are derived from real responses and every undocumented field is an assumption.
  - **C** — GraphQL: schema plus codegen, and a cache decision to make (below).
  Recommended default: whichever the API team actually publishes — ask for it before choosing, because A with a stale spec behaves worse than B with fresh payloads.
- **If B: where are the captured payloads?** One real response per endpoint, including an error response and an empty-collection response. This is an input, not something to invent — ask for it and stop until it arrives (RULES.md §3).
- **If C: normalized client cache or TanStack Query (`react-query.md`)?** Recommended default: pick one. Apollo/urql normalized caching *and* a query cache is two caches disagreeing about the same entity, and the bug looks like "the list updated but the detail screen didn't".
- **How does the API authenticate?**
  - Bearer token from the auth layer — read at request time, never captured at module load, or it goes stale the first time it refreshes.
  - Static API key — if the provider calls it a secret it cannot be `EXPO_PUBLIC_*`; that is `secure-backend.md`, a proxy, not a header in the app.
  - mTLS or a corporate gateway — a client certificate is not something an Expo app carries. This means a server in front, decided now, not discovered during the release build.
  Recommended default: bearer from the existing auth layer, if there is one.
- **Which environments exist, and is staging data shaped like production's?** Ask directly whether staging has the volume, the odd characters, the long names, and the archived records production has. A list screen tested against six tidy staging rows is untested.
- **Which failures must the user be able to tell apart, and what does the app do for each?** At minimum: this record is gone, you are offline, your session died, the API is broken. One "Something went wrong" for all four generates support tickets nobody can answer.
- **Which write endpoints are safe to retry, and do any accept an idempotency key?** Usually undocumented, so ask the API owner. A retried payment or a retried submit is a duplicate, not a recovery.
- **Who owns this API, and how are breaking changes announced?** Record the answer in `docs/DOMAIN.md`, including "nobody tells us" — that answer changes how defensively the boundary is written.

### Build

**One client module**

- A single HTTP (or GraphQL) client module. Screens and hooks never call `fetch` directly — otherwise the base URL, the auth header, and the timeout exist in twelve places and only eleven get fixed.
- Base URL per environment, resolved from config, never a string literal in a service file.
- Timeout on every request, and retry only what the Grill established as safe. Mobile networks fail slowly; a request with no timeout is a spinner with no end.
- A correlation id generated per request and sent as a header, logged locally with the response status. Without it, "the app failed at 14:32" is unfindable in a server log carrying thousands of requests a minute.
- Auth applied inside the client, reading the current token at request time. On a 401, one refresh attempt, then replay the in-flight request; a second failure signs the user out rather than looping.

**Types, per contract shape**

- **A** — generate from the spec into a directory treated as read-only output; never hand-edit it. Commit the spec (or pin its version/URL) so a regeneration is reproducible and a diff shows what upstream changed. Assume the spec and the running API disagree: validate at the boundary anyway, and log the mismatch with the endpoint name instead of silently coercing.
- **B** — derive DTOs from the captured payloads, and record in `docs/DOMAIN.md` which fields were observed, from which environment, on which date. An undocumented field is an assumption with an expiry, and writing the date down is what makes it reviewable later.
- **C** — codegen from the schema, operations colocated with the components that use them, fragments per component so a screen's data needs are visible where the screen lives. Remember GraphQL returns `200` with an `errors` array: a partial-success response that ignores `errors` renders a screen half-populated and calls it a success.

**Boundary and results**

- Validate every response where it enters the app and fail with a domain error. `undefined` reaching a screen is a crash three renders away from its cause.
- Map transport failures to a domain error taxonomy the UI can branch on — not-found, unauthorised, validation-rejected, offline, server-broken, malformed-response. HTTP status codes do not belong in a component.
- Pagination taken from the real contract — page/offset, cursor, or link headers — not assumed. Feed the real shape to `react-query.md`; guessing cursor pagination for a page-based API produces silent duplicate rows.
- Errors surfaced as messages tied to what the user was doing. Never the raw upstream error body, which in corporate APIs frequently contains internal hostnames and stack traces.

**Environments**

- Dev, staging and production base URLs in config, switchable in a build without a code edit, and visible somewhere in a debug build so a tester can say which one they hit.
- If the API is only reachable via VPN or an allowlist, write that in AGENTS.md. "Works on my machine" is literal here.

### Done when

- [ ] A real request succeeds from a physical device against the environment the developer named
- [ ] A malformed or truncated response surfaces a domain error and never reaches a screen as `undefined`
- [ ] An expired token triggers one refresh and the in-flight request completes, without the user seeing a logout
- [ ] Building and grepping the bundle finds no API secret, certificate or credential
- [ ] A correlation id from a request made on the device is found in the server's log for that request
- [ ] Airplane mode produces the offline error, not the generic one; a deleted record produces not-found
- [ ] Pagination verified past the second page against real data volume, with no repeated or dropped rows
