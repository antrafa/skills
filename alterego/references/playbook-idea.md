# Playbook: Refining a Raw Idea (`/alterego idea`)

An idea arrives dressed as a solution — "an app that…", "a tool to…" — and goes
straight to a plan or to code. This playbook exists so that it first passes
through the questions that decide whether it is worth building: what the real
problem is, who exactly feels it, which assumption breaks first and what the
cheapest test is.

---

## Invocation modes

```
/alterego idea <idea in a sentence>      (starts refining the idea)
/alterego idea ideas/<slug>.md           (resumes an idea file at the first incomplete phase)
/alterego idea                           (assumes the idea under discussion)
```

In Codex:
```
$alterego idea <idea>
```

**No target does not turn into a generic question.** Assume the idea being
discussed in the conversation, or the most recent `ideas/*.md` in the current
directory, and **say which one you assumed**. Only ask when there is no context
at all.

---

## 1. Resolve the `lapida` skill before starting

The method is the partner skill `lapida`: four phases (EXPLORE, CHALLENGE,
REFINE, FIT), rounds with a visible forecast, a gate after each phase and a
conditional `go` / `pivot` / `stop` at the end. Alterego routes and adds its
lens; it does not reimplement the method. Detect it and follow the rule in
[sources.md](sources.md#missing-catalog-skill-degrade-deliver-offer).

**Installed:** invoke it with the resolved target (the `Skill` tool when it
exists). The phases, the idea file and the output format are the skill's; do not
duplicate them here or rewrite the result. Alterego adds two things:

- **CHALLENGE runs through the [devils-advocate](personas/devils-advocate.md)
  lens.** Read the persona when that phase opens and apply it on top of the
  skill's own critique steps — `lapida` accepts a critique lens supplied by the
  invoking skill. The lens is for that phase only; the session's active persona,
  if any, comes back when CHALLENGE closes.
- **The profile sets the language and the examples.** Reply in the user's
  language, and when a question needs an example, prefer one from their own
  context (their domain, their team) over a generic one.

**Not installed:** open with one line saying so, run the degraded path from
section 2 **in the same reply**, and close **that first reply** with the
installation offer — not the end of the session: the refinement spans many
turns, and an offer deferred to the last one never gets made. The opening line
carries no command; the offer does:

> `lapida` is not installed here, so I refined the idea in the chat, without the
> idea file. To equip the environment: `git clone git@github.com:antrafa/lapida.git`
> plus the symlink — I'll show the exact command before running it.

Once per session. Declined? Do not repeat the offer.

---

## 2. Degraded path (without the skill)

Same four phases and the same discipline, straight in the chat, with no idea file
and no per-phase method references:

1. **Classify** the idea as `business`, `internal product` or `personal project`
   and state the forecast of questions (~15–20 / ~8–10 / ~5–7).
2. **Write it back as a problem**, with no solution inside it, separating what
   the user said from what you assumed. Wait for confirmation.
3. **Run the phases in rounds** of up to three independent questions, each with a
   recommended answer, under a header like `EXPLORE · question 3 of ~16`:
   - **EXPLORE** — real problem, specific audience, job to be done, current
     evidence and today's workaround.
   - **CHALLENGE** — assumptions by desirability, viability and feasibility, the
     riskiest one, a pre-mortem and "doing nothing", through the
     [devils-advocate](personas/devils-advocate.md) lens.
   - **REFINE** — three different solution options, the smallest version worth
     building and what stays out of v1.
   - **FIT** — alternatives and competitors, fit signals with current evidence,
     and the next test with a numeric success criterion.
4. **Stop after each phase** with its summary and wait for the ok.
5. **Close** with the recommendation — `go`, `pivot` or `stop` — conditional on
   the first test.

Throughout: no solution before EXPLORE closes; a competitor, price or market
number only with a source or labeled `hypothesis — to verify`; every piece of
evidence tagged `strong`, `weak` or `none`.

---

## 3. After the recommendation

The idea decides *whether* and *what*; building it is another command. Suggest,
do not start:

- `go` and it is software → `/alterego persona requirements-analyst` to turn the
  refined version into requirements, then `/alterego dev`.
- `go` with a structural choice expensive to reverse → `/alterego adr`.
- `go` and it is a local prototype → `/alterego local-app <refined version>`.

---

## Closing checklist

- [ ] Was the absence of `lapida` stated in one line, the refinement delivered in the same reply and the installation offered only at the end?
- [ ] Did the reply rewrite the idea as a problem before any solution appeared?
- [ ] Does every round show the phase, the current question and the forecast?
- [ ] Did CHALLENGE go through the devils-advocate lens?
- [ ] Is every competitor or market number sourced or labeled as a hypothesis?
- [ ] Did each phase wait for the ok before the next one opened?
