# Deep Linking

Opening the app directly on a specific screen from a URL, a notification, or another app.

Needed by push notifications (`push-notifications.md`), OAuth callbacks (`auth-clerk.md` / `auth-backend.md`), payment returns (`payments.md`), and any share feature — so most apps need at least the basics.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Set up deep linking.

### Grill

- **Custom scheme, or universal links / app links on a real domain?**
  - Custom scheme (`myapp://`) — no domain needed, works for notifications and OAuth callbacks. Enough for internal navigation.
  - Universal/app links (`https://yourdomain.com/...`) — required for links shared outside the app, and for a link that opens the web page when the app is not installed. Needs verification files hosted on the domain and correct native configuration.
- Which routes are linkable? Usually detail screens for the entities in `DOMAIN.md`. Take the list; do not expose every route.
- **What happens when the target requires authentication and the user is signed out?** The destination must be preserved through sign-in and resumed afterwards. Dropping the user on the home screen after login is the most common deep-link bug.
- What happens when the linked record does not exist, was deleted, or the user has no access?
- Does the app share links outward? Then the URL format is a contract — it will exist in messages and emails long after the code changes.

### Build

- The scheme and, if in scope, the associated-domain configuration on both platforms plus the verification files on the domain
- Route mapping that reuses the existing router paths rather than a parallel table that drifts
- Parameters validated on arrival — a link is untrusted input; a malformed id must produce a not-found state, never a crash
- Pending-destination handling: capture the target, complete authentication, then continue. Also correct when onboarding sits between the link and the destination
- A sane back stack. Landing deep in a hierarchy from a cold start must still allow going back to something that exists, not straight out of the app
- Coordinate with `push-notifications.md` so payload routing goes through this same mapping instead of a second one

### Done when

- [ ] Every linkable route opens correctly from **cold start**, from **background**, and while the app is already on another screen
- [ ] A protected link while signed out: sign in, then land on the intended screen
- [ ] A link to a deleted or unauthorized record shows a real message
- [ ] Universal links, if used, open the app rather than the browser on a fresh install — verified on both platforms
- [ ] Back navigation from a deep-linked screen goes somewhere valid
- [ ] Notification taps route through the same mapping
