# Bottom Tab Navigation

The app's primary navigation shell.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Implement the bottom tab navigation.

### Grill

- **Which tabs?** Derive candidates from `PRODUCT.md`'s core journey and confirm the list. 3–5 tabs; more than five is a sign something belongs inside a section rather than at the root. Name them with the app's own vocabulary, not "Explore" by default.
- Does the primary create action belong in a tab, or as a floating button? A center create-tab is a pattern, not a requirement.
- **Tab bar style — ask, do not choose:**
  - **A — Icon + label**, active in the primary color. Recommended default: clearest, most familiar, cheapest.
  - **B — Active indicator** (circle, pill, or underline behind the active icon) that animates between tabs.
  - **C — Floating bar**, inset from the edges with rounded corners and elevation.
- Does any tab need a badge (unread count)? That implies a data source.
- Is there a design reference to attach?

### Build

- A tabs layout with a route per confirmed tab, plus a placeholder screen for each (screen prompts fill them later)
- A custom tab bar only if the chosen style needs one; the default tab bar is adequate for A
- Active vs. inactive states from design tokens, safe-area padding at the bottom, and elevation consistent with the design system
- Animated transition for B, using the installed animation library (see `animations.md`) and honoring reduced-motion
- Which tab is the initial route, and what happens when a deep link targets a tab directly

### Accessibility — not optional

- Tap targets at least 44×44
- Each tab has an accessible label even when the label is visually hidden (style B hides text on the active tab; a screen reader still needs it)
- Selected state exposed to assistive technology, not conveyed by color alone

### Done when

- [ ] Every tab routes correctly, and the initial tab is the intended one
- [ ] Nothing is obscured by the tab bar on a device with a home indicator, or on Android with gesture navigation
- [ ] Tab labels use the app's vocabulary
- [ ] Screen reader announces each tab and its selected state
- [ ] Home screen UI not built here — that is `home-screen.md`
