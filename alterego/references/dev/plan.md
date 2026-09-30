# Step 2 — Plan

The plan is written for an engineer who knows the craft but not this codebase
nor this problem. It argues from the spec, and the spec travels with it.

Save it in `~/.alterego/work/<project>/plans/YYYY-MM-DD-<feature>.md`, outside the repository
([where and why](../archive.md#working-files-outside-the-repository-always)). A spec covering independent subsystems becomes one plan per subsystem,
each producing working, testable software on its own.

## Structure

**Header:**
- **Goal** in one sentence; **Spec:** the path to the spec it implements.
- **Architecture** in 2–3 sentences; **Stack** with the version assumed for
  each dependency.
- **Global constraints** — version floors, naming rules, platform limits —
  copied verbatim from the spec, one line each. Every task inherits them.
- **Review focus** — up to five inputs or conditions the spec implies but no
  test exercises yet, each with the behavior a reasonable user would expect.
  Each line then gets its test in the task that owns the code.

**File map** before the tasks: which files are created or changed and what each
one is responsible for. Follow the patterns the repository already has.

**Each task** is the smallest unit with its own test cycle that a reviewer could
reject while approving its neighbor. The first task is the **walking skeleton**.
Each one carries:
- **Files:** exact paths to create, change (with lines) and test.
- **Interfaces:** what it consumes from earlier tasks and what it produces for
  later ones, with exact names and types.
- **Acceptance criteria** it covers, by ID (`AC-01`).
- **Steps** of one action each, with checkboxes: write the failing test — run
  it and see it fail, with the command and the expected failure — minimal code
  — run it and see it pass — commit.

## No placeholders

Each of these is a hole in the plan: "TBD", "TODO", "fill in later"; "handle
errors appropriately", "add validation"; "write tests for the above" without the
test; "same as task N" (the reader may go out of order); a type or function that
no task defines.

## Self-review

With the spec open: every requirement and acceptance criterion points to a
task; no placeholder is left; names and signatures match across tasks
(`clearLayers()` in task 3 and `clearAllLayers()` in task 7 is a bug); every
line of the review focus has its test. Fix inline; a requirement with no task
gets the task.

## Done when

The plan is saved, self-reviewed, every acceptance criterion maps to at least
one task, and the user approved it.
