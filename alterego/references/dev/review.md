# Step 5 — Review in a separate context

The context that wrote the code sees what it meant to write, not what it wrote.
The review runs in a **fresh reviewer** that gets the work product, never the
session's history.

## How to run it

1. **Collect the range:** `BASE=$(git merge-base <base-branch> HEAD)` and
   `HEAD=$(git rev-parse HEAD)`, with the base confirmed in step 3.
2. **Dispatch the reviewer.** On Claude Code, the `Agent` tool with a fresh
   `general-purpose` subagent, not a `fork` — a fork inherits the history the
   review must not see. On a harness without subagents, run the review as a
   separate pass that reads only the plan and the diff, and record in the
   handoff that it was not independent.
   When the diff crosses the threshold in
   [review-squad.md](../review-squad.md#1-when-the-squad-runs), dispatch the squad
   instead of the single reviewer below, with the plan (and the spec, on the
   architectural path) as its written criteria, so the Acceptance lens runs.
3. **Act on the verdict.** Critical: fix now. Warning: fix before step 6. Note:
   record it. When the reviewer is wrong, answer with the code or the test that
   shows it, not with an opinion.

## The reviewer's prompt

Fill in the braces; `{REVIEW_PLAYBOOK}` is the absolute path of
[playbook-review.md](../playbook-review.md) in this skill's directory.

```
You review a finished change. Your review is read-only: do not modify the working
tree, the index, HEAD or any branch. Inspect with git show, git diff and git log;
if you need another revision, check it out into a temporary worktree. Do all of
the review yourself, without dispatching subagents.

What was built: {DESCRIPTION}
Plan or requirements: {PLAN_PATH_OR_TEXT}
Range: git diff --stat {BASE}..{HEAD} and git diff {BASE}..{HEAD}

Read {REVIEW_PLAYBOOK} and apply its hunting yardstick, severities and verdict
table. Every finding cites the file and line you actually read.

Where the plan is silent, judge by what a reasonable user of this software would
expect: silence in the plan is not permission.

Before the verdict, list every behavior you set aside as outside the plan, one
line each, with the reason. An empty list means you set nothing aside.

Return: what was done well (specific), the findings by severity with file:line,
the risk and the fix, and one verdict from the table.
```

## Excuses and the answer to each

| Excuse | Answer |
|---|---|
| "I'll review the diff myself, it's faster" | You review your intention. The fresh reviewer reviews the code. |
| "It's a simple change" | Simple diffs are where nobody looks. |
| "The reviewer needs the whole conversation" | It needs the plan and the diff; the conversation brings your reasoning along with it. |

## Done when

The reviewer's verdict is in the handoff, and no Critical or Warning finding is
left open — each one fixed or answered with evidence.
