# Development Environment

Run this once, right after `expo-setup.md`, before the first native dependency arrives. It decides how the app runs on a developer's machine — a decision that, left implicit, is discovered as a broken workflow the day Expo Go stops being enough.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Establish how this project is run, on what, and against which backend.

### Grill

- **Expo Go or a development build?** Read `PRODUCT.md`'s capabilities first: anything needing native configuration of its own — permissions with your own usage strings, push, biometrics, payments — means a development build, and `native-permissions.md` lists one as a prereq. Recommended default: a development build from day one for any app headed to a store; Expo Go only for a throwaway prototype. Deciding late means every developer rebuilds their workflow mid-project.
- **Where does it run day to day?** A named simulator/emulator per platform for layout work, and at least one physical device for what simulators lie about — camera, push, biometrics, real performance. Confirm both exist; this is a fact to check, then a gap to close.
- **How many backends does development see?** Recommended default: two variable sets at most — local/dev and a production-shaped staging — wired through the app config so switching never edits code. `eas-build.md` later maps these onto build profiles; agree the names now so they match.
- **Is the repo a repo?** A fact to check: `git init` done, `.gitignore` covering `.env*`, credentials, and native build output — in place before the first secret exists to leak.

### Build

- The development build, where chosen: built and installed on the named devices. Check the current command for the installed CLI (RULES.md §3)
- `.env` files per environment, plus a committed `.env.example` naming every key with no value filled. The app config reads them; nothing else does
- The scripts a newcomer needs, in `package.json` and recorded in AGENTS.md: start, typecheck, lint, test — each runnable from a clean checkout
- `.gitignore` verified against `git status` after a run and a build. A build that dirties the tree with credentials is one `git add -A` from an incident

### Done when

- [ ] A clean checkout plus the documented commands reaches a running app on the simulator and the device
- [ ] The development build, where chosen, installs on the named device and reloads from the local server
- [ ] Switching environment files points the running app at the other backend with no code edit
- [ ] `git status` is clean after a run and a build; `.env` and credentials are untracked
- [ ] AGENTS.md names the commands, the devices, and which build type this project uses
