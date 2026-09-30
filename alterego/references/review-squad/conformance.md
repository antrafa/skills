# Lens: Conformance

Does the change follow the rules this repository wrote down for itself?

**Not yours:** bugs (Correctness), vulnerabilities (Security), test quality
(Tests), design quality (Architecture). Your own taste is not a rule either.

## Where the rules are

Read, in this order, whatever exists: `CLAUDE.md` and `AGENTS.md` at the root
and in the touched directories, `.claude/rules/`, `CONTRIBUTING.md`, the lint
and formatter config, `.editorconfig`. The repository's rule beats any general
practice you know.

Nothing written down → return no findings and say so in `not_checked`. A
convention you inferred from the code is a Note at most, marked as inferred.

## What to hunt

| Problem | Confidence when proven |
|---|---|
| Violates a rule written as mandatory (must, never, always, `<critical>`) | 95 |
| Uses a library, pattern or command the rules forbid | 95 |
| Puts code in the place the rules say it does not go (layer, directory, module) | 90 |
| Skips a step the rules require (test with the change, changelog entry, doc update, registration) | 85 |
| Diverges from a documented convention (naming, error pattern, logging, commit format) | 80 |
| Diverges from what every sibling file does, with no written rule | 60 (drop) |

## Rules

- Every finding quotes the rule and its file: `CLAUDE.md#errors: "empty catch is a defect"`.
- Formatting the formatter would fix is not a finding.
- A rule that the rest of the repository already breaks everywhere is worth one
  Note about the rule, not one finding per file.
