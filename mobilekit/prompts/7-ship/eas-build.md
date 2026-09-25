# EAS Build & Deploy

Builds, store submission, and over-the-air updates.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Set up EAS Build for this app.

**Check the installed `eas-cli` version and follow the current docs** (https://docs.expo.dev/build/introduction/). Commands here move: environment-variable management in particular has been reorganized — use the current environment-variable commands rather than older secret commands, and confirm against `eas --help` for the installed version before scripting anything.

### Grill

- Which platforms ship, and to which stores? `PRODUCT.md` records this — read it and confirm it still holds.
- Are the developer accounts and store listings in place? A fact to check: missing accounts block submission, not building.
- Who owns the credentials — EAS-managed or manually supplied? Recommended default: EAS-managed — it removes the most error-prone manual steps, and remote builds need them server-side anyway. Manual only where a security policy requires holding the keys.
- Which environments are needed (development, preview, production), and does each point at a different backend? A fact first: `dev-environment.md` already named the environments and their variable sets — read them, and keep the profile names matched. Recommended default: all three, one variable set each — pointing preview at production's backend is how test data reaches real users.
- Is over-the-air updating wanted? Recommended default: yes, scoped to JS-only fixes. A native dependency added later still needs a store build — confirm the developer understands the boundary.

### Build

**Profiles** — a development profile producing a dev client, a preview profile for internal distribution, and a production profile with version auto-increment. Do not copy a profile block from memory; generate it with the CLI and then adjust.

**Environment variables** — this is where secrets leak:

- `EXPO_PUBLIC_*` variables are embedded in the bundle and readable by anyone with the app. Only genuinely public values (publishable keys, project URLs) belong there
- Server-side secrets belong to the API route or backend deployment, never to the app build
- Store per-environment values in EAS with the current environment-variable commands, and keep secret values out of the repo
- The Android submission credential is a **Google Play service-account JSON** — a different file from Firebase's `google-services.json`, and easily confused. Reference it by path, add it to `.gitignore`, and never commit it. Same for iOS keys
- The Android keystore: confirm Play App Signing holds the app signing key (a reset path exists then; without it a lost keystore orphans the listing), export a backup of the upload keystore, and record where it and its passwords live — somewhere a named second person can reach

**Verification before the first store build**

- Confirm the bundle contains no secret: build, then search the output for known secret values
- Test a preview build on a physical device — not a simulator build — before submitting. Distribution to testers and the review loop belong to `beta-and-review.md`, which runs next

**Submission and updates** — configure submission for the target stores, then set up update channels matched to build profiles so a preview update cannot reach production users. Update messages should say what changed.

Set a **`runtimeVersion` policy** deliberately, with the developer, and record it in the config. It is what stops an update from landing on a binary whose native code cannot run it — that failure is a crash on launch, and the only rollback is another store build.

### Done when

- [ ] A development build runs on a physical device
- [ ] A preview build installs and works against the correct environment
- [ ] Grepping the built bundle for secret values returns nothing
- [ ] No credential file is tracked by git — verified with `git ls-files`
- [ ] An OTA update reaches a build on the matching channel and not on others
- [ ] An update published against a different `runtimeVersion` does not reach the old binary
- [ ] Version and build numbers increment correctly between production builds
- [ ] The upload keystore's backup and passwords are reachable by a named second person
