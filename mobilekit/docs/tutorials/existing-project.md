# Adopting mobilekit in a project you already started

You have an Expo project with a few screens in it, no `docs/`, and decisions you made three weekends ago and half remember. You do not want to restart. This is the path for that, and it is the most common one.

**In progress is not in production.** If your app is in the stores, stop here: it has users whose sessions, saved data and existing links constrain every decision, so inventory replaces the interview — [legacy-app.md](legacy-app.md) is your path, not this one. This tutorial assumes nobody but you has the app.

The example is **a workout journal, half-built**: a home screen, a list of sessions, a `data/items.ts` full of hardcoded fixtures, no auth, and a `// TODO: backend` where the API should be. It is the app every developer has started in a folder somewhere, which is exactly why it works here.

> **Not your starting point?** [Thirty minutes and no accounts](quickstart.md) · [a new app from scratch](new-app.md) · [users see each other's content](social-app.md) · [the data is behind someone else's API](external-api.md) · [an app already in the stores](legacy-app.md). Full index: [TUTORIALS.md](../TUTORIALS.md).

---

## Before you start

| | Why |
|---|---|
| Everything committed, and a branch to work on | Discovery writes one file, but `domain-model` renames types across screens. You want a diff you can read and a commit you can walk back to. |
| A project that actually runs right now | The agent reads your repo to decide what is done. A repo that does not build makes every "already present" mark a guess. |
| A physical device | Same as every other path: several `Done when` items cannot be ticked without one. |
| 20–30 minutes for discovery and design | Shorter than the from-scratch path, because the agent can read a third of the answers. Not zero. |
| Your own memory, or none of it | You will be asked things you decided implicitly — whether content is yours or the user's, whether the app needs accounts. "I never decided" is a valid answer; it becomes `UNDECIDED — ask before assuming` and blocks the step that needs it, which is the point. |

**What this path does not do.** There is no command that reverse-engineers a product definition from an in-progress repo. That behaviour exists only for apps that already ship (`legacy-modernization.md`), and it leans on store listings and live usage you do not have. So discovery runs. It is just shorter than you expect.

---

## Phase 0 — `init` reads before it writes

```
/mobilekit:init
```

Nothing is copied into your repo. The prompt library stays inside the skill and is read from there, so the only file that lands in your project is `AGENTS.md`.

What it inspects first:

- **`package.json`** — is there an `expo` dependency, and what is actually installed. Aspirational libraries do not make the list.
- **The folder layout, as found.** This matters more on this path than any other. Every path in the prompts is illustrative; `RULES.md` §4 makes the agent read whether you use `app/` or `src/app/`, whether `tailwind.config.js` exists at all, and follow what is there. Your layout does not get normalized to match an example.
- **An existing `AGENTS.md` or `CLAUDE.md`.** It extends yours. It does not replace it.
- **`docs/`** — if `PRODUCT.md`, `DESIGN.md` or `BUILD-PLAN.md` are already there, this project has been through part of the flow, and `init` reports where it stands instead of starting over.

It asks one thing worth thinking about: **is there anything the assistant must not do in this repo** — touch migrations, edit generated files, run builds. Whatever you say goes into `AGENTS.md` and is read before every later task. This is the cheapest guardrail in the workflow.

Because there is no `PRODUCT.md` yet, the product sections come out as `TBD — run discovery`. The stack, the layout and the conventions read out of your existing code are filled in properly. After discovery, refill the rest:

```
/mobilekit:build agents-md
```

**If you need to override a rule for this project** — your repo already commits `.env.example`, your team forbids a dependency — write `docs/mobilekit-overrides.md`. It is read after `prompts/RULES.md` and wins on conflict.

---

## Phase 1 — Discovery still runs

```
/mobilekit:discovery
```

The instinct is to skip this because the app already exists. It exists to you. To the agent it is a folder of files that can be read but not explained, and **code answers what, never why**. `data/items.ts` tells it there are records with a date and a weight. It does not tell it whether a user logs their own workouts or follows a programme you wrote.

The shortening comes from `RULES.md` §1: **a fact is looked up, never asked; a decision is asked, never taken.** On this path a lot of Block D and Block G is fact. So the interview opens by reporting rather than asking:

> I read your repo before starting. `package.json`: Expo with Expo Router and NativeWind. Layout: `app/(tabs)/` with `index.tsx` and `sessions.tsx`, components in `components/`, no `src/`. Content comes from `data/items.ts` — 6 hardcoded records, no network call, and a `// TODO: backend`. I will not ask you any of that.

Then the block that pays for the session, with the code used as a proposal rather than a conclusion:

> **What is the one thing this app is mostly about?**
> `data/items.ts` calls each record an `Item` with `date`, `exercise`, `reps`, `weight`, and `sessions.tsx` groups them by day. My reading: the central object is a workout **Session**, and today's `Item` is a **Set** inside one. I am proposing this, not taking it from the code — confirm or correct.
>
> — Right. Session is what you open the app for. A Set is one line inside it.
>
> **What is the real vocabulary? The 3–7 nouns you would use talking to a colleague, and how they relate.**
>
> — A Routine has many Sessions. A Session has many Sets. A Set is of one Exercise, with reps and weight.
>
> **Is this content authored by you or created by users?**
> Recommended: both — the Exercise list looks curated, the Sessions look logged. Confirm.
>
> — Both. I ship the exercises; sessions are the user's.

Note what happened. `Item` never became the domain, and it never became a question either. The agent found it, said what it thought it meant, and waited. That is the difference between reading the code and trusting it.

Block D lands on the scenario your `TODO` already implies:

> **Does the data already live somewhere?** Given `data/items.ts` and no client, this is **D — no backend yet, local content first, backend later**. Confirm.

That one answer removes several steps from the plan later.

**What you get:** `docs/PRODUCT.md`, under 100 lines, with an `## Open questions` section holding everything you deflected, and a `Constraints` section ending in *existing codebase conventions: what you found by reading it*.

> **The failure this prevents.** Skip discovery here and the agent has exactly one source of vocabulary: your fixture file. `Item` is not a placeholder it will notice — it is the only name the repo offers, so it propagates into types, services, hooks and every screen you add from now on. On a from-scratch project a skipped interview invents a domain; here it *promotes* one.

If you already wrote a `PRODUCT.md` by hand, discovery reads it and asks whether this is a revision of specific sections or a fresh start. It is not silently overwritten.

---

## Phase 2 — Design, for screens that already exist

```
/mobilekit:design
```

Your screens exist; their **states** almost certainly do not. That is what this phase is for on this path.

Two things happen that are specific to adopting mid-project:

**Existing screens get tested against the journey.** Every screen in the inventory must trace to a step in the core journey or to a capability marked "now". A screen that traces to neither is left out of `DESIGN.md` with the reason stated. The workout journal lost a stats screen this way — half-built, reachable from nothing in the journey. **The code is not deleted**; it simply stops being something the plan builds toward, and the mismatch is now written down instead of sitting in your repo as an open tab.

**The four states get decided for screens you already shipped to yourself.** Your session list renders your six fixtures beautifully and has no answer for zero, for slow, or for failed:

| State | Session list |
|---|---|
| Empty | "No sessions logged yet." One action: *Log your first session*. |
| Loading | Skeleton rows shaped like a session row |
| Error | "Could not load sessions." Retry. Already-loaded rows stay visible. |
| Populated | Most recent first, this week's grouped at top |

You built the fourth one already. The other three are the retrofit, and they are cheap here because there are two screens rather than twelve.

**What you get:** `docs/DESIGN.md`.

---

## Phase 3 — The plan marks what is already done

```
/mobilekit:plan
```

This is the payoff of the whole path. `plan` reads your repo — `package.json` and the actual files — and **anything already done is marked done, not queued**:

```markdown
## Foundation
- [x] expo-setup · already present
- [x] nativewind · already present
- [ ] design-system
- [ ] domain-model
- [ ] ui-components
- [ ] app-shell · the screens exist; the root layout has no owner yet

## Screens
- [x] tab-navigation · already present · Sessions · Routines · Profile
- [ ] home-screen · states undefined until DESIGN.md landed
- [ ] list-screen · Sessions
- [ ] detail-screen · Session
- [ ] form-screens · log a Set

## Features
- [ ] dark-mode
- [ ] offline · cached reads only

## Release
- [ ] testing
- [ ] accessibility
- [ ] performance
- [ ] security-review
- [ ] store-compliance
- [ ] eas-build
- [ ] beta-and-review

## Skipped
| Step | Why |
|---|---|
| supabase, react-query | PRODUCT.md: Data scenario D — local content first, no remote source yet |
| auth-clerk, auth-backend, account-recovery | PRODUCT.md: accounts = no |
| monetization, in-app-purchases, payments, ads | PRODUCT.md: payments = never |
| media-upload, native-permissions | PRODUCT.md: media = never, no permission requested |
| content-moderation | Sessions are private to one device — revisit when the backend lands |
```

Three boxes arrive checked. That is the entire economics of adopting mid-project: you are not paying for the work you already did, only for the decisions you never recorded.

Two cautions. **`already present` means the repo shows it present, not that it is good** — `home-screen` above stayed unchecked because the file exists but the screen has no defined states. And the last `Skipped` row is conditional, with the condition written down: the moment the backend arrives, that skip is wrong, and the plan says so rather than leaving you to remember.

`BUILD-PLAN.md` is a markdown file you own. If a box was ticked that you know is not done, untick it and say why in the line. Nothing is hidden from you.

---

## The retrofit that actually hurts

Your screens are built against `Item`. `domain-model` will rename it.

```
/mobilekit:next          # → domain-model
```

Because `PRODUCT.md` records scenario D, the prompt takes the local-content path: types in `types/` named from your vocabulary — `Session`, `Set`, `Exercise` — authored content in `data/` typed against them, and access through the same function shapes a real backend would use (`getSessions()`, `getSessionById()`), so the day the `TODO` gets filled, that is an implementation change and not a screen rewrite. The swap point is recorded in `docs/DOMAIN.md`: which files change when the backend arrives, and which do not.

The fixture rewrite is stricter than what you have. Fixtures must cover empty, one, many, the longest realistic text, and every status value — because those are what let you actually see the states `DESIGN.md` just defined. Your six happy-path records do not.

Be clear-eyed about the cost. **This is real rework**, spread across every screen that touched `Item`, and it gets worse with every screen you add before running it. Two screens is an afternoon. Twelve is the most expensive rework in the build, which is why the plan puts `domain-model` ahead of every screen step.

Two things make it survivable. The prompt **shows you the model and the mapping before writing anything** — one table per entity, plus the relationships — so you approve names once rather than discovering them in a diff. And it will not invent a field: anything not traceable to `PRODUCT.md` or to your fixture is a question.

---

## `status` and drift

This is the most useful command on this path, because on this path the files and the repo start out disagreeing.

```
/mobilekit:status
```

```
Phase:      build
PRODUCT.md  ok · 1 UNDECIDED
DESIGN.md   ok
BUILD-PLAN  6/19 · next: list-screen
Drift:      plan says nativewind done, nativewind not in package.json
Next:       /mobilekit:next
```

That `Drift` line catches a ticked box with no dependency behind it — a lie in a file. On a project you started yourself this happens for a mundane reason: you installed something, ripped it out, and the plan still believes you.

It reports **which side is wrong and leaves the fix to you**. It does not silently reconcile, because it cannot know whether you meant to remove the dependency or meant to keep the step. `status` is read-only and changes nothing.

---

## `build`, out of order, and the honest cost

You will want to add one thing without walking the whole flow. That is what `build` is for.

```
/mobilekit:build dark-mode
```

It runs one prompt regardless of the plan, and **names the prerequisites it lacks rather than working around them**: no `PRODUCT.md` and it says the domain has to be guessed, recommends discovery, and runs anyway if you confirm; anything holding a secret and it tells you `secure-backend` has not run; camera or notifications and it tells you `native-permissions` has not. If the step is in `BUILD-PLAN.md`, the box gets ticked.

Ambiguity is a question, not a guess: `build auth` maps to three prompts, so it lists them and asks. A topic with no match lists the nearest three rather than improvising a prompt that does not exist.

Now the trade, stated plainly. Run a screen prompt before `DESIGN.md` exists:

```
/mobilekit:build detail-screen
```

and it asks you for the empty, loading and error states inline, and records the answers with that screen. Which works — once. There is no `DESIGN.md` for the next screen prompt to read, so the next one asks again, and the answers you gave in two separate conversations are consistent only by luck. Four questions per screen, forever, versus one design pass. That is the actual cost of skipping the flow, and it is small on two screens and absurd on twelve.

---

## The ways a step stops on this path

| It says | Why | You |
|---|---|---|
| "`docs/PRODUCT.md` already exists — is this a revision of specific sections, or a fresh start?" | A document you filled in by hand is never silently overwritten. | Name the sections, or say fresh start. |
| "Anything I should be forbidden from doing in this repo?" | It goes into `AGENTS.md` and is read before every task. | Name the migrations, generated files or build commands you want left alone. |
| "`data/items.ts` calls this an `Item`. My reading is `Session` — confirm or correct." | Fact looked up, decision asked. It will not adopt a name from your code. | Correct it now. This name reaches every file. |
| "Here is the entity table and the field mapping from your fixture. Approve before I write `types/`." | Renaming twice costs more than reading once. | Read it properly. Highest-leverage five minutes of the adoption. |
| "I need the NativeWind 5 install guide — paste it, give me a link, or save it to `docs/vendor/nativewind@5.md`" | It read your `package.json` and will not write setup from memory; config layout moved between majors. | Paste the page. Anything under `docs/vendor/` is read first next time, so the ask happens once. |
| "`PRODUCT.md` marks offline behaviour `UNDECIDED`." | The step that needs it cannot proceed on a guess. | Answer. It writes the answer back into `PRODUCT.md`. |
| "This screen has no states in `DESIGN.md`. Empty, loading, error — what does the user see?" | A screen shipped without them is not done. | Answer, or run `/mobilekit:design screens` once and stop being asked. |
| `Drift: plan says X done, X not in package.json` | The plan and the repo disagree. | Fix one side. It will not pick for you. |

---

## The four mistakes that cost the most

**Skipping discovery because the app already exists.** It exists to you. The agent gets one vocabulary from your repo — `Item` — and no reason to doubt it, so twenty minutes of interview turns into a week of unpicking a generic name out of forty files.

**Adding screens before `domain-model`.** The plan orders it correctly, and this is the one place where the existing-project path is more dangerous than the from-scratch path: you already have screens built on the old shape, so every new one you add doubles the rename. Run `domain-model` first, take the afternoon of rework, then build.

**Trusting `already present`.** A ticked box means the repo shows the step present, not that it works. Your half-built home screen counts as a file with the right name. Read the plan once after it is generated and untick what you know is unfinished — a box ticked without running it converts a known unknown into an unknown unknown.

**Living in `build` and never running `design` or `plan`.** Each out-of-order step is cheap and none of them record anything, so the fifth screen answers the same four state questions the first one did, inconsistently. The flow is not ceremony; it is the thing that stops you re-deciding.

---

## Where to look next

- [`COMMANDS.md`](../COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../prompts/README.md`](../../prompts/README.md) — all 59 prompts with a description each, and the reference build order
- [`../prompts/RULES.md`](../../prompts/RULES.md) — the rules every prompt inherits. §1 and §4 are the two that shape this path.

**Once the plan is cut, you are on the normal path.** [new-app.md](new-app.md) covers the build loop, the release gate and post-release observability in full — read it from *Phase 4* onward and ignore the phases you have already done.

**If the backend in that `TODO` turns out to be someone else's**, [external-api.md](external-api.md) covers a source you cannot change, and the DTO-versus-domain split that keeps its awkward shapes out of your screens. **If sessions become something other users can see**, [social-app.md](social-app.md) covers the authorization and moderation work that arrives with that decision — including the conditional skip your plan wrote down.
