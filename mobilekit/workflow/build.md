# Phase — build

Run one specific prompt, out of order. Alias: `/mobilekit:build <topic>`.

This is the escape hatch for existing projects and one-off additions.

## Resolve the topic

Match the argument against the prompt index in `prompts/README.md`. A filename matches directly; a word matches by subject — "auth", "analytics", "offline", "deploy", "permissions", "media", "legacy", "launch".

Ambiguous — "auth" maps to `auth-clerk`, `auth-backend` and `biometric-lock` — list the candidates one line each and ask. No match → say so and list the nearest three. A prompt that does not exist in the library is not improvised.

## State the missing prerequisites

Prompts assume things. Before running, say plainly what is missing rather than working around it silently:

- **No `PRODUCT.md`** → the prompt has to guess the domain. Say that, recommend discovery, and run it anyway if the developer confirms.
- **A screen prompt with no `DESIGN.md`** → the screen's empty / loading / error states are undefined. Ask for them inline and record the answers.
- **`secure-backend`** is a prerequisite for anything holding a secret — AI, payments, realtime tokens, signed uploads. If the topic is one of those and it has not run, say so first.
- **`native-permissions`** is a prerequisite for camera, photos, microphone, location and notifications.
- **`privacy-consent`** gates analytics and error tracking in any app shipping to the EU or Brazil.
- **`post-release`** needs a production build with real users. Without one, thresholds are invented. Say so.

## Execute

Per the skill's "Executing a prompt" procedure. Resolve installed versions, grill the prompt's questions one at a time, walk `Done when`, report honestly.

If `docs/BUILD-PLAN.md` exists and contains this step, check its box.
