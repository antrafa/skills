# Detail Screen

Full view of one entity, opened from a list or card.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Build the detail screen.

### Grill

- **Which entity?** Name it from `DOMAIN.md`. The route and file are named after it — not `[id].tsx` under a generic folder.
- Which fields belong on this screen, and in what priority? Take them from the entity definition; do not display every column because it exists.
- What is the primary action here — the thing this screen exists to enable (start, book, buy, complete, edit)?
- Are there secondary actions (save, share, delete)? Delete needs confirmation and a defined post-delete destination.
- Is the data already in the cache from the list, or must it be fetched fresh? If the list carries a partial entity, decide whether to render it immediately and refresh underneath, or wait.
- Can this screen be reached by deep link, with no list in the navigation stack? If yes, back must still work.

### Build

- A route under the entity's own path, receiving the id from route params and validating it — a malformed or missing id gets a real not-found state, not a crash
- Layout: hero/media if the entity has it, then title, metadata, body, then actions. Actions pinned to the bottom must respect the safe area
- Data from the same layer used elsewhere (React Query hook for this entity, store, or local content) — no new fetching pattern
- Scrollable content, with the header title handled by the navigator rather than duplicated in the body
- Restrained entrance motion; honor reduced-motion

### Every state, explicitly

Loading, error, and populated are decided in `DESIGN.md` — render them, skeleton matching the layout. Two states are detail-specific:

- **Not found / deleted** — a real message and a way back. This happens routinely via stale links and shared URLs
- **Action in flight** — the button shows progress and cannot be double-fired

### Done when

- [ ] Opened from the list and by direct deep link, both work — including back navigation from a cold start
- [ ] An invalid or deleted id shows not-found instead of crashing or hanging
- [ ] The primary action works and reflects its result without a manual refresh
- [ ] Destructive actions confirm first and navigate somewhere valid afterwards
- [ ] Long content and missing optional fields both render correctly
