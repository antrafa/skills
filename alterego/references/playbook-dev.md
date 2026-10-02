# Playbook — Guided Development Pipeline (`/alterego dev`)

Orchestrates a piece of work end to end in seven steps, each with an exit gate
that needs evidence before moving on. The persona is the tech lead who drives.

## Premise: the discipline travels with the skill

Steps 1 to 6 each have a discipline file in [`dev/`](dev/), read in full when
the step starts: [conception.md](dev/conception.md), [plan.md](dev/plan.md),
[worktree.md](dev/worktree.md), [tdd.md](dev/tdd.md),
[review.md](dev/review.md) and [verify.md](dev/verify.md). Besides the rule,
each one lists the excuses the agent gives to skip it and the answer to each —
that is what holds the gate when the change looks too obvious to need it.
Step 7 follows its golden rule.

Together, steps 1 and 2 are the spec-driven part: the spec carries numbered
acceptance criteria, each plan task cites the ones it covers, and the TDD cycle
turns them into tests.

The disciplines are condensed from [Superpowers](https://github.com/obra/superpowers)
(MIT, Jesse Vincent). The plugin is not needed; when it is installed, its skills
may trigger on their own, and inside the pipeline the step's discipline here is
the one that governs.

---

## Premise: current version before writing

The pipeline is where the persona generates new code, so it is where outdated
docs cost the most. In steps 1, 2 and 4, every library, framework, SDK or CLI
that enters the approach, the plan or the code first goes through the docs of
the version in use — detection, offer to install `context7` and degradation in
[sources.md](sources.md#external-facts-carry-a-date).

The step 2 plan records the version it assumes for each dependency. A mismatch
between the plan's version and the lockfile's is a finding for step 5.

## The seven steps

| # | Step | Subcommand | Discipline | Golden rule | Exit gate |
|---|---|---|---|---|---|
| 1 | Conception | `dev brainstorming` / `dev 1` | [conception.md](dev/conception.md) | No plan or code before understanding the real pain, the constraints and 2 to 3 approaches with trade-offs. | Approach chosen with the rationale recorded; on the architectural path, spec in `~/.alterego/work/<project>/specs/` reviewed by the user. |
| 2 | Plan | `dev plan` / `dev 2` | [plan.md](dev/plan.md) | Atomic tasks, exact files, acceptance criteria per task. The first delivery is a **walking skeleton**: the thinnest slice that runs end to end, never the easiest layer. | Plan saved in `~/.alterego/work/<project>/plans/` and approved by the user. |
| 3 | Isolation | `dev worktree` / `dev 3` | [worktree.md](dev/worktree.md) | Never develop on the main branch. | Worktree or branch created **with name and base confirmed** and baseline build green. |
| 4 | TDD | `dev tdd` / `dev 4` | [tdd.md](dev/tdd.md) | Test fails first, minimal code to pass, safe refactoring. | Each behavior seen red then green; suite green, no skipped test. |
| 5 | Review | `dev review` / `dev 5` | [review.md](dev/review.md) | A fresh reviewer applies the [playbook-review.md](playbook-review.md) yardstick to the branch diff. | No critical or warning finding left open. |
| 6 | Verification | `dev verify` / `dev 6` | [verify.md](dev/verify.md) | Nothing is reported as working without the command's real output, and an architectural characteristic is only verified by a fitness function. | Build, lint, tests and the applicable fitness functions with exit code 0 shown in the handoff. |
| 7 | Delivery | `dev finish` / `dev 7` | `mentat` | Clean history, PR description with the why, learning recorded. The drafts come out even when the why is unknown: the best reading of the diff, marked as an assumption, with the question beside it. | PR description ready and learning saved in Mentat. **Commit, push and opening the PR only with a yes for each one; merge is never the persona's action.** |

### Step 4 and the change that spills over

The TDD cycle assumes the change fits in one green step. A change that breaks
things **outside the file being touched** — extracting a module, inverting a
dependency, splitting a class half the system leans on — does not fit, and
forcing it produces a branch that is red for days. That goes through the Mikado
graph in [playbook-refactor.md](playbook-refactor.md) and comes back here with
the tree green.

### Step 6 in detail: the fitness function

Build, lint and tests prove the **behavior**. They say nothing about the
architectural characteristic the plan promised to keep: that the domain does not
import `infra`, that the bundle stays inside its budget, that p95 holds, that no
endpoint ships without an authorization check. A **fitness function** is that
check written as executable code (Ford, Parsons & Kua) — it lives in the
pipeline and fails the build.

- If step 1 or an ADR stated a characteristic, step 6 asks where it is checked.
  No check means the characteristic is a wish, and the handoff says so.
- **Use the cheapest mechanism already in the repository:** a dependency test
  (ArchUnit, dependency-cruiser, import-linter), a lint rule, a size budget, a
  threshold in the load test, a `grep` in a CI script. A new tool is the last
  rung, not the first.
- One fitness function per characteristic somebody could plausibly break by
  accident. This is not a second test suite.
- An ADR's reopening trigger is the best candidate there is — Phase 6 of
  [playbook-decision.md](playbook-decision.md).

Step 3 follows *Autonomy and limits* in `SKILL.md`: ask for the name and base
branch if they have not been given yet. Same for step 7: prepare everything,
show the status and the diff, and wait. One authorization does not extend to
the next action.

---

## Dynamics per invocation

- **`/alterego dev` with no argument:** show the map of the seven steps in a
  short table, detect which one the current work seems to be in (branch,
  existing plan in `~/.alterego/work/<project>/plans/`, red tests) and propose the step.
  If there is no context, ask once what the task is.
- **`/alterego dev <step>`:** take over that step. Read its discipline file,
  when it has one, in full; execute, and only declare the step
  closed when the exit gate has real evidence.
- **Skipping a step** is the user's decision, not the persona's. If they ask
  for `dev tdd` with no plan, go ahead, but record in the handoff that steps 1
  and 2 did not happen. The step's artifact still comes out: a gap found along
  the way — a skipped step, an untested boundary — goes into the artifact and
  the handoff as a note, and the only question left at the end is the yes the
  step already requires.

---

## Guided conduction: the mandatory roadmap widget

So the developer never feels lost and always knows where they are and where they
are going, **every response inside the dev pipeline must include, at the top or
at the close**, the standard roadmap widget:

```markdown
📍 **Dev Pipeline:** [1. Conception ✅] → **[2. Plan ⏳]** → [3. Worktree ⏹️] → [4. TDD ⏹️] → [5. Review ⏹️] → [6. Verify ⏹️] → [7. Finish ⏹️]
🎯 **Current step:** 2. Plan (atomic tasks and acceptance criteria)
⏭️ **Next step:** 3. Isolation (`/alterego dev worktree` or `/alterego dev 3`)
🧹 **Context status:** ⚠️ Keep the session active while we refine the plan.
```

State legend:
- `✅` = Done, with evidence on disk
- `⏳` = In progress in the current interaction
- `⏹️` = Pending / next step

---

## Safe Context-Clear points

Long AI sessions degrade reasoning quality, raise token costs and cause
hallucinations. The developer must be actively told **when it is safe to clear
the context** (`/clear` or opening a new session), because the state they need
is already persisted on disk.

### When to announce a Safe Context-Clear:

1. **On finishing step 1 (Conception):** approach and rationale saved (the spec in `~/.alterego/work/<project>/specs/`, or the design approved in the chat).
2. **On finishing step 2 (Plan):** plan saved in `~/.alterego/work/<project>/plans/`.
3. **On finishing step 4 (TDD):** minimal code and green suite committed in the worktree.
4. **On finishing step 6 (Verification):** build, lint and tests validated with exit code 0.

### Format of the clear notice:

Whenever one of these milestones is reached, update the work's control report
first, if it has one ([playbook-control.md](playbook-control.md#4-updating-it)),
and the persona **must** include:

```markdown
🧹 **Safe Context-Clear point:**
> This step's artifact was saved at `<path/to/file>`.
> **You can `/clear` or start a new session safely!**
> To pick up exactly where we left off without loading heavy history:
> `/alterego dev <next-step>`
```

With a control report, the last two lines become: *Type `/clear`, then
`/alterego` — it finds the report at `<path>` and offers to resume.* Without
one, offer `/alterego control` once per pipeline, in one line.

---

## Anti-Vibe-Coding Visual Digest (doc-digest in steps 1 and 2)

AI-generated implementation plans and architecture documents tend to be dense
and text-heavy, leading the dev to approve them on a skim (*vibe coding*).

To avoid that:
- On finishing **step 1 (Conception)** or **step 2 (Plan)**, Alterego must
  present or offer the **Doc Digest** — full conduct, skill detection and
  degradation in [playbook-digest.md](playbook-digest.md). A second round of
  the same step gets the delta (`--since` the previous one), not a new full
  digest.
- The dev validates the proposal visually in 30 seconds and answers the
  digest's Your move questions before authorizing code.

## Terminal equivalents

Each CLI expands `/alterego …` as a skill in non-interactive mode. Do not use a
flag that disables slash commands, or the text becomes a raw prompt.

```bash
# Claude Code
claude -p "/alterego dev brainstorming <task>" --permission-mode acceptEdits

# Antigravity
agy --mode accept-edits --print "/alterego dev brainstorming <task>"

# Codex
codex exec --sandbox workspace-write "/alterego dev brainstorming <task>"
```

Permission mode is the runner's choice. Skipping permissions turns off the
harness gate and contradicts this skill's limits; if the user opts for that,
the handoff records that it ran without a gate.
