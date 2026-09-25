# Release Rollback

`post-release.md` defines the numbers that say a release is bad. This one defines what happens next. Write it before it is needed — a rollback improvised during an incident is how a bad release becomes a worse one.

Prereq: a production build shipped, and `post-release.md`'s four numbers agreed so there is a threshold to act on.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Write the rollback plan for this app and put the levers it names in place.

### Mobile has no rollback

A store binary already installed on a user's phone cannot be recalled. There is no "revert" — there is a set of levers with different reach and different latency, and knowing which lever reaches which users is the whole skill. In order of reach:

- **Over-the-air update** — the only fast lever. Reaches JS-only changes on installed builds within a launch or two, and only for users on the matching channel. It cannot undo a native change. The rollback is republishing the previous known-good bundle, which means that bundle has to be identifiable: a channel pointing at "latest" with no record of what was previous is not a lever, it is a hope.
- **Halting the store rollout** — stops new installs and staged distribution reaching more users. Does nothing for users who already updated.
- **Removing or reverting the store build** — slow, needs review for the replacement, and leaves the bad version installed on every device that already has it.
- **A server-side kill switch or remote flag** — the only lever that reaches an already-installed native build immediately. Which is the argument for the flag existing before the feature ships (`analytics.md` covers the flag mechanism).
- **Server-side fix** — often the fastest real remedy, because the bug is frequently in the API rather than in the app.

### Grill

- **Which of those levers exists today?** A channel with an identifiable previous bundle, a staged rollout actually in use, a remote flag mechanism already shipping. Answer per lever, from the repo and the consoles — a lever you assume you have is the one that fails at the worst moment.
- Who decides to pull the trigger, and who is allowed to execute it out of hours? One name each. "The team" means nobody acts for two hours.
- What threshold triggers action rather than observation? Take it from `post-release.md`'s four numbers — a crash-free drop of a stated margin, not "it looks bad".
- **Can the app be forced to update?** A: no gate, old builds keep working indefinitely. B: soft prompt, dismissible. C: hard minimum-version gate that blocks the app below a floor. Recommended default: B for features, with C available for a build that must die — a hard gate is the only way to retire a broken native build, and it is also the fastest way to lock out users if the floor is set wrong.
- What does a user on an unsupported build see? This is user-facing copy, so it is drafted and approved, not invented at incident time.

### Build

**Identity**

- Every release identifiable, with the OTA update identifier distinct from the store build number, so a bad update does not hide behind a healthy build number (`post-release.md`)
- The previous good bundle recorded and reachable by id — written down at publish time, not reconstructed from git during an incident

**Reach limits**

- A staged rollout as the default for production releases, so a bad release reaches a fraction of users first
- Update channels matched to build profiles, so the rollback republish lands where intended and nowhere else (`eas-build.md`)

**The runbook**

- A documented runbook naming the levers in order, each with the command or console path to pull it, and what it does *not* reach
- Kept in the repo where an on-call person finds it — not in a chat thread, not in someone's notes

**Version gating**

- A minimum-supported-version gate with a screen that tells the user what to do, with the store link. A blank failure or a spinner on an unsupported build reads as "the app is broken"

**Migrations, in reverse**

- Data migrations considered backwards: a persisted store or a schema migrated forward cannot always be read by the previous build. A rollback into an unreadable local store is a second incident, and it hits exactly the users you were trying to rescue (`zustand.md`, `domain-model.md`)
- Where a forward migration is not reversible, say so in the runbook and name what the rollback path is instead

**Afterwards**

- A post-incident note recording which lever was used, how long it took, and what it cost. The next incident is judged against it

### Done when

- [ ] The runbook exists in the repo and someone who did not write it can follow it end to end
- [ ] An OTA rollback rehearsed on a preview channel — republished and confirmed on a device, not theorised
- [ ] The previous good bundle is identifiable by a recorded id, produced without guessing
- [ ] The last production release used a staged rollout
- [ ] The minimum-version gate tested by pinning a device below the floor, showing the real screen with a working store link
- [ ] Forward migrations checked for whether the previous build survives them, with the answer written down
- [ ] Decision-maker and out-of-hours executor named, with the acting threshold stated in numbers
