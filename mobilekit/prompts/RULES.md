# Prompt Rules

Read this before every prompt in this library. It is the single source of truth for how prompts are run — `SKILL.md` and `AGENTS.md` point here rather than restating it.

It exists because the common failure is not bad code. It is an assistant deciding something the developer never chose, or applying setup steps from a version that no longer exists.

## 1. Grill, one question at a time

Most prompts carry a `### Grill` block; `product-discovery.md`, `monetization.md` and `design-conception.md` are one from end to end. Wherever the questions are, work down them **one per message**, waiting for the answer before asking the next. Six questions asked at once are six questions answered badly.

- **Recommend an answer to every question**, in one line, with the reason. The answer can then be a confirmation instead of an essay.
- **A fact is looked up, never asked.** Installed version, folder layout, whether `babel.config.js` exists, which tables the database has, what `PRODUCT.md` already says — read it. Spending the developer's attention on something you could have read is the fastest way to lose it.
- **A decision is asked, never taken.** Provider, palette, schema shape, what sits behind a paywall, how conflicts resolve. Where a prompt lists Option A / B / C, that is a question: recommend one and wait.
- Resolve dependent questions in order — the answer to "does this app have accounts?" decides whether the next four questions exist at all.
- A vague answer ("some kind of feed", "the usual settings") gets one follow-up.
- Build once the answers are in. Anything still open at that point is recorded as `UNDECIDED — ask before assuming`, in the document that owns it.

## 2. `PRODUCT.md` is the source of truth

- Read `docs/PRODUCT.md`, `docs/DESIGN.md` and `docs/DOMAIN.md` before any task. They are written by `product-discovery.md`, `design-conception.md` and `domain-model.md`.
- Screen prompts read `DESIGN.md` for the screen's empty / loading / error states. A screen shipped without them is not done.
- Use the domain vocabulary recorded there — `Lesson`, `Invoice`, `Match`, whatever the developer said. Never `Item`, `Data`, `Record`, `Thing`.
- A decision marked `UNDECIDED` gets **asked, then written back** to the file that records it.
- A capability marked "later" or "never" gets no prompt run and no dependency installed.

## 3. Documentation is an input you request

Setup pasted from memory is the most common failure in this library. Config layout moved in Tailwind 3→4, NativeWind 4→5, Reanimated 3→4, Sentry 7→8 — each one added, moved, or deleted a required file.

Before writing setup code for any library, work this cascade in order and **say which step you landed on**:

1. **Read the installed version** from `package.json` and the lockfile. This is a fact — look it up.
2. **Use a documentation tool if this agent has one** (a docs MCP server, a fetch tool) and read the docs for that exact major.
3. **Otherwise ask the developer for it.** "I need the NativeWind 5 install guide — paste it, give me a link I can fetch, or save it to `docs/vendor/nativewind@5.md`." Anything under `docs/vendor/` is read first on later runs, so the ask happens once.
4. **If the developer says to proceed from memory**, name which steps are unverified, write the code, and list every unverified step in the final report so it gets checked against a real build.

Where the installed version's docs contradict a step in a prompt, follow the docs and say so. A prompt is a checklist of concerns, not a snippet to paste.

## 4. Inspect the repo before creating files

- Paths in these prompts are illustrative. Read whether this project uses `app/` or `src/app/`, whether `tailwind.config.js` or `babel.config.js` exist at all, and follow what is there.
- Create a config file when the installed version requires it, and only then.

## 5. Invent nothing

- Every field, table, endpoint, event name, and piece of user-facing copy traces to `PRODUCT.md`, `DOMAIN.md`, an inspected schema, or a real contract. Anything else is a question.
- Draft copy is labelled a draft and approved before it ships.
- Ask before adding a dependency: say what it replaces, and why doing it by hand is worse.

## 6. Secrets stay server-side

- `EXPO_PUBLIC_*` is compiled into the bundle and readable by anyone with the app. Publishable and anon keys belong there; anything the provider calls a secret key belongs to a server you control.
- Keys, service-account files and `.env` stay out of git.

## 7. Report honestly

- State what you skipped, what you assumed, and what you could not verify.
- Walk the prompt's `Done when` checklist and mark each item met, not met, or not verifiable. A box you did not test stays unticked.
- A failed step is reported with its output.
- **The next step is named by its command, never by a file.** Prompt filenames are internal ids the developer never types. A prompt that is a phase's own step uses the phase command (`/mobilekit:design`, not `design-conception.md`); every other prompt goes through `/mobilekit:build <id>` (`/mobilekit:build domain-model`, not `domain-model.md`) — in the host's invocation form, or as "run the mobilekit <id> step" where the host has no commands.
