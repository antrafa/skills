# Design System

Establish the visual foundation: color, type, spacing, radius, elevation — centralized so one change propagates everywhere.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Define this app's design system.

### Grill

`PRODUCT.md` records the design source. Confirm which applies:

- **A — A design reference exists** (Figma export, screenshots, brand palette). Extract the palette, type scale, spacing rhythm, radii, and shadow style from it. Attach it: `@path/to/design.png`
- **B — Nothing exists yet.** Propose a direction before building it: 2–3 palette options and a font pairing, each in one line with what it signals. Wait for a choice — do not pick a palette for someone's product.

Also confirm: does the app need dark mode now? If yes, define tokens semantically from the start (`background`, `surface`, `foreground`, `muted`) rather than retrofitting later in `dark-mode.md`.

### Build

**Color** — define, and name by role rather than by hue:
primary (+ the shades actually used), secondary/accent, background, surface, foreground, muted foreground, border, success, warning, error. Do not generate a 50–900 ramp for every color; generate the steps screens will use.

**Typography** — load the chosen fonts with `expo-font` in the root layout, register the families with NativeWind, and define a type scale (display, heading, body, caption) with line heights. Include only the weights actually used — each one is a shipped font file. Free pairings that work: Inter, Nunito, Poppins, Outfit, Plus Jakarta Sans.

**Spacing, radius, elevation** — a single spacing scale, named radius tokens, and standard control heights (button, input, card). For shadows, use the mechanism the installed NativeWind version supports for React Native — check its docs. React Native shadow properties are not valid CSS, so do not paste `shadow-color` / `shadow-offset` into a stylesheet layer and assume it works; verify on a device.

**Centralization** — tokens live in one place and are the only source of color and font values. Where the installed Tailwind major expects the theme (CSS or a JS config), follow that; mirror tokens into a TypeScript constant only if non-className code needs them.

### Done when

- [ ] Changing one token visibly changes every screen that uses it
- [ ] No hard-coded hex value or font name outside the token definitions
- [ ] Fonts render on a physical device, not only in the simulator
- [ ] Shadow/elevation verified on both platforms
- [ ] The palette was chosen by the developer, not by you
