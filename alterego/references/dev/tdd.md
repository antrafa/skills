# Step 4 — TDD

**Iron law: no production code without a test that failed first.** Code written
before its test is deleted and rewritten from the test, not kept "as reference"
and adapted: adapting it is testing after.

## The cycle

Each stage ends on something you observe, not something you assume.

1. **Red.** One test, one behavior, a name that states the behavior. Real code;
   mock only a boundary you cannot run (network, clock, third-party API).
   Before writing it, name the production change that would make it fail.
2. **Watch it fail.** Run it. It must *fail* (not error out), with the expected
   message, because the behavior is missing. Passes on the first run? It tests
   something that already exists: fix the test. Errors out? Fix the error and
   run again until it fails for the right reason.
3. **Green.** The simplest code that makes it pass. No option, parameter or
   extension point the test does not demand.
4. **Watch it pass.** Run the test, then the project's whole suite with the
   repository's own command, not just your file. The output is clean. A failure
   you did not cause still goes in the report, by name.
5. **Refactor.** Only on green: names, duplication. The suite stays green and
   no behavior is added.

A **bug fix** starts with a test that reproduces the symptom and goes red.
**Legacy with no tests** starts with a characterization test that pins down
today's behavior, then the change goes through the cycle.

Exceptions only with the user's explicit yes: a throwaway spike, generated code,
a configuration file. The handoff records the exception.

## Excuses and the answer to each

| Excuse | Answer |
|---|---|
| "Too simple to test" | Simple code breaks too; the test costs thirty seconds. |
| "I'll test it afterwards" | A test written after passes on its first run and proves nothing: you never saw it catch the bug. |
| "I already tested it by hand" | No record, cannot be rerun, and the forgotten case is the one that breaks. |
| "Deleting this code wastes the hours spent" | Sunk cost. The choice is between code you can trust and code you cannot. |
| "I need to explore first" | Explore, throw the exploration away, start from the test. |
| "It is hard to test" | Hard to test means hard to use: simplify the interface. |

**Red flags** — any of these means deleting the code and starting again from
red: code before its test; a test that passes on the first run; not being able
to say why the test failed; "just this once"; "this case is different".

## Done when

Every new behavior has a test that was seen red and then green, the whole suite
is green with no skipped test, and the handoff shows the red run and the green
run: command and result.
