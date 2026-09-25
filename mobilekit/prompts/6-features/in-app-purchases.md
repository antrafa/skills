# In-App Purchases with RevenueCat

For subscriptions and one-time purchases of **digital** content. Skip unless `PRODUCT.md` marks purchases "now".

If the app sells physical goods or services, use `payments.md` instead — app-store billing is required for digital content, and forbidden for most physical goods.

Prereqs: RevenueCat account; App Store Connect and/or Google Play products configured; paid developer accounts. Purchases cannot be tested in Expo Go — a development build and sandbox accounts are required.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Integrate RevenueCat for purchases and entitlement checks.

**Check the installed `react-native-purchases` version and follow its docs** (RULES.md §3 · canonical: https://www.revenuecat.com/docs/getting-started/installation/reactnative) for configuration, offerings, and the customer-info listener API.

### Grill

- The model, the tiers, the trial, the free/paid boundary and what a non-paying user sees are recorded in `PRODUCT.md` §Monetization — read them; ask only what that section leaves `UNDECIDED`. No section → run `monetization.md` first.
- Entitlement identifiers as configured in RevenueCat (not product ids).
- Is entitlement also needed server-side (to gate an API), or is client-side gating enough? Server-side means webhooks — a separate step.

### Build

- Install and configure once, early in the app lifecycle, with the platform's public SDK key from env
- Identify the user after authentication so entitlements follow them across devices; log out on sign-out. Configuring anonymously and never identifying loses purchases on reinstall
- A paywall screen driven by **offerings fetched from RevenueCat** — never hard-coded prices. Prices are localized per store and change without a release
- Purchase flow with: loading state, user-cancelled treated as a normal outcome rather than an error, store errors surfaced in plain language, and success reflected immediately
- **A visible "Restore Purchases" action.** Apple rejects apps without it
- One entitlement hook as the single source of truth, subscribed to customer-info updates so expiry and renewal propagate without a restart. Gate features on entitlement identifiers, not product ids
- Loading state distinct from "not entitled" — showing a paywall to a paying customer while entitlements load is the worst failure mode here

**Consumable credits**, where chosen — the model behind pay-per-use and AI metering (`PRODUCT.md`'s Monetization section):

- The balance lives server-side, granted by validated purchase events (RevenueCat webhook or server API). A client-held balance is a number anyone can edit
- Grant exactly once per purchase: the store retries, the app dies mid-flow, the user restores — none of those may double-credit
- Spend server-side too, where the metered action runs (`ai-features.md`'s server is the natural place); the app only displays the balance
- The balance visible before every paid action, and the empty-balance path designed: what the user sees, and where it sends them

### Done when

- [ ] A sandbox purchase completes and unlocks the feature without a restart
- [ ] Restore works on a fresh install with the same store account
- [ ] Cancelling the sheet leaves the app in a clean state
- [ ] Prices come from offerings and display correctly in a second locale
- [ ] Entitlement loading never flashes the paywall at an entitled user
- [ ] Where credits are sold: a sandbox purchase credits the balance exactly once — verified by killing the app mid-purchase and by restoring — and a reinstall keeps it
- [ ] Verified on both platforms if both ship
