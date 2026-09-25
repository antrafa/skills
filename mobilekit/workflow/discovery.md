# Phase — discovery

The product interview. Alias: `/mobilekit:discovery`.

Read `prompts/RULES.md`, then run `prompts/1-discovery/product-discovery.md`.

## What holds here in particular

- **Write no application code and install nothing.** The only file produced is `docs/PRODUCT.md`.
- **Grill: one question per message**, each with a recommended default so the answer can be a confirmation. The questionnaire is never dumped at once.
- The domain is never inferred from the folder name, the repo, or an existing scaffold. A repo cloned from a tutorial says nothing about the product.
- Anything unresolved is recorded literally as `UNDECIDED — ask before assuming`.

## If `docs/PRODUCT.md` already exists

Read it, then ask whether this is a revision of specific sections or a fresh start. A document the developer answered by hand is not silently overwritten.

## If the app already ships

Discovery interviews a product that does not exist yet. A released app is inventoried instead — `prompts/9-maintain/legacy-modernization.md` produces `docs/PRODUCT.md` from what the code and the store listing already say, and asks only about the gaps.

## Report

The filled sections, every `UNDECIDED` left, and point at the design phase. Offer `prompts/1-discovery/market-signal.md` — optional, and this is the cheapest moment to learn whether anyone wants the app.
