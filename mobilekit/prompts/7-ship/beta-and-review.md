# Beta Distribution & Store Review

The step between a build and the public: real testers first, then the review process — planned as a loop, not an event. Run it once `eas-build.md` produces installable builds, with `store-compliance.md` already passed; everything that prompt catches is cheaper before a reviewer sees it.

A first submission that comes back rejected is the normal case, not the failure case. Everything below assumes it.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Put the app in testers' hands, then take it through store review.

### Grill

- **Who tests, on what?** Recommended default: TestFlight internal and Play internal track with the team first, then a named external group — real users on both platforms, including at least one old low-end Android — before the public. The developer's own phone is not a beta. If `docs/LAUNCHES.md` exists (`market-signal.md`), its responders are the first external invitees — they asked for this build — and the invite's outcome is logged there.
- **What must the beta answer before go?** Recommended default: crash-free rate holding at the threshold `post-release.md` will watch, and at least one tester who was never shown how reaching the success action — the activation path `DESIGN.md` records is the pass bar. A beta with no exit criteria runs forever.
- **How does feedback come back?** Recommended default: the store's built-in feedback plus one named channel, triaged by one owner. Feedback nobody owns is feedback nobody reads.
- **Who answers the reviewer?** One name with access to the store consoles, checking daily while a submission is in review. Rejections carry reply deadlines; a message nobody sees becomes an abandoned submission.

### Build

**Beta tracks**

- iOS: TestFlight internal (instant), then external (light review). Android: internal testing, then a closed track. Both wired to the profiles from `eas-build.md`, so testers run the build that will ship — not a divergent one
- Error tracking and analytics live in beta builds; a beta crash that reports nothing teaches nothing (`error-tracking.md`)
- A tester-facing note per build: what changed, what to try

**Submission**

- Review notes written for a stranger in a hurry: the demo account from `store-compliance.md`, where the gated features live, and anything needing a second device or a real phone number explained up front
- Staged rollout (Android) and phased release (iOS) on for the first production release — going straight to 100% is a decision `release-rollback.md` gets a say in

**The rejection loop**

- A rejection cites a guideline: read the guideline itself, not only the reviewer's summary, and reproduce the problem before fixing it. Reviewers are sometimes wrong — a factual reply in the resolution center, with evidence, is a legitimate response
- Disagreement goes through the resolution center or a formal appeal, once. Resubmitting unchanged builds repeatedly is what escalates to worse outcomes
- Each rejection and its resolution recorded in a `docs/` note, so the next submission does not rediscover it

### Done when

- [ ] A build reached a tester's device through each store's beta track, not by cable
- [ ] Beta crashes and feedback arrive somewhere with a named owner — verified by one real report making the round trip
- [ ] The beta's exit criteria are written down, with the numbers that must hold
- [ ] Review notes let a stranger reach every gated feature in under a minute — tested on a colleague
- [ ] The first production release is staged/phased, with the starting percentage and who advances it recorded
