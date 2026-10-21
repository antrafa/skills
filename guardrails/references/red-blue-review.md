# Red team / blue team review

Two reviewers analyze the same change with opposite goals. The blue team
checks whether it solves what was agreed. The red team tries to prove it is
wrong. Independence is what gives the method its value: a reviewer who reads
the other's conclusion tends to agree with it.

## Material for both

Both receive the same package, and nothing beyond it:

- the original description of the problem;
- the plan agreed with the user (rule 18);
- the full diff of the change (`git diff <base>`, including what has not been
  committed);
- the tests created and the output of their last run.

## Blue team — validate

- Is every item of the plan implemented and covered by a test?
- Do the tests exercise the behavior or do they just pass? A weak assertion
  and a mock that returns exactly the expected value without going through the
  logic are the common cases.
- Who else uses the changed code? Are those callers still covered?
- Does the change follow the style and patterns that already exist in the
  repository?

## Red team — attack

Skeptical on purpose:

- Is the fixed cause the root, or a symptom of it?
- Inputs that break: null, empty list, boundary value, date and time zone,
  encoding, large number, concurrency, timeout, network down.
- Security: authorization, input validation, data exposed in a response or
  log.
- Side effects on other screens, endpoints, jobs or API consumers.
- Is there a simpler or safer solution that was discarded too early?
- Does any test pass for the wrong reason?

When possible, the red team demonstrates the failure with a quick test in a
temporary directory, outside the repository and without touching production
code.

## Execution

**With subagents:** dispatch both in parallel, each with the package and only
its own mission. These are read-only reviews; the prompt says explicitly that
they may not edit any repository file, commit, or run any command that changes
state.

**Without subagents:** in sequence, red first and then blue, in separate
sections, genuinely taking on each one's stance.

## What each team returns

- Verdict: `solid`, `solid with caveats` or `problematic` (in the user's
  language; in Portuguese: `sólida`, `sólida com ressalvas`, `problemática`).
- Findings, each with a severity (high, medium or low), evidence (file and
  line, test or output) and a suggestion.

## Synthesis for the user

Written in the user's language.

1. Where the two agree — the most reliable part.
2. Where they disagree, which side seems right and why.
3. High-severity findings first.
4. Final recommendation: keep, adjust or rethink.

No fix is applied here. Whatever the review suggests goes back to discussion
and waits for a new approval.
