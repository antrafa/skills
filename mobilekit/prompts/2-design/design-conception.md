# Design Conception (run after discovery, before any screen)

`PRODUCT.md` says what the app is. `design-system.md` says what things look like. Between them sits the question neither answers: **which screens exist, how you move between them, and what each one shows when it has nothing to show.**

Skipping this is why screens get rewritten. A home screen built before the navigation shape is decided gets rebuilt when the tab bar arrives; a list built before its empty state is considered ships a blank rectangle.

Run this **before** `domain-model.md` if the app is UI-led, or right after it if the data shape is the hard part. Either order works — both must precede any screen prompt.

---

## Prompt

Read `RULES.md` (this library) and `docs/PRODUCT.md` first.

You are designing the screen and navigation structure of this app. **Write no application code and install nothing.** The only output is `docs/DESIGN.md`.

### Hard rules

`RULES.md` §1 owns the interview mechanics — one question per message with a recommended default, `UNDECIDED — ask before assuming` for anything left open — and §2 the vocabulary: the real noun, never "item detail". The blocks below are the grill, not a form to hand over. On top of that:

1. Every screen you list must trace back to a step in the core journey or a capability marked "now" in `PRODUCT.md`. A screen that traces to neither does not go in the list — say why you dropped it.

### Block A — Screen inventory

Derive the list from the core journey, then confirm it:

1. Walk the core journey from `PRODUCT.md` and name one screen per step. Present that list and ask what is missing.
2. For each capability marked "now", which screen carries it? A capability with no screen is either unreachable or belongs to a screen already listed. A `## Monetization` section in `PRODUCT.md` counts here: the paywall and each boundary state it names are screens, and they enter the inventory now.
3. Which of these are the 3 screens the app is pointless without? Those get built first; the rest wait.

Classify each screen: **core** (journey), **support** (profile, settings), **entry** (onboarding, auth), **later**.

### Block B — Navigation shape

4. What is the top-level shape? Recommend one and say why:
   - **Tabs** — 3–5 destinations the user switches between freely. Default for content apps.
   - **Single stack** — one linear flow. Right when there is one job.
   - **Drawer** — many rarely-used destinations. Rare on mobile; usually a sign the tab count is wrong.
5. If tabs: which screens are tabs, and which are pushed on top of a tab? A screen reachable from two tabs needs to be decided now, not discovered later.
6. Which screens are **modal or sheet** rather than a push? Anything the user must finish or dismiss — a form, a confirmation, a picker.
7. Where does the app open on cold start, for: a new user, a returning signed-in user, a returning signed-out user? Each is a different route and each is a redirect someone forgets to write.
8. Which screens require authentication? What happens when a signed-out user reaches one via a link? (This is the input `deep-linking.md` needs.)
8b. `PRODUCT.md` names a success action. Which screen carries it, and what is the shortest path a first-time user walks from cold start to reaching it once? That path is the **activation path** — onboarding and every empty state along it point forward to the next step, and everything not on it can wait. It is also what "an activated user" means downstream: the beta pass bar in `beta-and-review.md` and the funnel in `analytics.md` both read it.

### Block C — States per screen

For every **core** screen, fill four states. Most bugs reported as "the app is broken" are one of these missing:

| State | Question to answer |
|---|---|
| Empty | First-ever use, nothing exists yet. What does the user see and what is the one action offered? |
| Loading | First paint vs refresh. Skeleton, spinner, or stale-with-indicator? |
| Error | Request failed. What is retryable, and what does the user read? No stack traces, no "something went wrong". |
| Populated | The normal case. What is on screen, in what priority order? |

If the app works offline (`PRODUCT.md`), add a fifth: what this screen shows with no connection.

Do not write the copy for all of them here. Write the *decision* — the copy comes with the screen.

### Block D — Visual direction

9. `PRODUCT.md` records the design source. Confirm which applies:
   - **A — A reference exists** (Figma, screenshots, a live app, a brand palette). Ask for it: `@path/to/reference.png`. Describe what you extract from it — palette, type rhythm, density, corner style — and confirm before it becomes tokens.
   - **B — Nothing exists.** Do not propose a palette yet. Propose 2–3 *directions* in one line each — what the app should feel like and what that implies (e.g. "calm and dense, like a reading app: muted surface, tight spacing, one accent"). Get a direction chosen; the palette is `design-system.md`'s job.
10. Density and target: one-handed phone use, tablet too, landscape? Each changes layout, not just size.
11. Is there an accessibility floor to hit now rather than audit later — larger minimum text, high contrast, no color-only meaning? Cheap now, expensive in `accessibility.md`.

### Block E — The shared pieces

12. Reading the screen list, which components appear on 3 or more screens? That set — and only that set — is what `ui-components.md` builds. A component library built before this list is speculation.

---

## Output

Write `docs/DESIGN.md`:

```markdown
# Design Definition

## Screens
| Screen | Type | Journey step / capability | Build order |
|---|---|---|---|
| [Name] | core | [step it serves] | 1 |

Dropped (and why): [...]

## Navigation
Shape: [tabs | stack | drawer] — [why]
Tabs: [...]
Pushed on a tab: [screen → parent tab]
Modal / sheet: [...]
Cold start: new → [route] · signed-in → [route] · signed-out → [route]
Auth-required: [...] · Unauthenticated arrival: [redirect | prompt | preview]

## Activation
Success action: [from PRODUCT.md] · Screen: [...]
First-run path: [cold start → … → success action]

## States
### [Screen name]
- Empty: [what is shown, one action offered]
- Loading: [skeleton | spinner | stale-with-indicator]
- Error: [retryable? what the user reads]
- Populated: [priority order of content]
- Offline: [only if PRODUCT.md requires it]

## Visual direction
Source: [A reference | B chosen direction]
Direction: [one line]
Density / targets: [...]
Accessibility floor: [...]

## Shared components
[Component] — used by [screens]

## Open questions
- [UNDECIDED — ask before assuming]
```

Keep it skimmable. Screen prompts read it before every screen; a document nobody rereads decides nothing.

---

## After this

- `design-system.md` turns the visual direction into tokens.
- `domain-model.md` turns the domain vocabulary into types.
- `ui-components.md` builds exactly the shared-component list — nothing else.
- Every screen prompt (15–23) reads `DESIGN.md` for its states before building.
- `beta-and-review.md` uses the activation path as the beta's pass bar; `analytics.md` derives the funnel from its steps.
