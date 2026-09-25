---
name: lapida
description: Refines a raw idea (a business, an internal product, a personal project) into a viable, testable proposal through four phases — EXPLORE, CHALLENGE, REFINE, FIT — built on consolidated methods (Jobs to Be Done, The Mom Test, Assumption Mapping, Pre-mortem, Lean Canvas, Riskiest Assumption Test). Use when the user brings an idea to elaborate, validate, stress-test or turn into a business — in any language, including "tive uma ideia", "refina essa ideia", "isso vira um negócio?" — or invokes /lapida or $lapida.
license: MIT
---

# Lapida

Cuts a raw idea down to what survives: the real problem, the exact audience, the
riskiest assumption and the cheapest test that settles it. The end state is not
"your idea is good" — it is a refined version, the evidence behind it and a
conditional recommendation.

## Language

Chat replies and the idea file follow the user's language, not the language of
this skill. Phase names (`EXPLORE`, `CHALLENGE`, `REFINE`, `FIT`) stay as proper
names; every block heading of the idea file is translated.

## Rules for every phase

- **Problem before solution.** No solution, feature or technology is proposed
  until EXPLORE has closed the problem and the audience. An idea that arrives as
  a solution ("an app that…") is rewritten as the problem it assumes.
- **Market facts carry a source.** A competitor, market size, price or demand
  signal enters only with a source you actually looked up (web search), or
  labeled `hypothesis — to verify` with the check that would close it. Recall
  from memory is a hypothesis.
- **Facts are yours to find, decisions are the user's.** Look up what the
  environment or the web can answer; put every choice to the user with your
  recommended answer.
- **Attack the idea, never the person.** When the idea survives an attack, say
  which test it passed.
- **Evidence has a strength.** Every assumption is tagged `strong`, `weak` or
  `none`. Evidence from a single person — the user included — is at most
  `weak`, even when it is past behavior: one case does not make a pattern.

## Steps

### 1. Resume or start

If the argument points to an existing idea file, read it and resume at the first
phase whose required fields are not all filled. Otherwise start at step 2.

Done when: the starting phase is announced.

### 2. Classify

Pick the class from the idea; announce it with the forecast and let the user
override:

| Class | Forecast | What changes |
|---|---|---|
| `business` | ~15–20 questions | full FIT: monetization, competitors, market signals |
| `internal product` (tool, feature, team process) | ~8–10 | FIT becomes adoption by the team; no monetization |
| `personal project` | ~5–7 | FIT becomes "is it worth my time"; CHALLENGE is shorter |

Done when: class and forecast are stated in the reply.

### 3. Write back the understanding

Rewrite the idea as a problem, with no solution inside it, and split what the
user said from what you assumed. Ask them to confirm or correct.

Done when: the user confirmed or corrected the rewrite.

### 4. Run the phases

In order: EXPLORE, CHALLENGE, REFINE, FIT. On entering a phase, read its
reference — [explore.md](references/explore.md),
[challenge.md](references/challenge.md), [refine.md](references/refine.md),
[fit.md](references/fit.md) — which holds its required fields, its methods and
its question repertoire.

Each phase runs in **rounds**:

- Open every round with the position: `CHALLENGE · question 7 of ~14`
  (translated to the user's language). The count is cumulative across phases.
- Ask up to **3 questions** per round, only ones that are independent of each
  other; a question that depends on an unanswered one waits for the next round.
  Number each and give your recommended answer under it.
- Recompute the forecast every round. When it moves, give the reason in one line
  ("up from ~12 to ~16: two distinct audiences emerged").
- **"avança" / "skip"** fills the rest of the current phase with your
  recommended answers, each marked `assumption`, and moves to the phase summary.

A phase is done when every required field is filled or marked
`hypothesis — to verify`. Then, in this order: write it to the idea file;
after that last tool call, **show the phase summary — every block the phase
owns, in full — in the same final message that asks for the ok**; and **wait for
that ok before opening the next phase**. The user approves what they read in
that message; a pointer to the file or to an earlier message is not a summary.
The file's `Phase` field moves forward only after the ok. A correction reopens
only the affected field.

Create the idea file when EXPLORE closes, at `./ideas/<slug>.md` in the current
directory, and state the path. Format: [idea-file.md](references/idea-file.md).

Done when: FIT's summary is approved.

### 5. Deliver

Show the full idea file in the chat order of its blocks, ending with the
**Recommendation**: `go`, `pivot` or `stop`, always conditional on the next test
("go if the landing page converts ≥ 3% in two weeks"). Offer, once, the optional
views from [more-methods.md](references/more-methods.md): the one-page Lean
Canvas and the PR/FAQ.

If the recommendation is `go` and the next step is building software, suggest —
do not invoke — turning it into requirements with whatever spec or design skill
the environment has.

Done when: the recommendation is delivered and the file is up to date.

## Methods outside the core

Business Model Canvas, Value Proposition Canvas, Opportunity Solution Tree, Six
Thinking Hats, Kano, RICE, TAM/SAM/SOM and PR/FAQ live in
[more-methods.md](references/more-methods.md). Reach for one only when the user
asks for it by name or a phase's reference points to it.
