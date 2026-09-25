# Privacy & Consent

Applies whenever the app ships to users in the EU (GDPR), Brazil (LGPD), or anywhere a comparable regime applies.

Run this **before** `analytics.md` and `error-tracking.md`, not after. An SDK that starts collecting at launch has already collected — device identifier, IP, session — before any consent screen renders, and that ordering is the violation. Retrofitting a dialog in front of an already-initialized SDK does not undo it.

Prereq: whoever owns the privacy policy at the organisation, and a network capture on a real device (proxy or on-device HTTP inspector) — this prompt cannot be verified from the simulator's console.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Gate every data-collecting SDK behind a consent decision that is read before the first paint, recorded, and revocable.

Whether consent is legally required here, and on what basis, belongs to the developer's counsel or privacy officer — this prompt states no thresholds, articles or penalties, and is not legal advice. The engineering question is the one it answers: once a basis is chosen, make the app actually behave that way. Get current requirements per `RULES.md` §3, or ask the developer for their organisation's existing policy and reuse it rather than inventing a second one.

### Grill

- **Which regions does this ship to?** Read the store availability and any geo-restriction already configured, then confirm it. This answer decides whether consent is required at all — if the app ships EU or BR, the rest of this list exists; if it genuinely ships neither, say so and stop here rather than building a gate nobody needs.
- **What is the legal basis for each collection purpose?** Ask it purpose by purpose: analytics, crash reporting, attribution, marketing. Specifically, is analytics being treated as *necessary* or as *consented*? Recommended default: consented — product analytics is rarely necessary to deliver the app, and calling it necessary is the assumption regulators look for first.
- **Which categories are actually collected?** Read the SDK list from `package.json` and present it, then have the developer confirm what each one sends and which purpose it serves. Intent is not evidence — an attribution or ads SDK pulled in as a transitive dependency collects whether or not anyone planned for it.
- **Is there a consent-management platform the organisation mandates, or is this built in-app?** **A)** a CMP the organisation already uses — inherit its categories and record format. **B)** in-app, backed by the app's own storage. Recommended default: B for a single app with three or four purposes; A only where it is mandated, because a CMP adds an SDK that itself collects.
- **Does consent follow the account across devices, or stay per-device?** **A)** per-device, stored locally — simplest, and the user is asked again on a new install. **B)** stored server-side against the account and synced. Recommended default: A when the app has no accounts; B where accounts exist and the user would reasonably expect one decision to hold, but the local copy still governs pre-login collection.
- **What is the retention period on each tool?** Ask per tool, then set it in the vendor console. An unset retention is whatever the vendor defaults to, which is usually far longer than anything the privacy policy claims.

### Build

**Deferred initialization**

- No analytics, attribution or crash SDK initializes until the consent state is known. Importing the module at the top of a screen is often enough to start it — check what the installed version does on import, not only on the init call.
- The stored decision is read before the first paint — add it to the boot list of the gate `app-shell.md` owns, never a second gate — which puts it in the same root-layout gate as auth and theme hydration. A gate that resolves one frame late is a frame of collection.
- A crash reporter is the common exception argued for. If it ships pre-consent, state exactly what it sends in that window — device model, OS, IP, stack frames, any user id — and get that decided by the policy owner rather than assumed because "crashes aren't personal data".

**The consent surface**

- Each purpose described in plain language and in the user's language (`i18n.md` if it applies): what is collected, what it is used for, who receives it. "To improve your experience" describes nothing.
- Granular per purpose where the regime requires granularity, not one all-or-nothing switch. Follow `DESIGN.md` for the surface's states.
- Reject as easy as accept — same visual weight, same number of taps, nothing pre-ticked, no decline hidden behind "manage options". A pre-ticked box or a buried decline is the classic finding.
- A refusal blocks nothing in the app unless the collection is genuinely necessary to the feature. Withholding function to extract consent is the other classic finding.

**Withdrawal**

- Reachable at any time from `settings-screen.md`, not only during onboarding, and it shows the current state per purpose.
- Withdrawal stops collection and deletes the local identifier and any queued-but-unsent events — flipping a boolean while the SDK keeps its device id and flushes its buffer is not withdrawal. Verify the effect on the wire, not the switch in the UI.

**The record**

- Persist what was consented to, per purpose, plus the version of the notice shown and a timestamp. Without a timestamped record against a notice version there is no proof consent was ever given, and no way to tell who needs re-asking when the notice changes.
- Changing the purposes or adding an SDK bumps the notice version and re-asks. Silently widening what an old "accept" covers is retroactive consent.

**Data-subject requests**

- Export: the user's own data in a machine-readable form, delivered through an authenticated path (`secure-backend.md`).
- Deletion: the same server-side deletion `profile-screen.md` builds — reference it, do not build a second path. Two deletion paths means one of them will be forgotten and keep the data.

**What is sent**

- No PII in event properties, no free-text user input in error context or breadcrumbs, no tokens or session identifiers anywhere in either. A crash report carrying the contents of a text field is a leak with a stack trace attached.
- IP and device-identifier handling stated per tool — truncated, dropped, or kept — and configured in the vendor console to match what the notice says.

**The declarations**

- What is decided here feeds the store privacy declarations in `store-compliance.md` and the privacy policy text. All three must agree with each other and with a real network capture. A declaration written from intent and contradicted by the capture is the version reviewers and regulators see.

### Done when

- [ ] On a fresh install with consent refused, a network capture shows nothing leaving for any refused purpose — including on cold start, backgrounding and crash
- [ ] Accepting one purpose and refusing another sends only the accepted one, verified by capture
- [ ] Withdrawing in Settings stops an already-running collection mid-session, verified by capture, and the local identifier is gone after restart
- [ ] The stored consent record contains purpose, notice version and timestamp, and bumping the notice version re-asks
- [ ] Export returns the user's data and deletion completes through the existing account-deletion path
- [ ] The categories declared in the store listing and privacy policy match the `package.json` SDK list and the capture, not the intent
- [ ] Every SDK's retention period is set explicitly in its console
