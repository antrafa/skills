# Product Discovery (run this first)

Every other prompt in this collection assumes it already knows what you are building. This one is what makes that true.

Run it **before** `agents-md.md`. Its output — `docs/PRODUCT.md` — is what the AGENTS.md, the domain model, and every screen prompt read instead of guessing.

---

## Prompt

Read `RULES.md` (this library) first.

You are running a product discovery interview before any code is written.

### Hard rules

`RULES.md` §1 owns the interview mechanics — one question per message, a stated default per question ("Default: single welcome screen — confirm or change"), one follow-up for a vague answer, `UNDECIDED — ask before assuming` for anything left open. The blocks below are the grill, not a questionnaire to hand over. On top of that:

1. **Do not write application code, do not install packages, and do not create any file other than `docs/PRODUCT.md` until this interview is complete.**
2. **Never infer the domain from the app name, the folder name, or an existing template.** A repo scaffolded from a tutorial tells you nothing about the product being built.

### Block A — Product and user

1. In two sentences: what does this app do, and for whom?
2. What does the user get out of it that they cannot get today?
3. Is this a production app, an internal tool, a prototype, or a teaching project? (This changes how much error handling, analytics, and polish is justified.)

### Block B — The central object (most important block)

Most of this collection's prompts talk about generic `items`. Replace that now.

4. What is the **one thing** this app is mostly about? (a lesson, a workout, a job posting, an invoice, a plant, a match)
5. What does the user *do* to it? (create, browse, complete, book, compare, track over time)
6. What is the real vocabulary of this domain? List the 3–7 nouns you would use talking to a colleague, and how they relate to each other.
7. Does one of these objects contain another? (e.g. course → module → lesson)
8. Is any of this content **authored by you** (curated, shipped with the app) or **created by users**? Both?

Record these nouns verbatim. From here on, code uses these names — never `Item`, `Data`, or `Record`.

### Block C — Core journey

9. What are the 3 screens without which the app is pointless?
10. Walk through the first session of a brand-new user, screen by screen.
11. What is the single action that means "this app worked"? (completed a lesson, sent an application, logged a meal)

### Block D — Data and backend

12. Does the data already live somewhere? Pick one:
    - **A — Nothing exists yet.** The schema will be designed from scratch.
    - **B — Tables already exist** in a database you control.
    - **C — Data comes from an API or database you cannot change** (third-party, legacy, another team).
    - **D — No backend yet.** Ship local/hardcoded content first, add a backend later.
13. If B or C: how do I inspect it? (connection string, Supabase project, OpenAPI spec, sample payload, read-only credentials)
14. Does content differ per user, or does everyone see the same content?
15. Does the app need to work offline?

Do not design any schema here. Stop after recording the answers and hand this to `domain-model.md`.

### Block E — Identity

16. Do users need accounts at all? If not, say so — skip auth entirely.
17. If yes: managed provider (Clerk, Supabase Auth) or your own backend? Which sign-in methods?
18. Are there different roles or permission levels?

### Block F — Capabilities (ask, do not assume)

For each: needed **now**, needed **later**, or **never**?

19. Payments or subscriptions — and if yes, digital content (app store rules apply) or physical goods/services? Marked "now", or the developer unsure how the app should earn → `monetization.md` runs after this interview and decides the model.
20. Push notifications — and what would actually trigger one?
21. AI / LLM features — and does it need real-time voice/video, or is request/response enough?
22. Analytics and error tracking.
23. Multiple languages in the UI (i18n).
24. Dark mode.
25. Media upload (camera, photos, audio).
25b. Links that open the app from outside it — shared links, email, notifications (`deep-linking.md`).

Anything marked "never" gets no prompt run and no dependency installed.

### Block G — Constraints

26. iOS, Android, or both? Web too?
27. Is there an existing design (Figma, screenshots, a brand palette), or should the design system be proposed from scratch?
28. Any technology already decided, mandated, or forbidden?
29. Are there constraints from an existing codebase (folder layout, conventions) I should inspect before proposing structure? If a project already exists, **read it** — do not assume the layout in this collection's examples (`app/` vs `src/app/`, presence of `tailwind.config.js`, etc.).

---

## Output

Write `docs/PRODUCT.md` with exactly this structure, filled from the answers:

```markdown
# Product Definition

## What this is
[2 sentences] · Audience: [...] · Stage: [production | internal | prototype | learning]

## Domain vocabulary
| Term | Meaning | Relates to |
|---|---|---|
| [Lesson] | [...] | [belongs to Unit] |

Central object: [...]
Content ownership: [authored | user-generated | both]

## Core journey
1. [...]
Success action: [...]

## Data
Scenario: [A new schema | B existing tables | C external/immutable source | D local-only for now]
Access: [how to inspect it]
Per-user data: [yes/no] · Offline: [yes/no]

## Identity
Accounts: [yes/no] · Provider: [...] · Methods: [...] · Roles: [...]

## Capabilities
| Capability | Now | Later | Never |
|---|---|---|---|
| Payments | | | x |

## Constraints
Platforms: [...] · Design source: [...] · Mandated/forbidden tech: [...]
Existing codebase conventions: [what you found by reading it]

## Open questions
- [UNDECIDED — ask before assuming]
```

Keep it under 100 lines. It is read before every task, so it must stay skimmable.

---

## After this

- If the app earns money — or that is still open — run `monetization.md`: it decides the model and appends the `## Monetization` section.
- Want proof anyone wants this before building it? `market-signal.md` puts the pitch in front of real people — the win is one reply — and starts `docs/LAUNCHES.md`. Optional, and cheapest right now.
- Run `agents-md.md` — build the AGENTS.md **from** `PRODUCT.md`, not from a generic template.
- Run `domain-model.md` — turn the domain vocabulary into types and, if needed, a schema.
- Every later prompt: read `docs/PRODUCT.md` first. If a prompt needs a decision that is `UNDECIDED` there, **ask, then update `PRODUCT.md`** — do not decide it inline and move on.
