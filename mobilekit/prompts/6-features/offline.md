# Offline Support

Skip unless `PRODUCT.md` says the app must work offline. Mobile networks are unreliable regardless, so the honest-degradation section applies to every app.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Add offline support.

### Grill — this is the question that decides the cost

- **Read-only offline, or offline writes too?**
  - **Reads** — cache what was already fetched and show it when disconnected. Moderate work, no conflicts.
  - **Writes** — a mutation queue, conflict resolution, and merge rules. An order of magnitude more work, and the source of the hardest bugs in mobile apps. Only build it if the product genuinely requires acting while disconnected.
- Which entities from `DOMAIN.md` need to be available offline? Usually a subset, not everything.
- How stale may cached data be before it should be hidden rather than shown?
- **For writes:** what happens when the same record changed on both sides? Last-write-wins is a decision with data loss attached, not a default — get it chosen explicitly, per entity if necessary.
- Is any offline data sensitive? Cached-on-device means readable on a compromised device.

### Build

**Honest degradation (every app)**

- Detect connectivity and wire it into the data layer, so queries pause offline and resume on reconnect (see `react-query.md`)
- A visible, non-blocking indicator when offline. Never a spinner that spins forever
- Actions requiring the network are disabled or clearly explained, not silently failing
- Recovery on reconnect without requiring a restart

**Cached reads**

- Persist the cache for the chosen entities, with an explicit size bound and an eviction policy
- Show the data with its age when it is stale, rather than pretending it is current
- Clear cached user data on sign-out — the next user on the device must not see it

**Queued writes (only if confirmed)**

- A durable queue surviving app restarts, drained in order on reconnect
- Every queued mutation carries an idempotency key, so a retry after an ambiguous failure does not duplicate the record
- Optimistic local state showing the item as pending, with rollback on permanent failure
- Conflict resolution as decided above, and a visible outcome when a change is rejected. Discarding a user's edit silently is the worst possible behavior here
- A bounded retry policy: distinguish "offline, retry later" from "server rejected this, stop"

### Done when

- [ ] In airplane mode: cached screens render, uncached ones explain themselves, and nothing hangs
- [ ] Reconnecting recovers without a restart
- [ ] Writes, if queued: created offline, restarted the app, reconnected — the record lands exactly once
- [ ] A forced conflict resolves as decided and the user is told
- [ ] A server-rejected mutation stops retrying and surfaces the reason
- [ ] Sign-out clears cached user data
