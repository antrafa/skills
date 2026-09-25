# NativeWind Setup

Install and configure NativeWind (Tailwind for React Native).

---

## Prompt

Read `RULES.md` (this library) and AGENTS.md first.

Set up NativeWind in this Expo app.

### Before you write anything

**The setup differs substantially between versions, and stale steps are the single most common failure here.** Work `RULES.md` §3 for the installed `nativewind` and `tailwindcss` majors (canonical: https://www.nativewind.dev) — whether a Tailwind config, a Babel plugin, or CSS directives exist at all is decided by those docs, not by an older guide. §4 owns config files: one exists when the installed version requires it, and what the repo already has is followed.

### Build

1. Install NativeWind and its peer dependencies at versions compatible with the installed Expo SDK.
2. Apply the config the installed version's docs specify: CSS entry, Metro config, Babel (only if required), TypeScript declarations.
3. Import the CSS entry in the root layout.
4. Set content/source paths so every route and component file is scanned.

### Done when

- [ ] A throwaway component styled only with `className` renders correctly on a device — not just in web
- [ ] `className` type-checks in `.tsx` files with no editor error
- [ ] No existing screen was modified
- [ ] You state which version's setup you followed, and any step in this prompt that no longer applied

Leave the design tokens to `design-system.md` — this prompt only makes styling work.
