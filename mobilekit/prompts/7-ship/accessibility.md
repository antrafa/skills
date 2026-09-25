# Accessibility Audit

The screen prompts each carry their own accessibility requirements. This one is the sweep across the finished app — run it before the first store submission, and again after any redesign.

Not optional and not a nice-to-have: it is a legal requirement in several markets, an App Store review criterion, and the difference between usable and unusable for a large minority of users.

---

## Prompt

Read `RULES.md` (this library) and AGENTS.md first.

Audit this app for accessibility and fix what fails.

### How to run it

Go screen by screen through `PRODUCT.md`'s core journey — not file by file. Report findings as a list with the screen, the failure, and the fix. Fix as you go, but **report every finding**, including the ones you cannot fix without a design decision.

### What to check

**Screen reader** (VoiceOver on iOS, TalkBack on Android — both, on real devices)

- Every interactive element announces what it is and what it does. Icon-only buttons need labels; a tab bar that hides labels visually still needs them
- Images that carry meaning have descriptions; decorative ones are hidden from the reader
- State is announced, not just drawn: selected, expanded, disabled, loading, error
- Reading order follows visual order
- Focus moves into a modal or sheet when it opens, returns when it closes, and cannot escape into the content behind

**Dynamic type**

- Set the system font to its largest setting and walk the journey. Text must scale, containers must grow or scroll, nothing may be clipped or overlap
- No fixed-height container holding scalable text

**Contrast and color**

- Text meets WCAG AA (4.5:1 body, 3:1 large) in every theme, including on brand-colored buttons and over images
- No information conveyed by color alone — errors, selected filters, and status all need a second signal (icon, text, shape)

**Touch and motion**

- Interactive targets at least 44×44, with adequate spacing between adjacent ones
- Every gesture-only action has a non-gesture alternative — swipe-to-delete needs a reachable button
- Reduced-motion honored: animations become instant or fade, and nothing depends on motion to be understood

**Forms**

- Labels programmatically associated with inputs, not just placed above them
- Errors announced when they appear, and identified as belonging to a specific field
- Placeholder text is never the only label

### Done when

- [ ] The full core journey completed using only a screen reader, on both platforms
- [ ] The full journey usable at the largest system font size
- [ ] Contrast verified in every theme, including brand surfaces
- [ ] No color-only information remains
- [ ] All tap targets meet the minimum
- [ ] Reduced-motion verified with the OS setting enabled
- [ ] Findings that need a design decision are listed and raised, not quietly skipped
