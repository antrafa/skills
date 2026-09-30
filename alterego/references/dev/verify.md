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

**Red flags:** "should", "probably", "seems to"; celebrating before running;
about to commit, push or open a PR without running; accepting a subagent's
report without looking at the diff.

## Done when

Build, lint, tests and the applicable fitness functions ran in this reply, every
criterion is met in the table above, and the handoff shows each command with its
exit code — or states which one could
not run and why.
