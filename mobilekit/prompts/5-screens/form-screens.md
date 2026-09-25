# Form Screens (Create / Edit)

Screens where the user produces data. Skip if all content in `PRODUCT.md` is authored rather than user-generated.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Build the create/edit form for a domain entity.

### Grill

- **Which entity, and which fields?** Take them from `DOMAIN.md`. Required vs. optional is a domain decision already recorded there — do not re-invent it in the UI.
- One screen or a multi-step flow? More than ~7 fields usually wants steps.
- Does create and edit share one screen, or are they separate? Sharing is usually right; confirm.
- What are the real validation rules per field — length, format, range, uniqueness? Uniqueness can only be checked server-side; decide whether that happens on submit or as the user types.
- Should an in-progress form survive leaving the screen or backgrounding the app? If yes, that is a draft, and drafts need a discard path.
- Does anything need a picker beyond text — date, select, image, location? Each pulls in a dependency or a native permission; ask before adding.

### Build

**Reusable field components** in the shared UI folder, each with label, value, change handler, error slot, and disabled state: text input (with secure and multiline variants), select, and only the specialized pickers actually needed. Build a picker when a field needs it, not preemptively.

**Screen structure** — header with a close/back action, fields with consistent spacing, and a submit button either inline or pinned. Pinned means safe-area padding plus keyboard avoidance.

**Validation** — validate on submit, not on every keystroke; revalidate a field on blur once it has been touched. Show errors inline beneath the field, scroll the first error into view, and keep the submit button enabled so pressing it explains what is wrong. Disable it only while submitting.

**Keyboard** — this is where forms usually fail on real devices:

- The focused field must stay visible above the keyboard on both platforms, verified on a small screen
- Correct `keyboardType` per field, `returnKeyType` chaining to the next field and "done" on the last
- The submit button must be reachable with the keyboard open
- Dismiss on tap outside

**Submission** — loading state on the button, no double submission, success navigates to the created entity or back with the list refreshed, failure keeps every entered value and shows a usable message. Losing a filled-in form to a network error is the worst outcome here.

**Leaving with unsaved changes** — either confirm before discarding or persist a draft. Silently losing input is not acceptable.

### Done when

- [ ] Every field maps to a field in `DOMAIN.md`; no invented fields
- [ ] Client validation matches the server's rules; a server rejection is displayed on the right field
- [ ] Keyboard behavior verified on a small iOS and a small Android screen
- [ ] A failed submit preserves all input
- [ ] Back with unsaved changes prompts or saves — never silently discards
- [ ] Edit mode loads existing values, and saving changes only what changed
