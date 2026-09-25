# CI / CD

Skip this for a prototype. It is justified the moment more than one person commits, or a release has to be reproducible — a build that only works on one laptop is a single point of failure with a name.

`eas-build.md` configures the build itself; this prompt is about what runs automatically, when, and who is allowed to release. Prereqs: `eas-build.md` done, `testing.md` for the test commands, and a git host with branch protection available.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Set up continuous integration and release automation for this app.

### Grill

- **Which CI provider?** **A** — the repo host's own runners (GitHub Actions, GitLab CI). **B** — the build service's hosted workflows (EAS Workflows). **C** — both: the host for checks, the build service for builds. Recommended default: **C**, because the store credentials already live with the build service and copying them into a second system doubles the number of places they can leak.
- **What runs on a pull request, on a merge, and on a tag?** Recommended default: checks on every pull request, an internal build on merge to the main branch, a production build and submission only on a tag. A full native build per commit is a bill nobody approved.
- **Who may trigger a production build and a store submission** — and is that enforced by the provider, or a convention someone will forget under deadline? Recommended default: enforced, restricted to a protected tag or a manual approval, because a convention is not a control.
- **Where do the store credentials live, and whose account is the release identity?** Confirm it is an organisation account. A release signed by a person's personal account stops shipping the day that person leaves, and the recovery path is a support ticket measured in weeks.
- **Is there a staging environment with its own backend?** That answer decides how many variable sets exist, and whether a preview build can reach production data — see `eas-build.md`.

### Build

Order the pipeline by cost: the cheapest check fails first.

**Per pull request — cheap and fast**

- Type check, lint, the unit and domain tests from `testing.md`, and a dependency audit for known vulnerabilities
- These must finish quickly enough that people wait for them. A ten-minute check on every push gets ignored, bypassed, or merged around
- The Expo project doctor, catching the dependency mismatch that would otherwise surface as a crash after submission rather than a red check before merge

**Per merge to the main branch**

- A development or preview build published to internal testers, so the current state of the branch is always installable by someone who is not a developer. Without this, "is it fixed?" is answered by a screenshot from the author's simulator

**Per tag or manual release**

- The production build and store submission, with version and build number incremented by the pipeline, not by hand. A hand-edited build number is the standard cause of a rejected upload
- The OTA channel matched to the build profile, so a preview update cannot reach production users
- The `runtimeVersion` policy from `eas-build.md` enforced by the pipeline, not remembered by a person — an update published from CI must never target a binary that cannot run it
- Release notes and rollback path per `release-rollback.md`; store metadata per `store-compliance.md`

**Secrets in CI**

- Every value injected from the provider's secret store, never committed and never printed. Log output is public in many setups; a build that echoes its environment has published it
- The Play service-account JSON and the iOS signing key are files, referenced by path from a secret and written at runtime outside the repo. They are the two most commonly leaked artefacts in mobile CI
- Server-side secrets belong to the deployment, not the app build (`secure-backend.md`)

**Caching and cost**

- State what is cached (dependency install, native build artefacts), what one full run costs, and a concurrency limit so one busy afternoon does not consume the month's quota

**Branch protection**

- Name the checks that actually block a merge. A check nobody blocks on is a notification, and notifications are muted

### Done when

- [ ] A pull request runs the checks, and a deliberately failing check blocks the merge button
- [ ] A merge to the main branch produces an installable build a non-developer opens on their own device
- [ ] A tag produces a submitted build with an incremented version and no manual step
- [ ] No secret appears in any log — verified by reading one full run's output, not assumed
- [ ] The pipeline builds from a clean checkout, so nothing depends on a developer's machine
- [ ] The release identity is an organisation account, and at least two people can trigger a release
- [ ] A concurrency limit and the per-run cost are recorded where the team can see them
