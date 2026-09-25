# Domain Model & Data Layer

This is the prompt that replaces the generic `Item` / `useItems()` / `/items` scaffolding that every other prompt in this collection falls back on.

Run it **after** `product-discovery.md` and **before** `supabase.md`, `react-query.md`, or any screen prompt. Screens built before the domain exists get retrofitted later, and that retrofit is the most expensive rework in the whole build.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first and follow them strictly.

Define this app's domain model and data access layer.

### Hard rules

Naming and invention are owned by `RULES.md` §2 and §5 — domain vocabulary only, nothing unconfirmed. On top of them:

1. **Show the model and get approval before writing migrations or generating files.** Present it as a table first.
2. No `any`. Every field gets a real type, and optionality is a decision, not an accident.
3. Destructive schema changes (drop, rename, type narrowing, `NOT NULL` on populated columns) are **never** applied without explicit confirmation, and never without a rollback path.

### Step 0 — Confirm the scenario

Read the `Data → Scenario` line in `docs/PRODUCT.md` and state it back before proceeding. If it is missing or ambiguous, ask which one applies:

- **A** — Nothing exists yet; design the schema.
- **B** — Tables already exist in a database we control.
- **C** — Data comes from a source we cannot change.
- **D** — No backend yet; local content first.

Then follow only that scenario's section.

---

## Scenario A — New schema

1. **Derive candidate entities** from the domain vocabulary. Present, for approval, one table per entity:

   | Field | Type | Null? | Notes |
   |---|---|---|---|

   Plus a relationship list (`Lesson.unit_id → Unit.id`, one-to-many) and, if there are more than three entities, a short text diagram of how they connect.

2. **Ask before deciding**, do not default silently:
   - Surrogate `uuid` key or a natural key that the domain already has?
   - Which entities are per-user (need an owner column) vs. shared/authored content?
   - Does anything need history — "when did this change" — or is current state enough?
   - Is delete real or reversible? Only add soft delete if something in the product actually needs to restore or audit.
   - Which enums are fixed forever (DB enum / check constraint) vs. likely to grow (lookup table)?

3. **Then write the migration**, as a versioned file — not ad-hoc SQL run against a live database:
   - Primary keys, foreign keys with an explicit `ON DELETE` decision per relation.
   - `created_at` / `updated_at` on every table unless there is a reason not to.
   - An index on every foreign key, plus one on each column the screens in `PRODUCT.md` will filter or sort by. Name the screen that justifies each index.
   - A `down` / rollback for every migration.

4. **Row-level authorization.** If any data is per-user, this is not optional and not deferrable:
   - Postgres/Supabase: enable RLS on those tables and write the policies in the same migration that creates them. A table with per-user data and no policy is a data leak, not a TODO.
   - Custom backend: the ownership check goes in the query layer, and no endpoint accepts a caller-supplied owner id.
   - State plainly which tables are intentionally public/read-only-for-all.

5. **Apply**: run against local/dev first, confirm it is reversible, and ask before touching a shared or production database.

6. Generate types **from the applied schema**, not by hand (see *Types* below).

---

## Scenario B — Existing tables

1. **Inspect before proposing anything.** Use whatever access `PRODUCT.md` recorded — a database MCP tool, `psql`, the Supabase dashboard, or `information_schema` queries. Report what you actually found: tables, columns, types, nullability, keys, indexes, constraints, and row counts.

2. **Confirm scope.** List the tables you found and ask which are in scope for this app. Legacy databases contain tables that belong to other systems; touching them is out of bounds.

3. **Map, do not redesign.** Produce a mapping table:

   | DB column | TS field | Type | Notes |
   |---|---|---|---|

   Where the DB naming does not match the product vocabulary, keep the DB name in the mapping layer and use the product name in the app — do not rename columns to make the app prettier.

4. **When something the app needs is missing**, do not silently work around it and do not fold it into another change. Say which field is missing and which screen needs it, then propose it as a **separate additive migration** (new nullable column or new table, backfill strategy stated) and wait for approval. Additive is allowed to be proposed; altering or dropping existing columns is not, without explicit sign-off.

5. **Check what already enforces integrity.** If constraints, triggers, or views exist, the app respects them rather than duplicating or bypassing them.

6. Generate types **from the live schema** (see *Types*). Hand-written types drift from the database within a week.

---

## Scenario C — External / immutable source

1. **Get the real contract** before writing a single type: OpenAPI/GraphQL schema, or at minimum a captured response payload per endpoint. Ask for it. Do not model from prose descriptions or from a guess at what the API "probably" returns.

2. **DTO is not the domain.** Create two layers and keep them apart:
   - `types/dto/` — mirrors the external payload exactly, including its awkward names, string-typed dates, and nullable-everything.
   - `types/` — the app's own model, using the product vocabulary.
   - `services/<source>-mapper.ts` — the only place that converts between them.

3. **Validate at the boundary.** The external response is untrusted input: check it where it enters the app, and fail with a clear domain error rather than letting `undefined` reach a screen. If a schema-validation library is already installed, use it; if not, ask before adding one — hand-written guards are fine for a handful of endpoints.

4. **Record the limits** in `docs/DOMAIN.md`: what the source cannot do (no filtering, no pagination, rate limits, eventual consistency), because those limits will decide screen behavior later.

5. If some data is ours and some is theirs, say explicitly which fields live where, and how they are joined.

---

## Scenario D — Local content first

1. Define the types in `types/` from the product vocabulary, exactly as they would look with a real backend.
2. Put authored content in `data/`, typed against those types — no untyped JSON blobs.
3. Ship a small, honest sample: enough breadth to exercise every screen state (including empty and long-text cases), not a placeholder single row.
4. Access it through the same function shapes a real backend would use (`getX()`, `getXById()`), so the swap later is an implementation change, not a screen rewrite.
5. Record the swap point in `docs/DOMAIN.md`: which files change when the backend arrives, and what does not.

---

## Types (all scenarios)

- Where a schema exists, generate types from it and treat the generated file as read-only output. For Supabase this is `supabase gen types` — check the current command and flags for the installed CLI version (RULES.md §3).
- Re-generate whenever the schema changes, and commit the result so type errors surface in review.
- Export the app's own model types from one place; screens import from there, never from the generated file directly.
- Model states the domain actually has. If something is `draft | published | archived`, that is a union type, not a `string`.

## Sample / seed data (all scenarios)

Development should not depend on a populated remote database.

- Provide typed fixtures that cover: empty, one, many, longest realistic text, and every status value.
- Keep them in one place, importable by both screens-in-progress and tests.
- Make it obvious which code path is fixtures vs. real data, and how to switch.

## Output

- `types/` — the domain model, named from `PRODUCT.md`
- `types/dto/` + a mapper — scenario C only
- migration file(s) with rollback — scenario A, and additive-only for B
- `data/` fixtures or authored content
- `services/` access functions per entity, typed, with errors as part of the return contract rather than thrown strings
- `docs/DOMAIN.md` — the approved entity tables, the relationships, the scenario, row-level authorization decisions, known limits of the source, and the mock→real swap point

### Done when

Before saying this is done, verify and report:

- [ ] Every type name appears in `docs/PRODUCT.md`'s vocabulary
- [ ] No `any`, no generic `Item`
- [ ] Every relationship has an explicit cardinality and delete behavior
- [ ] Every per-user table has an enforced authorization rule, named in `docs/DOMAIN.md`
- [ ] Every migration has a rollback
- [ ] Nothing was invented: each field traces to `PRODUCT.md`, an inspected schema, or a real API contract
- [ ] Fixtures cover empty / one / many / long / all statuses
- [ ] `docs/DOMAIN.md` written, and `docs/PRODUCT.md` updated if the interview answered anything new

State anything you had to assume. If the list is not empty, ask before continuing to screens.
