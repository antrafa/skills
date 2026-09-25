---
name: mobilekit-build
description: Run one specific mobilekit prompt out of the plan order. Argument is the topic — for example auth, media-upload, offline, payments, push, deploy, legacy. Use on `/mobilekit:build`, or when one capability is asked for in an app that already exists.
metadata:
  short-description: Run one prompt out of order — takes a topic
---

# mobilekit build

Read `../../workflow/build.md` — relative to this file, inside the `mobilekit` skill — and run that phase.

`../../prompts/RULES.md` governs how prompts are run and is not restated here.

The text after the invocation is the topic. Codex substitutes nothing into this file — read it from the message.
