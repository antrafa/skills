# Animations with Reanimated

Motion that clarifies state changes. Skip if nothing in the app needs it yet — Expo's built-in `Animated` and layout defaults cover simple cases.

---

## Prompt

Read `RULES.md` (this library) and AGENTS.md first.

Set up Reanimated and build only the animations this app actually uses.

### Before you write anything

**Check the installed `react-native-reanimated` version and the Expo SDK, then follow the docs for that major** (RULES.md §3 · canonical: https://docs.swmansion.com/react-native-reanimated/). Specifically:

- **Do not add a Babel plugin by reflex.** On current Expo SDKs `babel-preset-expo` already handles Reanimated, and Reanimated 4 moved worklet compilation to a separate package. Adding a stale `react-native-reanimated/plugin` entry — or creating a `babel.config.js` that did not exist — breaks the build. Check whether this repo even has a Babel config before touching one.
- Layout-transition APIs were renamed between majors (the old `Layout` export is deprecated in favor of explicit transitions such as `LinearTransition`). Use what the installed version exports.
- Reanimated 4 requires the New Architecture. Verify before assuming an upgrade is drop-in.

### Grill

- Which interactions in `PRODUCT.md`'s core journey deserve motion? Build those. Do not create a library of animated components nothing imports.
- Is Reanimated needed, or would the platform default do? A screen transition and a pressable's opacity are free.

### Build only what is used

Typical set, each added when a screen needs it:

- **Press feedback** on primary controls — a small scale or opacity change. Prefer the pressable's built-in state; reach for gesture handling only when the interaction is genuinely gestural
- **Mount/unmount transitions** for content that appears conditionally, via entering/exiting animations
- **List item add/remove** via the installed version's layout transition API
- **Progress indication** driven by a shared value, if the app has progress
- **Sheet/modal motion** — coordinate with `modals-sheets.md` rather than animating a modal twice

### Rules

- Animate on the UI thread: shared values and animated styles, no state updates per frame
- Springs for interactive motion, timing when duration must be exact
- Keep durations short (150–300ms). Motion that the user waits on is a bug
- **Respect reduced-motion.** Check the OS accessibility setting and fall back to instant or fade. This is not optional polish
- Verify on a low-end Android device, not only in a simulator

### Done when

- [ ] The build passes with no stale Babel plugin added and no config file created unnecessarily
- [ ] Every animated component is imported by a real screen
- [ ] Reduced-motion honored
- [ ] Smooth on a physical low-end device
- [ ] You state which version's API you used and any step here that no longer applied
