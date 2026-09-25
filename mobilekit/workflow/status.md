# Phase — status

Where this project is, and what to run next. Alias: `/mobilekit:status`.

Read-only. Change nothing.

## Read

- `docs/PRODUCT.md` — exists? any `UNDECIDED` left?
- `docs/DESIGN.md` — exists? any screen with undefined states?
- `docs/BUILD-PLAN.md` — how many boxes checked of how many, and the first unchecked one
- `docs/LAUNCHES.md` — optional; if present, the strongest signal reached and the next moment
- `package.json` and the repo — does what is installed match what the plan claims is done? A checked box with no dependency installed is a lie in the file.

## Output

Short. No preamble.

```
Phase:      [legacy | discovery | design | build | ship | observe]
PRODUCT.md  ok · 2 UNDECIDED
DESIGN.md   missing
BUILD-PLAN  7/24 · next: tab-navigation
Signal:     waitlist · next moment: #3 beta   (only if LAUNCHES.md exists)
Drift:      plan says zustand done, zustand not in package.json
Next:       design
```

Report drift where the files and the repo disagree, say which one is wrong, and leave the correction to the developer.

None of the three files exist → say the project has not started this workflow and point at the init phase. An app that already ships points at `prompts/9-maintain/legacy-modernization.md` instead.
