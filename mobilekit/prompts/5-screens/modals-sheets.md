# Modals & Bottom Sheets

Overlay surfaces for confirmations, pickers, and short flows.

---

## Prompt

Read `RULES.md` (this library) and AGENTS.md first.

Implement the overlay surfaces this app needs.

### Grill

- **Which overlays does the app actually use, and for what?** List them before building anything. Common: destructive confirmation, action list, filter panel, short form, success/error acknowledgement.
- Would a **route** serve better than a modal? Expo Router can present a route as a modal, which keeps back-button behavior, deep linking, and state handling for free. For anything with more than one field, prefer the route. Recommend this before adding a sheet library.
- **Implementation — ask, do not choose:**
  - **A — Router modal presentation.** No dependency, correct navigation semantics. Recommended default.
  - **B — Platform `Modal`.** Enough for a centered confirmation or a simple bottom panel.
  - **C — `@gorhom/bottom-sheet`.** Justified only when you need snap points, drag-to-resize, or gesture-driven dismissal. It is a real dependency — ask before installing.
- Does any overlay contain text input? If yes, keyboard avoidance inside the overlay is part of the work, and it is the part that usually breaks.

### Build

- The chosen mechanism, wrapped once in a shared component so overlays look consistent instead of each screen styling its own
- Backdrop dimming, tap-outside to dismiss where dismissal is safe, and **no** tap-outside dismissal for destructive confirmations or forms with unsaved input
- Android hardware back must close the overlay, not the screen behind it
- Safe-area padding at the bottom for bottom-anchored surfaces
- Enter/exit motion consistent with the design system, honoring reduced-motion
- One place that owns whether an overlay is open. Two overlays racing to open is a common and ugly bug — decide what happens if one is requested while another is showing

### Accessibility

- Focus moves into the overlay on open and returns on close
- Assistive technology must not reach the content behind the overlay
- A visible, reachable close affordance — gesture-only dismissal is not sufficient

### Done when

- [ ] Every overlay in the list opens, dismisses, and cleans up its state
- [ ] Android back closes the overlay only
- [ ] An overlay with input keeps the focused field above the keyboard on both platforms
- [ ] Destructive confirmations cannot be dismissed accidentally
- [ ] Screen reader is trapped inside the overlay while it is open
- [ ] No dependency added without approval
