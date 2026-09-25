# React Query (TanStack Query)

Server-state fetching, caching, and mutations. Skip if `PRODUCT.md`'s data scenario is D (local content only) — there is nothing to cache yet.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Set up TanStack Query for this app's server data.

Reference for the installed major: https://tanstack.com/query/latest/docs/framework/react/react-native (check `package.json` first).

### Grill

- Which data in `DOMAIN.md` comes from the server? Only that gets query hooks.
- Does the app need offline reads (`PRODUCT.md`)? If yes, cache persistence is part of this step, not an afterthought — ask before adding the persistence package.
- Is there pagination, and is it page-based or cursor-based? The hook shape differs; get it from the real contract.
- How stale can each kind of data be? Reference data and user-specific data rarely want the same `staleTime`.

### Build

**Client** — one query client with defaults chosen deliberately: `staleTime` per the answers above, a bounded retry count, and no retry on 4xx (retrying a 404 or a 401 wastes a round trip and delays the error the UI needs). Provider in the root layout, above anything that queries.

**React Native specifics** — these are missing from most copied setups and cause "stale data until I force-refresh" bugs:

- Wire refetch-on-focus to `AppState` rather than browser window focus, via the library's focus manager
- Wire online status to the device's network state via the library's online manager, so queries pause offline and resume on reconnect
- Configure both once, next to the client

**Query layer, per entity from `DOMAIN.md`** — one hook file per entity, using the domain names, never `useItems`:

- Query keys structured hierarchically (entity, then id or filters) so invalidation can target a subtree instead of clearing everything
- Dependent queries gated with `enabled` so nothing fires with an undefined id
- Mutations that invalidate the narrowest key that could have changed. Optimistic updates only where the latency is actually felt, and always with a rollback path
- Auth: the token comes from the auth layer at request time, not captured at hook creation, or it goes stale after refresh

**Cache persistence** — only if offline reads were chosen in the grill. Persist the query cache with the persister the installed major documents, version the cache so a shape change invalidates it instead of rendering stale structures, and clear it on sign-out — the next account on this device must not see the previous account's data.

**Consumers** — every screen handles loading, error, empty, and success. Empty is not an error state and deserves real copy plus a next action (see `ui-components.md`).

### Done when

- [ ] Data loads on a device; backgrounding and returning refetches when stale
- [ ] Airplane mode: queries pause, the UI says so, and reconnecting recovers without a restart
- [ ] A mutation updates the screen without a manual reload, and a forced failure rolls back
- [ ] Hook and key names use `DOMAIN.md` vocabulary — no generic `Item`
- [ ] No screen renders `undefined` while loading
- [ ] Where persistence was chosen: a cold start in airplane mode renders cached data, and signing out clears it
