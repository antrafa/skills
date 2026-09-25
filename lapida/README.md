# Lapida (`lapida`)

Refines a raw idea — a business, an internal product, a personal project — into
a viable, testable proposal. You bring a sentence; Lapida takes you through four
phases and hands back the real problem, the exact audience, the riskiest
assumption and the cheapest test that settles it.

*Lapidar* is Portuguese for cutting a raw stone into a gem: the work is removing
material until only what holds up is left.

## The problem

An idea usually arrives already dressed as a solution — "an app that connects
X to Y" — and goes straight to a plan, a pitch or code. Nobody asked whether the
problem is real, who exactly feels it, which assumption is the most fragile, or
what the smallest test would be. Months later the answer shows up anyway, at the
most expensive moment.

Lapida is the step before the requirement. It does not tell you your idea is
good. It tells you what is known, what is assumed, where it breaks first and
what to test next — and ends with a recommendation you can act on.

## What it is not

- **Not a requirements or spec writer.** It decides whether an idea is worth
  pursuing and what goes into v1; turning that into requirements is the next
  step, with whatever spec or design skill you use.
- **Not market research.** A conversation cannot measure demand. Competitors,
  prices and market sizes enter only with a source that was actually looked up,
  or labeled `hypothesis — to verify` with the check that would close it.
- **Not a cheerleader, and not a wet blanket.** Critique targets the idea, and
  when the idea survives an attack, Lapida says which one.

## How it works

### 1. Classify

The idea is classified first. The class sets how deep the last phase goes and
how many questions to expect:

| Class | Forecast | What changes |
|---|---|---|
| `business` | ~15–20 questions | full FIT: monetization, competitors, market signals |
| `internal product` (tool, feature, team process) | ~8–10 | FIT becomes adoption by the team; no monetization |
| `personal project` | ~5–7 | FIT becomes "is it worth my time"; CHALLENGE is shorter |

You can override the class.

### 2. Write back the understanding

Before any question, the idea is rewritten as a problem with no solution inside
it, separating what you said from what was assumed. Nothing moves until you
confirm or correct it.

### 3. Four phases

| Phase | Question it answers | Methods |
|---|---|---|
| **EXPLORE** | What hurts, for whom, and what proves it? | Jobs to Be Done, 5 Whys, The Mom Test |
| **CHALLENGE** | Why might this not work? | Assumption Mapping (DVF), Pre-mortem, devil's advocate stance |
| **REFINE** | What is the smallest version worth building? | How Might We, SCAMPER, Lean Canvas |
| **FIT** | Which signals would confirm fit, and what is the next test? | Riskiest Assumption Test, test cards |

EXPLORE and CHALLENGE work the problem; REFINE and FIT work the solution — the
two diamonds of the Double Diamond. No solution is proposed before EXPLORE has
closed the problem and the audience.

### 4. Rounds, progress and gates

- Questions come in **rounds of up to three**, only ones independent of each
  other, each with a recommended answer. Finding facts is the agent's job;
  decisions are yours.
- Every round opens with the position: `CHALLENGE · question 7 of ~14`. The
  forecast is recomputed every round and, when it moves, the reason is given
  ("up from ~12 to ~16: two distinct audiences emerged").
- A phase is done when every required field is filled or marked
  `hypothesis — to verify`. It then shows a summary and **waits for your ok**
  before opening the next phase — four stops in total, where a wrong premise is
  caught before it contaminates the next phase.
- **`avança` / `skip`** fills the rest of the current phase with the
  recommended answers, each marked `assumption`, and jumps to the summary.

### 5. Recommendation

The session ends with `go`, `pivot` or `stop`, always conditional on the first
test — for example, *"go if 30 of the 200 feirantes reached join the waitlist in
two weeks"*. Stopping early is the skill doing its job.

## What comes out

A living file at `./ideas/<slug>.md`, created when EXPLORE closes and updated
at the end of every phase. Its blocks, and the phase that owns each:

| Block | Phase |
|---|---|
| Original idea · Real problem · Target audience · Job to be done · Current evidence · Current workaround | EXPLORE |
| Risks and assumptions (DVF + evidence strength) · Riskiest assumption · Pre-mortem · Doing nothing · Contradictions | CHALLENGE |
| Solution options and hypothesis · Differentiator · Refined version · Out of v1 | REFINE |
| Alternatives and competitors (with source) · Fit signals · Monetization (`business` only) · Next tests · Recommendation | FIT |
| Decision log | every phase |

Every piece of evidence carries a strength — `strong`, `weak` or `none` — and
one person's opinion, the author's included, is `weak`. The next test is written
as a test card:

> We believe `<hypothesis>`. To verify, we will `<test>`. We measure
> `<metric>`. We are right if `<numeric criterion>` by `<date>`.

Resume in a later session by passing the file: `/lapida ideas/<slug>.md`. It
picks up at the first phase with missing fields.

Optional views, offered once at the end and always rendered from the file,
never kept as a second source:

- **Lean Canvas** on one page.
- **PR/FAQ** (Amazon's Working Backwards) — when the idea has to be sold to a
  boss, a partner or an investor.

## Methods and sources

The core methods, one default per phase:

| Method | Author / origin | Where |
|---|---|---|
| Jobs to Be Done | Clayton Christensen; Tony Ulwick (outcome-driven innovation) | EXPLORE |
| 5 Whys | Toyota Production System | EXPLORE |
| The Mom Test | Rob Fitzpatrick | EXPLORE, FIT |
| Assumption Mapping | David Bland, *Testing Business Ideas* | CHALLENGE |
| Desirability · Viability · Feasibility | IDEO | CHALLENGE |
| Pre-mortem | Gary Klein | CHALLENGE |
| How Might We | IDEO, Stanford d.school | REFINE |
| SCAMPER | Bob Eberle, from Alex Osborn's checklist | REFINE |
| Lean Canvas | Ash Maurya, *Running Lean* | REFINE |
| Riskiest Assumption Test | Rik Higham, on Eric Ries's Build-Measure-Learn (*The Lean Startup*) | FIT |
| Test card | Strategyzer, David Bland | FIT |
| Sean Ellis test | Sean Ellis | FIT |

Outside the core, reached only when you name one or a phase needs it: Business
Model Canvas, Value Proposition Canvas, Opportunity Solution Tree, Six Thinking
Hats, Kano, RICE, TAM/SAM/SOM, PR/FAQ and Double Diamond — see
[references/more-methods.md](references/more-methods.md) for when each beats
the default.

## Language

The skill is written in English; replies and the idea file follow the user's
language, block headings included. Phase names stay as proper names.

## Structure

```
lapida/
  SKILL.md                    flow: resume/classify → write back → 4 phases → deliver
  references/
    explore.md                required fields, methods and questions per phase
    challenge.md
    refine.md
    fit.md
    idea-file.md              format of the living file
    more-methods.md           methods outside the core, optional views
  evals/                      executable cases for `claude plugin eval`
  .claude-plugin/plugin.json
```

Each phase's reference is read only when that phase opens, so the main file
carries only the flow and the rules every phase shares.

## Install

Clone the repository and link it into each agent's skills directory:

```bash
git clone git@github.com:antrafa/lapida.git ~/workspace/pessoal/skills/lapida
SRC=~/workspace/pessoal/skills/lapida   # adjust to where you cloned it
for d in ~/.claude/skills ~/.agents/skills ~/.codex/skills ~/.gemini/config/skills; do
  mkdir -p "$d" && ln -sfn "$SRC" "$d/lapida"
done
```

| Directory | Agent |
|---|---|
| `~/.claude/skills` | Claude Code |
| `~/.codex/skills` | Codex |
| `~/.gemini/config/skills` | Antigravity |
| `~/.agents/skills` | shared default (Cursor, OpenCode and others) |

## Usage

```
# Claude Code / Antigravity
/lapida tive uma ideia: um app que conecta produtores rurais a restaurantes
/lapida a tool to open deploy tickets automatically for my team
/lapida ideas/estoque-feirantes.md          # resume
/lapida ideas/estoque-feirantes.md avança   # resume and skip the current phase

# Codex
$lapida a newsletter about legacy Java modernization
```

Non-interactive:

```bash
claude -p "/lapida <your idea>"
codex exec "\$lapida <your idea>"
agy --print "/lapida <your idea>"
```

It also triggers from natural language, in any language: "I had an idea",
"stress-test this idea", "could this become a business?", "tive uma ideia",
"refina essa ideia".

## Evals

Seven executable cases in `evals/`, each run with and without the skill. The
first three check the entry and the sourcing rule; the last four each start
from an idea file stopped at one phase and check that its methods are applied:

| Case | Checks |
|---|---|
| `01-business-first-reply` | a solution-shaped business idea is classified, rewritten as a problem, and no solution is proposed |
| `02-internal-tool` | an internal tool gets the ~8–10 forecast and no monetization talk |
| `03-competitors-sourced` | asked for competitors up front, names none without a source or a hypothesis label |
| `04-resume-skip-challenge` | CHALLENGE: assumptions by DVF, the riskiest one, a pre-mortem and doing nothing, then the gate |
| `05-explore-weak-evidence` | EXPLORE: The Mom Test tags "they said they would use it", a compliment and the author's own pain as weak; the job statement names no product |
| `06-refine-options` | REFINE: three different options, one without software, a v1 cut around the riskiest assumption |
| `07-fit-test-card` | FIT: the next test as a full test card with a numeric criterion and a deadline, and a recommendation conditional on it |

```bash
claude plugin eval . --scaffold --allow-tools Edit Write --output-dir /tmp/lapida-eval
```

`--scaffold` runs the fixture that creates the idea file for the resume case;
`--output-dir` keeps results outside the skill, which is itself the plugin's
skills path.

## Credits

The conversation mechanics draw on two skills: Superpowers' `brainstorming`
(write back the understanding, one approval per stage) by Jesse Vincent, and
`grilling` (decision rounds with a recommended answer per question) by Matt
Pocock.

## License

[MIT](LICENSE). Built by [Antonio Rafael Ortega](https://github.com/antrafa).
