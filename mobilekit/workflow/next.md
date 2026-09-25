# Phase — next

Run the first unchecked step of the plan. Alias: `/mobilekit:next`.

**Prerequisite:** `docs/BUILD-PLAN.md`. Missing → run the plan phase.

## Run one step

1. Read `BUILD-PLAN.md` and take the **first unchecked box**. One step. The next one stays untouched however small it looks.
2. Announce which step and which prompt file, and give the developer a chance to skip it before starting.
3. Execute it per the skill's "Executing a prompt" procedure — read, grill, build, walk `Done when`.
4. Check the box in `BUILD-PLAN.md` only when the checklist actually passed. Partially done stays unchecked, with a note of what remains.

## Every box checked

The plan is done, not the product. Not yet submitted → the ship phase. Submitted → `prompts/8-observability/post-release.md`. Deciding what the next version contains → `prompts/8-observability/next-feature.md` reads the four numbers and appends the next cycle to `BUILD-PLAN.md`; scope beyond `PRODUCT.md` gets a discovery round for the delta first. And every Expo SDK cycle, `prompts/9-maintain/sdk-upgrade.md` — on a schedule, not when something breaks.

## Blocked

A step that cannot proceed — a missing account, an `UNDECIDED` in `PRODUCT.md`, a credential you must not create — stops, states exactly what is needed from the developer, and leaves the box unchecked. A placeholder substituted to keep moving is a bug shipped with a tick beside it.

## Report

What was built, what the checklist says, and the next unchecked step.
