# Profile Screen

The user's own account screen.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Build the Profile screen.

### Grill

- Is this the user's **own** profile, a **public** profile others can view, or both? They are different screens with different privacy rules; do not build one and assume it covers the other.
- Which stats or figures are worth showing? Take them from `DOMAIN.md` — do not invent metrics to fill a row of cards.
- Can the user edit their profile here, including avatar upload? Upload means media permissions and storage — a separate decision.
- Is Profile separate from Settings? If they merge, skip `settings-screen.md` and put preferences here instead of building both.
- Is account deletion required? **If the app has accounts and ships on the App Store, in-app deletion is required by Apple.** Confirm whether it deletes or anonymizes, and what happens to the user's content.

### Build

- Header: avatar with an initials fallback, display name, and secondary identity line — from the auth provider or the user record
- Stats only if confirmed, using the app's real figures
- Grouped rows with section headers, each row tappable with a leading icon and a trailing chevron. Only include rows that lead somewhere that exists — a row that does nothing is worse than an absent row
- Sign out with confirmation: call the provider's sign-out, clear persisted user state and any analytics identity, and route to the unauthenticated entry point
- Account deletion, if in scope: double confirmation, an explicit statement of what is deleted, a server-side action (never client-only), and immediate sign-out afterwards

### Every state

- Loading, and a graceful render when optional fields (avatar, display name) are missing
- Error on a failed sign-out — the user must not be left in an ambiguous state

### Done when

- [ ] Sign-out leaves no user data behind: store cleared, tokens cleared, analytics reset
- [ ] Every row navigates somewhere real
- [ ] Missing avatar and missing name both render correctly
- [ ] Deletion, if built, is server-side and confirmed twice
- [ ] Long names and long emails do not break the layout

If a design reference exists, attach it: `@path/to/profile-design.png`
