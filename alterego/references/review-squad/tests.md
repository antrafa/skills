# Lens: Tests

Would these tests catch a real bug in this change, or do they only pass?

**Not yours:** bugs in production code (Correctness), conventions (Conformance),
design (Architecture). Do not run the tests: another step does that.

## How to look

1. Read the rules for tests in the repository (framework, what is forbidden,
   naming, where they live).
2. Read the production change first and list every branch, error path and side
   effect it has.
3. Read the tests and map what each one proves.
4. Compare the two lists.

## What to hunt

| Problem | Confidence when proven |
|---|---|
| Changed production file with branches and no test touching it | 85 |
| Test that passes if the logic is reverted (asserts nothing that the change affects) | 95 |
| Test name promises an outcome the assertions never check | 90 |
| Only "not null" or "success" asserted, never the actual value | 85 |
| Return value asserted, side effect (saved, sent, published) not | 85 |
| Mock of the very logic under test | 90 |
| Verify that something was called, with any arguments | 80 |
| Error path with no test, or "not found" / empty input / boundary with no test | 85 |
| Failure path that does not assert the side effect did *not* happen | 85 |
| Test that depends on execution order, wall clock or network | 85 |
| Test weakened or skipped in this diff to make it pass | 95 |
| Test with a forbidden framework or library, per the repository's rules | 90 |

## Rules

- A test count is not coverage. Name the scenario that is missing.
- Do not ask for tests of getters, trivial wiring or generated code.
- Infrastructure with no test harness in the repository: say so once in
  `not_checked`, do not open one finding per file.
