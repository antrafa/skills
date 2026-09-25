# Evals

Three scripts, split by what they can honestly measure.

| Script | Covers | Cost |
|---|---|---|
| `run_script_evals.py` | vault.py's arithmetic and cross-file consistency | seconds, no model |
| `seed_vault.py` | throwaway vaults with ages relative to today | instant |
| `grade_agent_runs.py` | the vault state an agent run left behind | seconds, no model |

Agent runs themselves are spawned by hand — one subagent per arm — because what
they test is judgment, and judgment needs a model.

## Run the deterministic half

```bash
./run_script_evals.py        # 44 assertions, exit code 1 on any failure
./run_script_evals.py -v     # show evidence for passes too
```

This is the one to run after touching `vault.py`. It covers evals 1, 4, 7, 9 and
10 plus the mechanical half of 5. `vault.py --selfcheck` is the faster inner loop;
this is the outer one, driving the real CLI against real vaults.

Verify it can still fail before trusting a green run — reintroduce a bug and
confirm the relevant assertion goes red. A harness that has never failed is
untested.

## Build a vault to poke at by hand

```bash
export MENTAT_VAULT=$(./seed_vault.py --scenario cors)
```

Scenarios: `cors` (a vault that already knows the CORS bug, plus two deliberate
distractors), `mixed-age` (every type, ages spread from 0 to 300 days idle, one
orphan, one dangling link), `empty` (initialized, no entries), `bare` (the path
does not exist — for testing bootstrap).

Ages are generated relative to today rather than checked in. A seed frozen at a
fixed date tests something different every day it sits in the repo, and the decay
assertions — "a note idle 14 days lands near 75" — would drift into failing on
their own.

## Run the agent half

Spawn one subagent per arm, then:

```bash
./grade_agent_runs.py <workspace>/iteration-N
```

It diffs each run's vault against a freshly generated reference and writes
`grading.json` per run. Assertions about the *response* rather than the
filesystem come out as `needs_review` — those are for a human, not for a script
guessing at tone.

### Keeping the baseline honest

The baseline arm is supposed to answer "what does Claude do without this skill?"
It is easy to accidentally measure something else. In the first run of these
evals, all four baseline agents found and read `SKILL.md` anyway — so the
"without skill" numbers were really "with the skill, discovered the hard way",
and the comparison measured nothing.

Two things caused it, both in the harness rather than the skill:

- The output path contained the literal string `without_skill`, which told the
  agent it was in an experiment and invited it to look for the thing it was
  supposed to lack.
- The vault lived inside the skill's own repository, so `grep` for anything in
  the prompt led straight to `SKILL.md`.

So for a baseline run: put the vault somewhere neutral (`/tmp/...`), name nothing
after the skill or the arm, and scope the agent to that directory. The user's
prompt still says `/mentat` — that is the real input and cannot be laundered —
but nothing else should hint that a skill exists.
