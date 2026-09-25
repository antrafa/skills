# Dark Mode

Skip unless `PRODUCT.md` marks dark mode "now". Retrofitting it is far cheaper if `design-system.md` already defined semantic tokens.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Add dark mode support.

### Before you write anything

**Check the installed NativeWind version and read its dark-mode docs** (RULES.md §3 · canonical: https://www.nativewind.dev). React Native has no `document.documentElement`, so web guidance does not transfer: a hand-written hook that returns `'dark'` changes nothing on its own, because nothing applies the class to the tree. NativeWind exposes its own color-scheme API for setting and reading the active scheme — use that as the mechanism, and read the installed version's docs for its exact name and whether a `darkMode` setting is still required in the Tailwind config.

Verify the switch works on a device before styling a single screen. Building 20 screens against a scheme toggle that never fires is the expensive failure here.

### Grill

- Three options (light / dark / system) or just a system-following toggle? System-only is less code and what most users expect.
- Should the choice persist across restarts and follow the account, or is per-device enough?
- Do any brand colors need a different value in dark mode? A primary tuned for white backgrounds often fails contrast on dark ones — this needs a design decision, not a guess.
- Are there assets (logos, illustrations, screenshots) that need a dark variant?

### Build

- Semantic tokens defined for both schemes: background, surface, foreground, muted foreground, border, and the brand colors, adjusted where contrast requires it. Screens use semantic names — a component referencing a literal hue cannot theme
- The scheme applied through NativeWind's mechanism, driven by the persisted preference and falling back to the system scheme
- Persist the preference and restore it before the first paint, so a dark-mode user does not see a white flash on launch
- Status bar style following the active scheme
- The selector in Settings (`settings-screen.md`), applying immediately
- Dark asset variants where needed; images with baked-in white backgrounds must be handled, not ignored

### Done when

- [ ] The toggle demonstrably changes the UI on a device — proven before the rest of the work
- [ ] Every screen and overlay checked in both schemes, including modals, sheets, and the tab bar
- [ ] No white flash on cold launch in dark mode
- [ ] Text contrast meets WCAG AA in both schemes, including on brand-colored surfaces
- [ ] Status bar readable in both
- [ ] System-scheme changes while the app is running are picked up
