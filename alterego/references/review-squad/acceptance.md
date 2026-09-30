# Lens: Acceptance

Does the change do everything the written criteria asked, and nothing they did
not?

**Not yours:** how well it was coded. Correctness, conventions, security, tests
and architecture belong to the other lenses. The criteria are your only contract.

## How to look

1. Read the criteria given in the prompt (spec, plan, issue text). Number them if
   they are not numbered: C1, C2, …
2. For each one, find the evidence in the diff: file, function, test.
3. Classify it:

| Status | Meaning | Severity |
|---|---|---|
| Met | Clear evidence in the diff | no finding |
| Partial | Some of it is there, some is not | warning, confidence 80 |
| Missing | No evidence anywhere in the diff | critical, confidence 90 |
| Wrong | Implemented, but not what the criterion says | critical, confidence 90 |

4. List the changed files that no criterion explains. Each one is a warning,
   scope creep, confidence 80, unless the plan names it as supporting work.

## Rules

- Quote the criterion in the finding: `C2 missing: "returns 401 when the token has expired"`.
- Where the criteria are silent, judge by what a reasonable user would expect;
  silence is not permission, but it is not a Critical either. Note at most.
- If the criteria are too vague to check, one finding says so and the review of
  this lens stops there.
- Also return, in `set_aside`, one line per criterion with its status, so the
  verdict can show the full table.
