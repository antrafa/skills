# Phase — ship

The release gate. Alias: `/mobilekit:ship`.

A gate, not a step. It runs several prompts in a fixed order because each one finds problems that are cheaper before submission than after.

Read `prompts/RULES.md` first.

## Order

1. **`prompts/7-ship/testing.md`** — risk-driven scope. For an app handling money or auth, not optional.
2. **`prompts/7-ship/accessibility.md`** — the cross-app sweep. Store review rejects on this; users leave over it.
3. **`prompts/7-ship/performance.md`** — startup time, bundle size, list and image behaviour on a low-end device.
4. **`prompts/7-ship/security-review.md`** — the adversarial sweep: re-test every ticked security check, the joints between features, the storage dump, the logs. Before store-compliance, because a finding here changes the declarations.
5. **`prompts/8-observability/error-tracking.md`** — if it has not run. Shipping without it makes the first production crash invisible.
6. **`prompts/8-observability/privacy-consent.md`** — if any analytics, tracking or crash reporting ships to users in the EU or Brazil.
7. **`prompts/7-ship/store-compliance.md`** — privacy manifest, data-safety declarations, tracking permission, policy URL, reviewer account, age rating, metadata. This is what rejects builds.
8. **`prompts/7-ship/eas-build.md`** — profiles, environment variables, submission.
9. **`prompts/7-ship/beta-and-review.md`** — a build in testers' hands before the public, review notes, and the rejection loop the first submission usually meets.

A step is skipped only when the developer says to, and it is recorded in the report as skipped rather than passed.

## Toolchain check

Run the Expo project doctor for the installed SDK and report what it flags. A dependency mismatch it catches in one command is a crash someone else finds in production.

## Secret leak sweep — before the first store build

An actual check, not a paste from memory:

- `git ls-files` for anything credential-shaped: `.env`, `*.p8`, `*.p12`, service-account JSON, keystores. The Google Play service-account JSON and Firebase's `google-services.json` are different files and get confused.
- Confirm `.gitignore` covers them.
- Build, then grep the output bundle for each known secret value. `EXPO_PUBLIC_*` is inside the bundle by design — confirm nothing in there is actually secret.

Report anything found before continuing. A committed secret is not fixed by deleting the file: it stays in history, and the key has to be rotated.

## Physical device

A simulator build proves nothing about fonts, shadows, permissions, or push. Confirm a preview build ran on a real device before submission, and say plainly if it did not.

## Report

Per step: passed, failed with output, or skipped by request. Then point at `prompts/8-observability/post-release.md` for what to watch once users are in it, and at `prompts/8-observability/release-rollback.md` for what happens when one of those numbers goes bad. If `docs/LAUNCHES.md` exists, the release is `market-signal.md` moment #4 — the announcement goes to the responders first.
