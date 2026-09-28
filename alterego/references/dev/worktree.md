# Step 3 — Isolation

The work leaves the main checkout before the first line of code, and the
baseline is known before anything changes.

## How to run it

1. **Detect existing isolation.** Compare `git rev-parse --git-dir` with
   `git rev-parse --git-common-dir`. Different paths mean a linked worktree —
   unless `git rev-parse --show-superproject-working-tree` prints a path, which
   means a submodule. Already in a linked worktree: skip creation and report the
   path and branch.
2. **Name and base confirmed with the user**, per *Autonomy and limits* in
   `SKILL.md`. The base can be a release or maintenance branch; ask when it was
   not given.
3. **Create it with the harness's own tool first** (on Claude Code,
   `EnterWorktree`, when it accepts the confirmed base): it owns placement and
   cleanup, and a manual `git worktree add` alongside it leaves state the
   harness cannot see. Without one, `git worktree add -b <name> <path> <base>`.
4. **Directory:** the user's stated preference; otherwise an existing
   `.worktrees/` or `worktrees/` in the project; otherwise a sibling directory
   outside the repository. A directory inside the project must be git-ignored
   (`git check-ignore -q <dir>`) — when it is not, propose the `.gitignore` line
   and wait for the yes, since it is a change to the repository.
5. **Baseline.** Install the project's locked dependencies and run its test
   command. A red baseline is reported and the user decides whether to go on:
   every later failure becomes ambiguous otherwise.

## Excuses and the answer to each

| Excuse | Answer |
|---|---|
| "Obviously this is not a worktree" | Run step 1: harness-made worktrees and submodules fool the eye. |
| "The base is obviously main" | Ask. A branch from the wrong base only shows up at merge time. |
| "The directory is surely ignored" | Run `git check-ignore`. An unignored worktree commits a whole tree. |
| "The baseline can wait" | A red baseline found later looks like your bug. |

## Done when

The handoff shows the worktree path, the branch, the confirmed base and the
baseline: the test command, the number of tests and the failures.
