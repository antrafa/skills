# Creating Your AGENTS.md

Generates the `AGENTS.md` that every later prompt relies on. Run it **after** `product-discovery.md` — the AGENTS.md is derived from `docs/PRODUCT.md`, not from a generic template.

---

## Prompt

Read `RULES.md` (this library) and `docs/PRODUCT.md` first.

Create an `AGENTS.md` in the project root, filled from `PRODUCT.md`. It is read before every task, so it must be accurate and short — **under 200 lines**. If you are tempted to add a section you cannot fill from `PRODUCT.md` or from the existing code, leave it out.

### Grill

- Is there an existing `AGENTS.md`, `CLAUDE.md`, or contributing guide to extend instead of replace?
- Anything the assistant should be forbidden from doing in this repo (touching migrations, editing generated files, running builds)?

### Sections to include

1. **Role and philosophy** — the expertise expected, and that clarity beats cleverness. One paragraph.
2. **Project overview** — copied from `PRODUCT.md`: what the app is, who it is for, stage (production / internal / prototype / learning). Core features as a bullet list.
3. **Domain vocabulary** — the terms from `PRODUCT.md`. State that code uses these names and nothing else.
4. **Tech stack** — only what is actually installed. Read `package.json`; do not list aspirational libraries. Add: "Do not introduce new major libraries without asking."
5. **Folder structure** — **inspect the repo and document what exists.** Do not paste a structure from a template. Note where routes, components, stores, types, services, and assets actually live.
6. **Development flow** — build feature by feature; smallest useful version first; read `PRODUCT.md` before coding; refactor only when repetition appears; refactors separate from behavior changes.
7. **Clarification policy** — when to ask instead of assume: missing domain decision, new dependency, destructive change, conflict between a prompt and installed docs. Give one example of the format.
8. **Styling** — the styling system in use, where design tokens live, and that tokens are the only source of colors and fonts.
9. **State** — what belongs in global state vs. local component state, and what gets persisted.
10. **Navigation** — the routing approach and grouping conventions in this repo.
11. **TypeScript** — no `any`; shared types exported from one place; states modeled as unions, not `string`.
12. **Error handling** — errors are part of the domain, not thrown strings; user-facing messages are actionable and never leak internals.
13. **Commits** — one logical change per commit; imperative subject; explain *why* in the body.

### Skeleton

```markdown
You are an expert React Native + Expo engineer helping build [app, from PRODUCT.md].

[Philosophy paragraph.]

## Project Overview
[What / who / stage.] Core features: [...]

## Domain Vocabulary
[Term → meaning. Code uses these names.]

## Tech Stack
[Only what is in package.json.] Do not introduce new major libraries without asking.

## Folder Structure
[What actually exists in this repo.]

## Conventions
[Styling · State · Navigation · TypeScript · Errors · Commits]
```

### Done when

- [ ] Every section is filled from `PRODUCT.md` or from inspected code — nothing invented
- [ ] The folder structure matches reality, verified by listing the repo
- [ ] The stack list matches `package.json`
- [ ] Under 200 lines

Update this file whenever the stack or structure changes — every prompt in this collection depends on it being true.
