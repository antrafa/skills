# Expo Project Setup

Initialize a new Expo project. Skip this prompt if a project already exists — inspect it instead.

---

## Prompt

Read `RULES.md` (this library) and `docs/PRODUCT.md` first.

Create a new Expo project with TypeScript and file-based routing.

### Grill

- App name, slug, and bundle identifiers (iOS `com.x.y`, Android package)?
- Deep-link scheme?
- Target platforms — iOS, Android, web? (`PRODUCT.md` may already answer this.)
- Source under `src/` or at the repo root? Both are valid; pick one and keep it consistent — every later prompt reads this decision from the repo.

### Build

1. Scaffold with the current `create-expo-app` command and a TypeScript template. Check the Expo docs for today's recommended template rather than pasting a flag from memory.
2. Set up file-based routing with Expo Router: root layout with a stack navigator, one placeholder home route, and the correct entry point in `package.json`.
3. Install only the baseline runtime packages Expo Router and the app shell need — status bar, splash screen, fonts, safe area, screens, gesture handler — plus secure storage **only if `PRODUCT.md` says the app has accounts**.
4. Create the folder structure the project will actually use (routes, components, lib, store, types, data, constants, hooks, services, assets). Create a folder when the first file needs it; empty folders are noise.
5. Configure the app manifest: name, slug, scheme, bundle identifiers, icon, splash.

Do **not** install styling, state management, auth, or analytics libraries here — later prompts do that, and only for capabilities `PRODUCT.md` marked "now".

### Done when

- [ ] `npx expo start` runs and the placeholder route renders on a device or simulator
- [ ] The source-root decision (`src/` or root) is recorded in AGENTS.md
- [ ] No dependency installed that no capability in `PRODUCT.md` requires

`dev-environment.md` runs next — dev build vs Expo Go, devices and env files are its decisions, not this prompt's.
