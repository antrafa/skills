# Store Submission Compliance

Run before the first submission to either store, and again whenever an SDK, a tracker, or a permission is added. `eas-build.md` produces the binary; this decides whether the binary is accepted.

Prereqs: an Apple Developer account and a Play Console account, a real build from `eas-build.md`, and a physical device to sign into it from.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Prepare this app for store review and fix everything that would get it rejected.

**Store policy is the moving part of this prompt.** Every item below names a concern, never a current rule. Resolve each one's actual requirement per `RULES.md` §3, against the store's own policy or form the day you submit. Never state a form field, threshold, asset size, or category name from memory: a stale checklist confidently followed is worse than no checklist.

### Grill

- **Does anything in this app use an identifier for advertising or cross-app measurement?** **A** — nothing, analytics is first-party and product-only. **B** — an attribution SDK, to measure where installs come from. **C** — an ad network SDK. Recommended default: **A**, because B and C both pull in the iOS tracking prompt, a consent obligation, and a declaration that has to stay true. B and C are marketing decisions, not build decisions — the developer owns them.
- **Who supplies the reviewer account, and where does its second factor arrive?** **A** — a dedicated review account with no second factor, restricted to demo data. **B** — a shared TOTP seed handed over in review notes. **C** — a real account with SMS or email codes. Recommended default: **A**; C is a guaranteed rejection, because the reviewer cannot receive the code.
- Where does the privacy policy live, who maintains it, and does it already name the data this app actually sends? A URL that 404s, or one that describes a different product, fails review.
- **Age rating:** what does the app actually contain — user-generated content, unmoderated messaging, gambling, alcohol, medical or financial advice? Answer against the shipped feature set, not the intended positioning.
- If anything is bought: is it digital (unlocks, subscriptions, credits) or physical (goods, shipped items, in-person services)? The two have opposite obligations and the wrong choice is a rejection either way.
- Does the app use encryption beyond the platform's standard HTTPS? This is an export-compliance answer with legal weight; the developer answers it, not the agent.
- Who approves the listing copy and screenshots before send?

### Build

**Privacy declarations**

- Produce the iOS privacy manifest from the actual dependency list: what data the app collects, why, and each required-reason API the app or any bundled SDK touches. A missing or incomplete manifest is a build-time rejection at upload, not a review note — it never reaches a human.
- Check which third-party SDKs are themselves required to ship a manifest, and confirm the installed versions do. An SDK that does not blocks your upload, and the fix is upstream.
- Fill the Play data-safety declaration from what the app **sends**, not what the developer intends it to send. Crash reporters, analytics, and ad SDKs collect on their own schedule and their defaults are usually broader than expected.
- **Bind both declarations to `package.json`.** Enumerate every SDK, resolve what each one transmits, and record the mapping. Analytics added in a later sprint without updating the declaration turns a true declaration into a false one, and a false declaration is a removal, not a correction.

**Tracking and consent**

- iOS tracking permission is required when an identifier is used for advertising or cross-app measurement. Its copy, its timing, and what the app does on refusal are decided here and wired through `privacy-consent.md` — one consent state, not a prompt per SDK.
- The app must remain fully functional when tracking is refused. A feature gated on consent is a rejection.
- Declaring no tracking while shipping a tracker is the fastest route to removal. If the answer to the attribution question was B or C, the declaration, the prompt, and the SDK's own default configuration all have to agree.

**Required app content**

- A reachable privacy policy URL, in the listing and in the app. Both stores require it and a 404 fails review.
- In-app account deletion wherever the app has accounts — reachable without contacting support, and it must actually delete, not just sign out (`profile-screen.md`).
- Where users post or message: the reporting, blocking, and moderation mechanisms from `content-moderation.md`, all reachable in the submitted build. Terms alone are not a mechanism.
- A restore-purchases action if anything is bought (`in-app-purchases.md`). A user who reinstalls and loses a paid subscription files both a refund and a review.
- Digital goods go through store billing; physical goods and real-world services must not. Routing digital unlocks to an external processor, or store billing to shipped goods, both get rejected.

**The review submission**

- A working reviewer account, credentials in the submission fields, verified by signing in on a clean device — not a simulator, and not one already authenticated.
- Review notes explaining anything that looks broken without context: a feature behind a paywall, a region lock, a hardware or peripheral dependency, a flow that needs a code from a partner system.
- Demo data seeded on that account, so a stranger opening the app does not see an empty shell. Empty screens read as a broken app.
- Age rating and content questions answered honestly against what the app contains, including anything users can post into it.
- Export-compliance and encryption answers recorded, matching the answer from the grill.

**Listing and assets**

- Screenshots captured from the build being submitted, at the sizes the store currently requires, on real devices — not mockups, not a marketing render. A screenshot showing a feature that is not in the build is a rejection.
- Icon with no transparency, no placeholder, no rounded corners baked in, at every required size.
- Name, subtitle, and description describing what the app does. Keyword stuffing and a description promising a feature that does not exist are both rejections.

### Done when

- [ ] Both privacy declarations generated from the actual `package.json` SDK list, then cross-checked against a network capture of a real session — every host seen is accounted for
- [ ] The privacy policy URL loads, from a device, and matches the declarations
- [ ] The reviewer account signed into successfully from a clean device, second factor included or absent by design
- [ ] Every store-required in-app mechanism — deletion, restore, report, block — reached by tapping through the submitted build
- [ ] Screenshots and icon taken from the build being submitted, at the sizes verified against the current store requirement
- [ ] Tracking refused on a real device, and the app still fully usable
- [ ] Every answer given on the developer's behalf listed in the final report, for review before send
