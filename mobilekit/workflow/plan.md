# Phase — plan

Turn `PRODUCT.md` + `DESIGN.md` into an ordered checklist. Alias: `/mobilekit:plan`.

**Prerequisite:** `docs/PRODUCT.md`. `docs/DESIGN.md` is strongly preferred — without it the screen steps are guesses. Missing → say so and ask whether to run design first or to plan the non-screen work only.

Read `prompts/RULES.md` first.

## Build the plan

**If `docs/MODERNIZATION.md` exists, its sequence is the spine.** Keep its step order, expand each step into prompt-sized boxes, and use the reference order below only for what the sequence does not cover. Contracts it marks "keep" or "wrap" rule out the competing prompt without discussion — a kept backend is `api-integration`, never `supabase`.

Start from the reference order in `prompts/README.md`, then **cut it down**:

- Remove every step whose capability `PRODUCT.md` marks "later" or "never". No payments step for an app with no payments.
- Replace the generic screen steps with the actual screens from `DESIGN.md`, in its build order — core screens first.
- Choose between mutually exclusive prompts and say why in one line: `auth-clerk` vs `auth-backend`; `supabase` vs `api-integration` for an existing API; `react-query` only if data comes from a remote source; `in-app-purchases`, `payments` and `ads` per `PRODUCT.md`'s Monetization section — where the app earns money and that section is missing, run `monetization.md` first.
- **Keep the steps a store submission requires**, whatever the product is: `native-permissions` if the app asks for any, `privacy-consent` if any analytics or tracking ships, `store-compliance` and `accessibility` before the first submission, `account-recovery` if the app has passwords, `content-moderation` if users can publish anything other users see.
- Read the repo. Anything already done is marked done, not queued — check `package.json` and the actual files.

## Output

Write `docs/BUILD-PLAN.md`:

```markdown
# Build Plan

Generated from PRODUCT.md and DESIGN.md. The `next` phase runs the first unchecked step.

## Foundation
- [x] expo-setup · already present
- [ ] nativewind
- [ ] domain-model

## Screens
- [ ] [real screen name from DESIGN.md] · list-screen

## Release
- [ ] accessibility
- [ ] store-compliance
- [ ] eas-build

## Skipped
| Step | Why |
|---|---|
| in-app-purchases | PRODUCT.md: payments = never |
```

Every unchecked box is one prompt file. Two prompts never share a box — the `next` phase runs one at a time on purpose.

## Report

The plan, the step count, and what was skipped. Then point at the next phase.
