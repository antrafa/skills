# Authentication with Clerk

Two steps: build the auth UI, then wire it to Clerk. Skip both if `PRODUCT.md` says the app needs no accounts.

Prereq: a Clerk project (https://clerk.com) and its publishable key.

---

## Prompt — Step 1: Auth UI, no logic

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Build Sign Up and Sign In screens with UI only — no auth calls yet.

### Grill

- Which sign-in methods does `PRODUCT.md` list? Email/password, email code, magic link, Google, Apple, phone? Build UI only for those.
- Does sign-up collect anything beyond credentials (display name, the preferences from onboarding)?
- Is there a design reference to attach?

### Build

- Sign Up and Sign In routes in an auth route group, sharing layout and visual language
- Only the fields the chosen methods require, plus social buttons for the chosen providers (styled, inert for now)
- A link toggling between the two screens
- If email verification is a chosen method: a verification step with a 6-digit code input, number pad, kept above the keyboard, auto-submitting on the last digit
- Inline error slots and a loading state on the primary button — Step 2 fills them, and retrofitting them later means editing every screen again
- Design system tokens only

Mock the outcome for now: the primary button advances the flow so navigation is testable end to end.

### Done when

- [ ] Both screens render from design tokens, with the chosen methods' fields and nothing else
- [ ] The mocked flow navigates end to end: sign-up → verification (where chosen) → the authenticated route
- [ ] Inline error slots and the loading state exist on every screen, inert

---

## Prompt — Step 2: Clerk integration

Read `RULES.md` (this library) and AGENTS.md first.

Replace the mocked auth with Clerk, keeping the existing UI and navigation intact.

**Check the installed `@clerk/clerk-expo` version and follow the docs for that version** (RULES.md §3 · canonical: https://clerk.com/docs/quickstarts/expo). Provider setup, token caching, and hook names have all changed across majors — do not apply steps from memory.

### Grill

- Where should a newly verified user land — home, or a required setup step (`PRODUCT.md`'s first-session journey)?
- Does the app need Clerk user data mirrored into your own database (see `domain-model.md`)? If yes, that is a separate step with a webhook or a first-login upsert — do not silently duplicate user rows.

### Build

- Install `@clerk/clerk-expo` and a secure token cache backed by `expo-secure-store`
- Wrap the app in Clerk's provider in the root layout; publishable key via `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY`
- Implement only the flows Step 1 built UI for, using Clerk's hooks: sign-up, sign-in, verification, OAuth
- Plug the session into the gate `app-shell.md` built in the root layout: authenticated → the first authenticated route; not authenticated → onboarding or auth. The session joins the boot list behind the splash — an unresolved session must not flash the auth screen at a signed-in user, and no second gate is added
- Map Clerk errors to the inline error slots already in the UI. Show the actionable message, not the raw error object

### Done when

- [ ] Sign up, verify, sign in, sign out, and relaunch-while-signed-in all work on a device
- [ ] No flash of the wrong screen while the session resolves
- [ ] Failure paths show usable messages (wrong code, taken email, no network)
- [ ] Screen designs unchanged
