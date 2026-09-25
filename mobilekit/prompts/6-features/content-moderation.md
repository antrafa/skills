# User-Generated Content & Moderation

If any user can see content another user wrote, this prompt applies. It does not matter that the product calls it "comments", "a shared list", "notes on a booking" or "a display name — nobody will abuse that".

Not a feature request. Apple's review guideline for user-generated content requires four things: a mechanism to filter objectionable content, a way to report offensive content, a way to block abusive users, and published contact details for the developer. An app with UGC and none of these is rejected — and the rejection arrives after the build is submitted, not before.

Prereqs: accounts (`auth-clerk.md` / `auth-backend.md`) — reporting and blocking need an identity on both sides. Read alongside `store-compliance.md`.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Add reporting, blocking and moderation for user-generated content.

### Grill

- **What exactly is user-visible, and to whom?**
  - **A** — public: any user, signed in or not, can see it.
  - **B** — scoped: visible only inside a group, team or conversation the author belongs to.
  - **C** — private: only the author ever sees it. This is not UGC; stop here and record why.
  Answer per content type, not once for the app. A private journal with a public profile photo is still UGC.
- **Pre-publication or post-publication moderation?**
  - **A** — review queue: nothing is visible until approved. Genuinely safer, and needs a human staffing it every day, including weekends.
  - **B** — publish immediately, remove on report. Recommended default: it is what almost every app needs, and A is a commitment to a shift rota disguised as a checkbox.
- **Who reviews a report, and within what time?** Name a person and a target. "We'll look at it" with nobody named means reports accumulate unread and the next store review finds them.
- **Is automated screening in scope?** A moderation API for text and images, called server-side on the write path (`secure-backend.md` — the key never ships in the app). If yes: what is the threshold, and what happens to an author whose legitimate post is auto-hidden? Screening with no appeal path turns a false positive into a silently censored user who churns without telling you.
- **What happens to a blocked user's content that is already visible to the blocker?** Hidden retroactively, or only future content suppressed? Blocking that leaves yesterday's abuse on screen is not a block.
- **What happens to published content when its author deletes their account?** Deleted with them, anonymised, or retained as written — coordinate with `profile-screen.md`. Orphaned posts attributed to a ghost account are the default nobody chose.

### Build

**Report**

- A report action reachable from **every** surface that displays user content — feed row, detail screen, profile, comment, message, image. One missed surface is the one the reviewer taps.
- A short reason list drawn from what this product actually hosts, plus free text. Confirmation states what happens next and by when, so the reporter does not report the same item four times.
- The reported item and reporter recorded once — a repeat report from the same user is not four signals.

**Block**

- Bidirectional in effect: neither party sees the other's content, and neither can initiate contact. A one-way block leaves the abuser a working channel.
- Immediate in the UI. Existing content disappears on the current screen without a manual refresh, applied at the query layer so every list inherits it rather than each screen filtering by hand.
- Reachable from the same surfaces as report, and reversible from a visible list of blocked users (`settings-screen.md`).

**Moderation state**

- A state on the content entity — `visible | reported | hidden | removed` — belonging in `docs/DOMAIN.md` as a domain union. A boolean bolted on later cannot distinguish "hidden pending review" from "removed for cause", and every read path then guesses.
- Read paths filter on that state server-side. Filtering in the client means the content was already delivered to the device.

**Review and outcome**

- A review surface, even if it is a database view someone opens by hand. Say plainly in the report that it needs a named owner; an unstaffed queue is worse than none because it looks handled.
- Author-facing outcome when something is hidden or removed, naming the reason. Silent removal reads as a bug, and the author reposts.
- Automated screening, if in scope, on the write path server-side, with the human appeal route defined and reachable from the notice the author receives.

**Contact route**

- The developer contact the store requires, published where the store's reviewer can find it: the store listing, and a route in the app that does not depend on the user being signed in.

### Done when

- [ ] Report and block are reachable from every surface that shows user content — walked one by one on a device, not assumed
- [ ] Blocking removes the blocked user's existing content from the blocker's view immediately, with no refresh
- [ ] A submitted report lands somewhere a named person opens, and that person has opened it once
- [ ] A hidden or removed item's author is told, with a reason
- [ ] A hidden item is absent from the API response, not just from the rendered list
- [ ] Automated screening, if built, has an appeal path tested with a deliberate false positive
- [ ] The developer contact route is live and reachable from a signed-out state
