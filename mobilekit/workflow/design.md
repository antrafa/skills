# Phase — design

Screens, navigation, per-screen states, visual direction. Alias: `/mobilekit:design`.

**Prerequisite:** `docs/PRODUCT.md`. Absent → stop and run discovery; there is nothing to derive screens from.

Read `prompts/RULES.md` first.

## Step 1 — Structure

Run `prompts/2-design/design-conception.md`. Write no code and install nothing; the only output is `docs/DESIGN.md`.

Every screen traces to a core-journey step or a capability marked "now" in `PRODUCT.md`. Screens that trace to neither are dropped, with the reason stated. Names come from the domain vocabulary.

## Step 2 — Visual system

Only after `DESIGN.md` records a visual direction, run `prompts/2-design/design-system.md` to turn it into tokens.

A design reference (Figma export, screenshots, brand palette) is requested before anything is proposed: `@path/to/reference.png`. Without one, propose directions and **let the developer choose the palette** — the palette of someone's product is their decision.

## Step 3 — App identity assets

Icon, adaptive icon, splash. These are design deliverables, not build configuration, and a placeholder shipped to a store is a rejected build. Confirm what exists and what has to be produced, and record the gap in `DESIGN.md`.

If arguments name one concern ("just the screens", "just the tokens"), run only that step.

## If `docs/MODERNIZATION.md` exists

The screens already ship. Derive them from the running app and the parity list — a "keep" row's current behaviour is its specification — and grill only where the redesign deliberately changes something. Inventing screens a live app already answers is the design-phase version of re-interviewing.

## Report

Which screens were dropped and why, what is still `UNDECIDED`, which identity assets are missing, and point at the plan phase. If `docs/LAUNCHES.md` exists, offer `prompts/1-discovery/market-signal.md` moment #2 — there is now something to show the people who replied.
