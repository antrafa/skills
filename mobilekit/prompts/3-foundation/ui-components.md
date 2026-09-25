# Common UI Components

The building blocks every screen composes from. Run after `design-system.md` — components consume tokens, they do not define them.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Build the shared UI components for this app.

### Grill

**Build what the confirmed screens need, and nothing else.** Walk `PRODUCT.md`'s core journey, list the components those screens require, and confirm the list. A component library with unused variants is dead code that still has to be maintained and reviewed.

Then confirm:

- Which variants and sizes are genuinely used? Five button variants when the app uses two is four too many — build a variant when a screen needs it.
- Is a variant helper (`cva` or similar) already installed, or is a conditional class map enough? For a handful of components, plain conditionals are fewer moving parts.

### The likely set

Build only the ones the answers justify:

- **Button** — variants and sizes actually used; loading state that replaces the label with an indicator while keeping the button's width stable (a resizing button on submit is a visible jump); disabled distinct from loading; optional icon
- **Input** — label, placeholder, error slot, focus styling, disabled, secure and multiline variants. Coordinate with `form-screens.md` so form fields are not built twice
- **Card** — surface with the design system's radius and elevation; a pressable variant with press feedback
- **Avatar** — image with initials fallback and the sizes in use
- **Badge / Chip** — status labels and selectable filters. Selected state must be distinguishable without color alone
- **Skeleton** — loading placeholder shaped like the content it replaces, not a generic grey box
- **Divider**, **EmptyState** — empty state takes an icon, a title, a description, and an optional action; every list and dashboard depends on it

### Rules

- Tokens only — no hard-coded colors, spacing, or font names
- Every interactive component: minimum 44×44 tap target, an accessible label, and its state exposed to assistive technology
- Accept a class-name override for one-off adjustments, but if a screen overrides the same thing repeatedly, that is a missing variant
- Props typed with unions, not `string`
- Keep components presentational — no data fetching, no store access inside a button

### Done when

- [ ] Every component built is imported by at least one screen or is on the confirmed list
- [ ] No hard-coded style values
- [ ] Tap targets and accessible labels verified with a screen reader on both platforms
- [ ] Loading button does not resize; skeletons match real layout
