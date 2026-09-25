# Payment Gateway (Stripe)

For physical goods, services, or bookings — model F in `PRODUCT.md`'s Monetization section. Skip unless that section selects it, or the Capabilities table marks payments "now".

Digital content and subscriptions inside the app must use store billing instead — see `in-app-purchases.md`. Shipping the wrong one gets the app rejected.

Prereqs: a Stripe account, and a server you control (Expo API route or backend) — there is no client-only path. Run `secure-backend.md` first; the authentication, authorization, and secret-handling rules for the endpoints below live there.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Integrate Stripe for payments.

**Check the installed `@stripe/stripe-react-native` and `stripe` versions and follow their docs** (https://docs.stripe.com/payments/accept-a-payment?platform=react-native). API versions and the payment-sheet options change; do not paste initialization from memory.

### Grill

- What is being charged for, and is the amount computed server-side? **It must be** — an amount sent from the app is an amount the user can edit.
- One-time payment, saved payment method for later, or recurring billing?
- Apple Pay / Google Pay? Each needs additional platform configuration and a merchant identifier.
- Which currencies, and is tax or shipping involved?
- What happens **after** payment succeeds — which record is created, and where? That record is the order (see `domain-model.md`).
- Refunds and cancellations: in scope now?

### Build

**Server side** (API route or backend — never in the app):

- `STRIPE_SECRET_KEY` lives only here, in a non-`EXPO_PUBLIC_` variable
- An endpoint that creates the payment intent, computing the amount from server-held data and the authenticated user — it accepts an identifier of *what* is being bought, never a price
- The endpoint requires authentication and verifies the user may buy this thing
- A **webhook** endpoint with signature verification as the source of truth for fulfillment. The client returning from the payment sheet is not proof of payment — the user can lose network mid-flow, and the payment still succeeds
- Idempotency so a retried request does not charge twice
- Where a saved payment method was chosen in the grill: a Stripe Customer created and stored against the user's server record, and an ephemeral-key endpoint so the sheet can list saved cards — the customer id is never minted client-side
- Where refunds are in scope: a server-side refund path tied to the order record, with the refund webhook events driving the order's state — an order refunded in the dashboard must not keep showing paid

**App side:**

- Provider configured with the publishable key from env
- Payment-sheet flow: fetch the intent from your endpoint, initialize, present, and interpret the outcome — treating user-cancelled as a normal path, not an error
- A checkout screen showing what is being bought and the server-computed total, with the pay button disabled while in flight so no double submission
- Success confirmation reflecting the **server-confirmed** state, plus a pending state for when the webhook has not landed yet
- Every failure path handled: declined, network loss mid-payment, expired intent

### Done when

- [ ] A test-card payment succeeds and fulfillment happens via the webhook, not via the client's return
- [ ] The secret key is absent from the bundle — grep the built output to confirm
- [ ] An amount tampered with in the request cannot change what is charged
- [ ] Cancel, decline, and mid-payment network loss all leave a correct, non-duplicated state
- [ ] Double-tapping pay charges once
- [ ] Where saved methods were chosen: a returning user sees their saved card in the sheet, and another user does not
- [ ] Where refunds are in scope: a refund issued in the Stripe dashboard moves the order out of paid via the webhook
