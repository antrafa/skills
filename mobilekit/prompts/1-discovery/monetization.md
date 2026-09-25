# Monetization Concept (run after discovery)

How the app earns is a product decision with store-law consequences: the same feature priced as a subscription, a consumable credit, or an ad-funded free tier ships through three different prompts and three different review rules. Run this once `docs/PRODUCT.md` exists, whenever the app is meant to earn money — or the developer is not sure how.

Skip only when `PRODUCT.md` marks payments and ads "never".

---

## Prompt

Read `RULES.md` (this library) and `docs/PRODUCT.md` first.

You are running a monetization interview. Like discovery, it is a grill from end to end: write no code and install nothing — the output is a `## Monetization` section in `docs/PRODUCT.md`.

**Assume no monetization experience.** This interview is likely the developer's first contact with the subject, so it teaches as it asks: gloss each term on first use ("consumable credits — a balance the user buys and spends, like prepaid minutes"), put a number on every consequence that has one (the store's cut, a price floor), and phrase each recommendation as what this app's users would experience, in the domain vocabulary. The developer still decides; they just decide informed.

### Block A — What is worth paying for

1. Which part of the product would a user pay for, in one sentence? If the answer is "nothing yet", the honest recommendation is to ship free and return here with usage data.
2. Who pays — the end user, their employer, nobody (ad-funded)?
3. What do comparable apps in this category charge, and how? A model users never meet in the category is a model they distrust.

### Block B — The model

The recommendation is derived, not guessed: read the signals `PRODUCT.md` and Block A already gave, and name the matching signal when recommending.

| Signal | Points to |
|---|---|
| Each use has a marginal cost — AI calls, processing, human time | **D**, priced above that cost |
| The value recurs: content refreshes, a service keeps working | **B** |
| One-shot utility, value delivered on day one | **C** — **A** only carries a known brand |
| Mass casual audience, high session count, low willingness to pay | **E** |
| Physical goods or real-world services | **F**, always |
| An employer pays, or it is an internal tool | none — say so and stop here |

Present the menu, recommend against the table, and wait:

- **A — Paid app.** One price at the store door. Simple, and the hardest sell: no trial, and both stores buried the model for a reason.
- **B — Subscription.** Recurring, through store billing (`in-app-purchases.md`). Right when the value recurs — content that refreshes, a service that keeps working. Wrong for one-shot utility.
- **C — Freemium with one-time unlocks.** Free core, paid features (`in-app-purchases.md`).
- **D — Consumable credits.** Pay per use — the natural fit when each use has a marginal cost, AI calls above all. `in-app-purchases.md` sells them; `ai-features.md` meters them.
- **E — Ads.** Free, funded by an ad SDK (`ads.md`). Needs volume to pay anything, and costs consent prompts, review scrutiny, and screen space. Rewarded ads pair well with D.
- **F — Physical goods or real-world services.** Not monetization of the app itself — `payments.md`, and store billing is forbidden for it.

Hybrids are normal — free + ads + a subscription that removes them; a free tier + credits. Name each part.

### Block C — The boundary

4. Where exactly does free end? List the features or the usage cap on each side. A freemium boundary drawn feature-by-feature later gets drawn twice.
5. What does a free user see at the boundary — a locked screen, a preview, a counter running down? That is the paywall's design input; `design-conception.md` records it in `DESIGN.md` like any other screen.
6. Trial: none, time-boxed, or usage-boxed? Who is eligible, and what happens the day it ends?
7. If credits: what does one credit buy, does it expire, and is the balance visible before every paid action?

### Block D — The consequences (state them, do not decide them)

- Digital content and subscriptions must use store billing; physical goods must not (`store-compliance.md`).
- The store takes its cut of models A–D. Price with it in mind.
- Ads pull in a consent chain — `privacy-consent.md`, the iOS tracking prompt, and a data-safety declaration that must stay true.
- Every model needs recovery: a subscription survives reinstall, a credit balance lives server-side, a paid app follows the store account.

## Output

Append to `docs/PRODUCT.md`:

```markdown
## Monetization
Model: [paid | subscription | freemium | credits | ads | hybrid: ...]
Who pays: [...] · Category norm: [...]
Free/paid boundary: [...]
At the boundary the free user sees: [...]
Trial: [...] · Credits: [what one buys, expiry, where the balance shows]
Prompts this selects: [in-app-purchases | payments | ads]
```

Update the Capabilities table to match, and record anything unresolved as `UNDECIDED — ask before assuming`.

## After this

- `design-conception.md` — the paywall and every boundary state are screens; they go in `DESIGN.md`.
- The plan phase keeps only the prompts this section selects: `in-app-purchases.md`, `payments.md`, `ads.md`.
