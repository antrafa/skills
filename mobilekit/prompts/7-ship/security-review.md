# Security Review

The cross-app adversarial sweep before submission — the security counterpart of `accessibility.md`. Individual prompts build their own defenses where they build the feature (`secure-backend.md` owns the server rules, `RULES.md` §6 the secrets, `domain-model.md` the row-level policies); this prompt does not re-teach any of it. It exists for what no single prompt can see: the joints between features, the surface nothing owns, and the regression since a check last passed.

It is also the only security pass an existing project gets when it entered through `/mobilekit:build` and never ran the prompts with the defenses built in.

Runs in the ship gate after `performance.md` and before `store-compliance.md` — a finding here can change the privacy declarations. Re-run it whenever an SDK, a permission, or a data class is added.

Prereqs: a release-configured build on a physical device, and a second authenticated account — half the checks below are two-party.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Sweep the app for the security failures that survive feature-by-feature construction.

### Grill

- **What is the most valuable thing this app holds?** Derive it from `PRODUCT.md` and `DOMAIN.md` — money, health records, private messages, location history, plain profiles — and confirm. It sets the depth of everything below; a to-do list and a wallet do not get the same sweep.
- **Which attacker is worth caring about?** **A** — a curious user with the app bundle. **B** — another authenticated user. **C** — someone holding the unlocked device. Recommended default: B — every multi-user app has this attacker, and it is the one the per-feature checks most often miss at the joints.
- **What blocks submission?** Recommended default: any finding that reaches another user's data blocks; everything else is recorded with a named owner and a date. A review whose findings block nothing is a report nobody reads.

### The sweep

**Re-test what already claimed to pass.** Walk `BUILD-PLAN.md` for every security-shaped box already ticked — another user's row denied, a tampered amount rejected, the rate limit enforced, the bundle grep clean — and re-run each against the current release build. A check that passed in week three regresses silently by week ten; that is why this sweep exists as a gate step and not a memory.

**The joints.** Each of these crosses two prompts' territory, so neither owns it:

- A deep link into a protected route: through auth, and through the biometric lock where one exists — the destination reached only after both gates
- The offline queue and the persisted caches: what is actually inside them on a real device, and whether anything sensitive sits outside secure storage
- Sign-out on a shared device: store, query cache, secure storage, scheduled notifications — nothing of the previous account recoverable, verified by signing in as the next one
- The error tracker and analytics: capture a session and read the payloads that actually left — no token, no PII beyond what was approved in `privacy-consent.md`
- The app switcher and screenshots on sensitive screens — checked by opening the switcher, not by reading the config

**The surface nothing owns.**

- Dump the app's local storage on a real device and read it. Anything that would matter in a stolen backup belongs in secure storage
- The built Android manifest and `Info.plist` — not the config files: exported components, intent filters, and any cleartext-traffic exception each carry a stated reason or get removed
- Log output from a full real session: no token, no credential, no PII. A log that prints the request "for debugging" has published it to every log collector downstream
- WebViews, if any exist: what can be loaded into them, and whether JavaScript injection from loaded content reaches anything native

**The red audit.** Run the dependency audit `ci-cd.md` wired into every pull request, now, against the release lockfile. Every finding gets a fate — upgraded, patched, or accepted by a named person with the reason — never a warning scrolled past.

### Done when

- [ ] Every security box already ticked in `BUILD-PLAN.md` re-ran green on the release build
- [ ] A second authenticated account attempted the other user's rows, files, and endpoints — denied, walked one by one
- [ ] The storage dump from a real device was read, and nothing sensitive sits outside secure storage
- [ ] A captured session shows no token or unapproved PII leaving in analytics, crash reports, or logs
- [ ] The built manifest and `Info.plist` carry no exported surface or cleartext exception without a stated reason
- [ ] Sign-out leaves nothing of the previous account that the next sign-in can reach
- [ ] The dependency audit is clean, or every finding has a named owner and a fate
- [ ] Every finding of this sweep is fixed or accepted by name — none silently open
