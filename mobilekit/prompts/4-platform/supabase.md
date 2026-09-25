# Supabase Setup

Wire Supabase in as the backend. Run `domain-model.md` first — the schema decision belongs there, not here.

Prereq: a Supabase project (https://supabase.com).

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Integrate Supabase into this Expo app.

### Grill

- Which parts are actually needed now: database, auth, storage, realtime? Configure only those.
- Does `DOMAIN.md` record scenario A (new schema) or B (existing tables)? If neither exists yet, stop and run `domain-model.md`.
- Is `SUPABASE_SERVICE_ROLE_KEY` needed anywhere? If yes, that code goes in an API route or backend — **never** in the app. The anon key is the only key that ships.

### Build

**Client** — one module creating the client from `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_ANON_KEY`.

Session persistence needs a storage adapter, and the correct one depends on the installed `@supabase/supabase-js` version — check its React Native docs (RULES.md §3) for the current adapter shape and options. Two things to get right regardless of version:

- Use `expo-secure-store` for the session, not AsyncStorage. SecureStore has a value-size limit; if a session exceeds it, the write fails silently and the user is logged out on next launch — verify a real session round-trips.
- Disable URL-based session detection; it is a web concern.

**Auth** — only if Supabase Auth is the chosen provider. Details in `auth-backend.md`; do not build a second auth path here.

**Types** — generate from the live schema with the Supabase CLI and commit the output. Check the current `gen types` command for the installed CLI version. Treat the generated file as read-only and import app-facing types from `types/` (per `domain-model.md`), not from the generated file directly.

**Data access** — one typed function per operation the screens in `PRODUCT.md` actually need, named for the domain entities from `DOMAIN.md`. Do not scaffold generic CRUD for entities nothing reads yet. Return errors as values so callers can distinguish "not found" from "offline".

**Storage** — only if chosen in the grill. One bucket per content class, each with its access model stated: public read, or private with signed URLs. Policies verified the same way as RLS — fetch another user's file and be denied. The upload flow itself belongs to `media-upload.md`; build only the buckets and policies it will need.

**Realtime** — only if chosen in the grill. Subscriptions tie to screen lifecycle: subscribe on mount, unsubscribe on unmount, or every visit to the screen leaks a channel. Confirm private channels are backed by RLS on the underlying table — realtime bypasses nothing, but an open table broadcasts to anyone.

**Authorization** — confirm RLS is enabled with policies on every table holding per-user data, and state which tables are intentionally public. The anon key is in the bundle: without RLS, every row is readable by anyone who extracts it. If `domain-model.md` already wrote the policies, verify them rather than rewriting.

### Done when

- [ ] A real query returns data from a device with only the anon key present
- [ ] RLS verified by attempting to read another user's row and being denied
- [ ] Session survives an app restart
- [ ] Generated types committed; no hand-written table types
- [ ] Nothing but the anon key exists in the app bundle
- [ ] Where storage was configured: a file belonging to another user is unreachable
- [ ] Where realtime was configured: leaving the screen closes its channel, verified in the dashboard
