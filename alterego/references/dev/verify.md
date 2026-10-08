# Step 6 — Verification

**Iron law: no claim that something is done, fixed or passing without evidence
produced in this same reply.** A run from earlier in the session is history, not
evidence.

## The gate, per claim

1. **Identify** the command that proves the claim.
2. **Run** it whole and fresh — the full suite, the real build.
3. **Read** the whole output: exit code, number of failures, warnings.
4. **Claim only what the output shows.** If it shows something else, report the
   real state with the output.

| Claim | Needs | Not enough |
|---|---|---|
| Tests pass | Test command output with 0 failures | A previous run, "it should pass" |
| Lint is clean | Linter output with 0 errors | A partial check |
| Build succeeds | Build command with exit 0 | Lint passing, logs that look fine |
| Bug fixed | The original symptom reproduced and now passing | Code changed, fix assumed |
| Regression test works | Pass → revert the fix → **fails** → restore → pass | A single passing run |
| A subagent finished | The diff in version control, checked | The subagent saying it succeeded |
| Plan delivered | The plan reread, item by item | Green tests |

## Nothing to run is the finding

A repository with no build, lint or test command has nothing that proves the
work. That goes first under **Blocks** in the handoff: the delivery had no
proof, and saying so is the result. Propose the cheapest check the repository
supports — a compile, the script run once with a known input — and run it if
the user agrees.

## Current base, before the gate counts

Green on a stale base proves the branch, not the merge. Before the run that
counts:

1. `git fetch` the base when it is a remote branch. Offline, the last fetched
   one stands, and the handoff says so.
2. `git merge-base --is-ancestor <base> HEAD` succeeds: the branch is current,
   go on.
3. It fails: the base moved. Say by how many commits
   (`git rev-list --count HEAD..<base>`) and propose the update the repository
   uses — rebase for a branch never pushed, merge for a shared one — run with
   the user's yes. The gate then runs again on the updated branch; the run
   before it is history.
4. A conflict stops the step: it goes under **Blocks**, with the files.

## Criteria check, before any commit

Green tests prove the code does what the tests say, not what was asked. Before
committing, reread every acceptance criterion — from the spec, the plan or the
bounded design in the chat — and point to the code and the test that meet it:

```markdown
| Criterion | Status | Evidence |
|---|---|---|
| AC-01 | met | `src/auth/Token.java:42`, `TokenTest.expiredReturns401` |
| AC-02 | not met | expiry handled, the 401 body is not |
```

One criterion not met sends the work **back to step 4**, not forward. No
criteria at all is itself the finding: say that the delivery had no contract to
check against.

The architectural characteristic is verified by a fitness function, never by the
suite — see *Step 6 in detail* in [playbook-dev.md](../playbook-dev.md#step-6-in-detail-the-fitness-function).

## Excuses and the answer to each

| Excuse | Answer |
|---|---|
| "I'm confident it works" | Confidence is not output. Run it. |
| "The linter passed" | The linter does not compile nor run the tests. |
| "The agent said it succeeded" | Check the diff yourself. |
| "A partial check is enough" | A partial check proves the part it checked. |
| "This repository has no tests" | Then nothing was verified, and that is the finding. |
| "The base only moved a little" | A little is enough for a conflict nobody ran. |

**Red flags:** "should", "probably", "seems to"; celebrating before running;
about to commit, push or open a PR without running; accepting a subagent's
report without looking at the diff.

## The handoff

Two lists on top, then each command with its exit code:

- **Blocks** — the work stays out of step 7 while one is here: a gate command
  not at exit 0, nothing to run, a criterion not met, a Critical or Warning
  still open from step 5, a base that moved and was not updated, a conflict
  with it.
- **Needs your look** — not known to be wrong, worth a human eye before the PR:
  a criterion with no automated test (and why), a path where a plausible change
  still breaks production (CI, deploy, migration, dependency manifest, auth,
  secrets), a diff over ~400 changed lines, a security scanner that did not run,
  a step 5 finding answered with a counterpoint instead of a fix.

An empty list is written as *none*. A blocker reaches step 7 only with the
user's written reason, and the PR description carries it under *Out of scope
and side effects*.

## Done when

Build, lint, tests and the applicable fitness functions ran in this reply on a
branch current with its base, every criterion is met in the table above, and
the handoff shows both lists and each command with its exit code — with
**Blocks** empty, or the user's reason written for each item left in it.
