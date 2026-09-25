# Phase — init

Prepare a project to be built with mobilekit. Alias: `/mobilekit:init`.

Read `prompts/RULES.md` first.

## 1. Inspect before writing

- **Is this an Expo project?** Read `package.json`. No `expo` dependency → say so and ask whether to scaffold (`prompts/3-foundation/expo-setup.md`), whether this is a legacy app to modernize (`prompts/9-maintain/legacy-modernization.md`), or whether this is the wrong directory.
- **Is this an app that already ships?** A released app has a domain and a codebase that outrank any interview. Route it to `prompts/9-maintain/legacy-modernization.md` before discovery.
- **Does `AGENTS.md` or `CLAUDE.md` already exist?** Read it. You are extending it, not replacing it.
- **Does `docs/` already hold `PRODUCT.md`, `DESIGN.md` or `BUILD-PLAN.md`?** Then this project has been through part of the flow — report where it stands instead of starting over.

## 2. Write AGENTS.md

Follow `prompts/1-discovery/agents-md.md`.

Without `docs/PRODUCT.md`, write only what is true regardless of the product — stack read from `package.json`, folder layout as actually found, conventions read from existing code — and mark the product-specific sections `TBD — run discovery`. The domain is not invented to fill them.

## 3. Nothing is copied

The prompt library stays in the skill and is read from there. The project gets `AGENTS.md` and its own `docs/`. A project that needs to override a rule writes `docs/mobilekit-overrides.md`, which is read after `prompts/RULES.md` and wins on conflict.

## Report

What was written, what was left alone, and the next phase:

- Legacy app → `prompts/9-maintain/legacy-modernization.md`
- No `PRODUCT.md` → discovery
- `PRODUCT.md` exists → design
