# Review Squad: Fresh Reviewers in Parallel, One Lens Each

The agent that wrote a change reviews what it meant to write. When a session has
produced a large diff, the review goes to **fresh reviewers** that see only the
work product, each one hunting a single kind of problem, and their findings come
back through a verification pass before the user sees them.

This file covers orchestration: when to call the squad, which lenses, the prompt,
consolidation and verification. What to look for inside each lens lives in
[review-squad/](review-squad/), one file per lens. Severities and the verdict
table are the ones in [playbook-review.md](playbook-review.md#severity-and-verdict).

---

## 1. When the squad runs

| Diff | Review |
|---|---|
| Up to ~150 changed lines and up to 5 files, no infrastructure file | A single pass by [playbook-review.md](playbook-review.md), in this context |
| Larger, or any infrastructure file (manifest, Helm, compose, Dockerfile, Terraform, CI pipeline, deploy or database script) | The squad |
| The user asks for it ("com o squad", "com os agentes") | The squad, whatever the size |
| The user asks for a quick look | A single pass, whatever the size |

Below the threshold the squad costs three to five times the tokens of one pass
and finds the same thing. State in one line which one was chosen and why.

## 2. Collect the range

The target of `review` with no argument is **the work on the current branch**:
commits since the base plus what is not committed yet.

```bash
BASE=$(git merge-base HEAD <base-branch>)
git diff --stat $BASE            # committed + staged + unstaged, against the base
git ls-files --others --exclude-standard   # new files git does not track yet
```

The base is the one confirmed in the session (the branch this work was created
from). Without that, use the remote's default branch
(`git symbolic-ref --short refs/remotes/origin/HEAD`) and say it was assumed. New
untracked files are part of the change: list them for the reviewers by path.

## 3. Pick the lenses

| Lens | Runs when | File |
|---|---|---|
| Correctness | Always | [correctness.md](review-squad/correctness.md) |
| Conformance | Always, when the repository has written rules (`CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, `CONTRIBUTING.md`, lint config) | [conformance.md](review-squad/conformance.md) |
| Security | The diff touches input from outside, auth, secrets, config, dependencies, CI or infrastructure | [security.md](review-squad/security.md) |
| State and rollback | Any infrastructure file, migration or script that changes a server, a cluster or a database | [infra-state.md](review-squad/infra-state.md) |
| Tests | Production code changed in a repository that has tests | [tests.md](review-squad/tests.md) |
| Architecture | New module or directory, new dependency, change to a shared or public contract, imports across layers | [architecture.md](review-squad/architecture.md) |
| Approach | What the change is for is stated: a bug fix, a request from the session, a spec | [approach.md](review-squad/approach.md) |
| Acceptance | There are written criteria: a spec or plan in `~/.alterego/work/<project>/`, the criteria of a bounded design, or requirements the user gave | [acceptance.md](review-squad/acceptance.md) |

**At most five per run.** More than that and consolidation costs more than the
extra lens finds. If more than five apply, drop Architecture first, then Tests, then Approach,
and say which ones were left out.

## 4. Run the scanners that are installed

Scanners read the code without running it, so you run them before the dispatch
and hand their output to the Security lens as evidence. Each one runs when it is
installed (`command -v <tool>`) and the change gives it something to read:

| Scanner | Runs when | Command |
|---|---|---|
| gitleaks | Always: a secret lands in any kind of file | Commits: `gitleaks git --no-banner --redact --log-opts="$BASE..HEAD"`. Uncommitted and new files: `gitleaks dir --no-banner --redact <file>`. Before gitleaks 8.19 the two are `gitleaks detect`, the second with `--no-git --source <file>`. |
| semgrep | The Security lens runs and code files changed | `semgrep scan --config p/default --metrics=off --quiet <changed code files>` |
| Dependency audit | A manifest or lockfile changed | The one for the ecosystem: `npm audit --omit=dev --audit-level=high`, `pip-audit`, `govulncheck ./...` |

- A secret gitleaks reports is a Critical with confidence 100, masked, with
  rotation, and goes straight into the verdict whichever lenses ran.
- A scanner that is missing, or that needs the network while offline, goes to
  *what was left out* with how to install or run it. The user installs; you
  report.

## 5. Dispatch

On Claude Code, one `Agent` call per lens, **all in the same message** so they
run in parallel, each a fresh `general-purpose` subagent. Not a `fork`: a fork
inherits the session history, which is exactly what the review must not see.

On a harness without subagents, run the lenses one after another as separate
passes, each reading only the diff and its lens file, and state in the verdict
that the review was not independent.

Fill in the braces. `{LENS_FILE}` is the absolute path of the lens file in this
skill's directory; `{REVIEW_PLAYBOOK}` is the absolute path of
[playbook-review.md](playbook-review.md).

```
You are one reviewer in a squad. Your review is read-only: do not modify the
working tree, the index, HEAD or any branch, and do not run builds or tests
(other reviewers are reading the same tree right now). Inspect with git diff,
git show, git log and by reading files. Do all of the review yourself, without
dispatching subagents.

Repository: {REPO_PATH}
Change: git diff {BASE} (committed and uncommitted), plus these new files:
{UNTRACKED_FILES}
What the change is for: {ONE_PARAGRAPH_FROM_THE_SESSION_OR_"not stated"}
Written criteria, if any: {SPEC_OR_PLAN_PATH_OR_"none"}
Scanner output for your lens, if any: {SCANNER_OUTPUT_OR_"none"}

Your lens: read {LENS_FILE}. Look only for what it covers; the lines under
"Not yours" belong to other reviewers, leave them alone.
Severities: the table under "Severity and verdict" in {REVIEW_PLAYBOOK}.

For every finding:
1. Read the whole file around the line, not just the hunk.
2. Confirm the problem is in this change, not pre-existing. Pre-existing goes
   in "set aside".
3. Give it a confidence from 0 to 100. Report only 75 or more.

Return only this JSON, nothing before or after it:
{
  "lens": "<lens name>",
  "findings": [
    {"file": "path", "line": 42, "severity": "critical|warning|note",
     "confidence": 90, "problem": "one sentence",
     "evidence": "the code or rule that proves it",
     "risk": "what happens in real use", "fix": "smallest diff or the next check"}
  ],
  "set_aside": ["one line each: what you saw and why it is not a finding here"],
  "not_checked": ["what your lens could not verify and why"]
}
```

## 6. Consolidate

1. **Parse each reply.** A reply that is not the JSON above, or a reviewer that
   failed, counts as that lens *not run*; say so, do not fill the gap by guessing.
2. **Merge duplicates.** Same file, lines within ~3 of each other, same problem:
   one finding, the higher severity, every lens that saw it listed.
3. **Keep disagreements.** When two lenses contradict each other on the same
   line, show both sides; the user decides.

## 7. Verify before showing

The reviewers are fresh; you are not. Verification is where that matters
again, so it has one job: **confirm the finding exists**, not argue it away.

For each Critical and Warning, open the file at the cited line and check that
the code says what the finding claims. Then:

- **Confirmed** → it stays, as reported.
- **The code does not say that** (wrong line, misread, already handled two
  lines below) → drop it, and count it in the verdict.
- **You disagree with the risk but the code is as described** → it stays; add
  your counterpoint with evidence next to it. Knowing what you meant to write is
  not evidence.

Notes are not re-verified one by one; keep the three most useful.

## 8. Deliver

The verdict format in [playbook-review.md](playbook-review.md#review-verdict-format),
with one extra line on top:

```markdown
Squad: correctness, conformance, security, infra-state (tests and architecture left out: no production code changed). Scanners: gitleaks clean, semgrep not installed. Base: `main` (assumed). 14 findings reported, 11 after merge, 2 dropped in verification.
```

Then findings by severity, each tagged with the lens that found it, and the
reviewers' `not_checked` lines under *what was left out*. Reviewing does not
authorize fixing: offer to fix the Criticals, and wait.

## Excuses and the answer to each

| Excuse | Answer |
|---|---|
| "I'll review it myself, I know what I changed" | That is why it goes to someone else. |
| "Five agents for this is overkill" | Then it is below the threshold, and a single pass is the right call. Say so. |
| "The reviewer got it wrong, drop it" | Drop it only if the code at that line says otherwise. |
| "Everything came back clean, it's approved" | Clean from which lenses? List the ones that did not run. |
