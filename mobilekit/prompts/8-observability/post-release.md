# Post-Release Observability

`analytics.md` and `error-tracking.md` install the instrumentation. This one decides **what you actually look at once the app is in users' hands**, and what wakes someone up.

A dashboard with every event on it is the same as no dashboard. Run this after the first production build reaches real users — not before, because you cannot set a threshold on a number you have never seen.

Prereq: analytics and error tracking already shipping data from a production build.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Define what this app is monitored on after release.

### Grill

- Has a production build actually been out long enough to produce a baseline? If not, stop — set the instrumentation up, ship, and come back. Thresholds invented before data are noise generators.
- Who is on the receiving end of an alert, and through what? An alert nobody reads is worse than no alert: it trains the team to ignore the channel.
- What is the realistic response? If nothing can be done at 3am, it is a morning report, not a page.

### The four numbers

Everything else is diagnostic. These four are the ones checked without being asked:

1. **Crash-free session rate** — from the error tracker's release health. This is the single number that says whether the last build is safe. Set the alert on a *drop relative to the previous release*, not an absolute floor.
2. **The success action, per day** — the action `PRODUCT.md` names as "this app worked". If this falls and nothing crashed, something in the funnel broke silently, which is worse.
3. **Drop-off at the worst funnel step** — from the funnel built in `analytics.md`. Watch the step, not the total.
4. **New unhandled error types in the current release** — a *new* signature matters; a known one at stable volume does not.

Present these four with the number each is at today. If any cannot be produced, say which instrumentation is missing rather than substituting a proxy.

### Release health

- Every release is tagged with `release` and `dist`, or none of this is attributable to a build. Verify this against a real production event, not the config.
- Compare crash-free rate and success-action rate **between the current release and the previous one**. A regression is the comparison, never the absolute value.
- Over-the-air updates change the running code without changing the store build. Confirm the release identifier moves with the OTA update, or a bad update hides behind a healthy build number.

### Alerts

Three at most, to start:

- Crash-free rate drops more than a chosen margin below the previous release
- The success action drops sharply against its own recent baseline
- A new error signature crosses a volume threshold in the current release

For each: state the threshold, where it fires, and **what the responder does**. An alert with no next step gets muted within two weeks.

### Privacy

- Re-check what is actually being sent now that real users are in it: no PII in event properties, no free-text user input in error context, no tokens in breadcrumbs.
- Confirm the retention setting on both tools is deliberate rather than default.

### The loop back

- A confirmed production error becomes a fix, and the fix references the issue. Errors that stay open across three releases are either not real or not owned — decide which.
- When a funnel step is confirmed broken, the fix ships behind the same event, so the same number proves it recovered.
- When the plan is empty and the question becomes "what next?", these four numbers are the input — `next-feature.md` turns them into the next cycle of `BUILD-PLAN.md`.

### Done when

- [ ] The four numbers are visible in one place, with today's value recorded as the baseline
- [ ] A production event carries the correct release and dist, verified on a real build
- [ ] Current release compares against the previous one, not against an absolute target
- [ ] At most three alerts exist, each with a named responder and a stated next step
- [ ] OTA updates are distinguishable from store builds in the release data
- [ ] No PII confirmed against real production data, not against the config
