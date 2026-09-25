# Playbook: Socratic Code Review & Impact Analysis

This playbook guides the review of Merge Requests, Pull Requests, code diffs and
technical implementation proposals. It defines **what to look for, how to
classify it and how to write the review verdict**.

When the target is a remote MR/PR, the mechanics of getting to the code —
finding the MR, setting up a worktree, measuring impact beyond the diff, the
posting gate — live in [mr-flow.md](mr-flow.md). When the target is a local
file or diff, this playbook is enough.

The stance is one of **constructive technical leadership**: the goal is not to
show off erudition but to **make the team and the product better**, raising
code quality with empathy and technical firmness.

---

## Core stance: the Socratic method

When you spot a serious problem or technical risk, **do not open by giving
orders or belittling the implementation**:

1. **Ask the edge-case question:** frame a focused question that leads the
   author to see the flaw on their own.
   - *Concurrency example:* *"What happens to this shared instance if two
     requests land here at the same time?"*
   - *Database/N+1 example:* *"If this collection has 200 items in production,
     how many round trips to the database does this loop fire?"*
   - *Resilience example:* *"If the downstream service times out after 30s on
     this synchronous call, who absorbs the stalled threads?"*
2. **Give a concrete way forward:** present the fix in the **smallest diff**
   pattern when it is well grounded. If the contract, context or measurement
   needed to pick the patch is missing, report the proven defect, the impact
   and the investigation required. A missing patch does not lower the
   finding's severity.

### Three rules that apply before any finding

- **Don't review from memory.** Every finding needs a file and line actually
  read, on the ref under review. If the diff gives no context, open the whole
  file before asserting anything.
- **A finding without evidence is dropped, not downgraded** to "warning".
- **The project's written rule beats your preference.** Before pointing out
  style, read `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, `CONTRIBUTING.md` and
  the lint config. If the baseline was inferred, say so in the review verdict.

---

## The Hunting Yardstick — in order of the cost of being wrong

### 1. Correctness
Logic bug, off-by-one, unhandled null, inverted condition, swallowed error,
resource not closed. And, with special attention, **concurrency and
resources**:

- Shared mutable state in Spring Singletons/Beans.
- Database connections, streams, sockets or files opened without safe closing
  (`try-with-resources`).
- Potential deadlocks: multiple locks acquired in different orders.
- Slow I/O operations inside active database transactions (holding a pool
  connection for too long).

### 2. Security (OWASP Top 10)
Input at a trust boundary without validation, injection, hardcoded secret,
missing authorization, personal data in logs (LGPD). **Confirm the path is
reachable** before reporting.

### 3. Data loss
Destructive migration, write without a transaction, non-idempotent retry.

### 4. Contract
Signature change, field removed from a DTO/response, new enum the consumer
does not know, altered event or topic.

### 5. Performance — actively hunt N+1 and ORM abuse
- Loops (`for`, `forEach`, `stream`) running queries, repository calls or
  Hibernate/JPA lazy-loading navigations.
- Careless use of `FetchType.EAGER` or `@ManyToOne` without a planned fetch in
  lists.
- Loading full JPA entities into memory when only 2 fields were needed
  (missing projection/DTO).
- No pagination or limits on queries that grow over time.
- Missing index for the new filter; synchronous call on a hot path.

### 6. Tests with real value
- Does the new behavior have a test? Does the test **fail** if the logic is
  reverted? A test tweaked just to pass is a finding.
- Weed out theatrical tests: those that mock the business logic itself, test
  getters/setters, or are 90% mock setup to assert `assertNotNull`.
- Demand tests that exercise real behavior, edge cases and an actual
  regression of the reported failure.

### 7. Scope and smallest diff
- **The task's scope is the action's scope:** the MR must solve the stated
  problem and nothing else. An unannounced change is a process finding.
- Point out opportunistic refactors, mass renames outside the scope or
  cosmetic formatting changes that pollute the git history.
- Ask: *"Is this change essential to the current delivery, or can it be split
  into a separate improvement?"*

### 8. Readability > cleverness & YAGNI
Severity **Note** by default — it only goes up when the code has already shown
a real cost.

- Reject "clever" code: cryptic tricks, mile-long stream/lambda chains nobody
  can debug at 3 a.m.
- Simple > generic: cut premature abstractions, factories for a single class,
  empty interfaces with no plausible second implementer.
- The person who will maintain this code in 6 months is not in this
  conversation: optimize for them.

---

## Severity and verdict

**Severity:**

| Level | When |
|---|---|
| **Critical** | Breakage, data loss, reachable security flaw |
| **Warning** | Works, but will cost later |
| **Note** | Preference or readability, no proven cost |

**The label, when the finding is posted.** The dense terminal format is for the
user; a comment that goes to the MR is read by someone else, and what they need
first is whether it blocks. [Conventional Comments](https://conventionalcomments.org/)
is the market standard for that, and it maps onto the severity above:

| Severity | Label on the comment |
|---|---|
| Critical | `issue (blocking):` |
| Warning | `issue (non-blocking):` or `suggestion (non-blocking):` |
| Note | `nit (non-blocking):` |
| — | `question:` for a real question, when the answer might be that there is no problem |
| — | `praise:` for what was done well |

The label states the severity, it never softens it: `nit:` on something that
breaks is dishonest, and a `question:` whose answer you already know is a
finding in disguise — post it as `issue:`. `praise:` is the one piece of
non-finding content that earns its place in a review, and it is not filler:
point at something specific.

**Approve when the change improves the code's overall health, even if it is not
perfect** (Google's *Code Review Developer Guide*). Reviewing against "how I
would have written it" blocks deliveries and teaches nothing. The question is
whether the codebase gets better with this merged — if it does and there is no
critical, the verdict is approval with the notes attached, not a request for
changes.

**Verdict** — a single one, stated without drama:

| Verdict | Rule |
|---|---|
| **No findings in the reviewed scope** | No problem identified; state what was checked |
| **Approved with minor reservations** | No critical, up to 3 warnings |
| **Awaiting changes** | At least 1 critical, or more than 3 warnings |
| **Inconclusive review** | Essential evidence to assess is missing; spell out what is missing |

*Inconclusive review* is the right verdict when fetching the ref failed, the
consumer's contract is not visible locally, or the requested focus needed a
measurement that does not exist. Do not force a verdict on the merits over an
incomplete base.

---

## Review verdict format

Three blocks. If there are no findings, deliver the verdict and the checked
scope in a few lines, including relevant limitations of the review. For a
remote MR, the dense terminal format is in [mr-flow.md](mr-flow.md); the
formal, publishable template is in [deliverables.md](deliverables.md).

### 1. Points of attention & Socratic questions
For each finding:
- **Where:** file and exact line (`file.ext:line`).
- **Scenario / question:** the Socratic question that brings the edge case to
  the surface.
- **Real risk:** concrete impact (connection pool exhaustion, deadlock, CPU
  starvation, lost data).
- **Evidence and severity:** the code, contract or reproduction that supports
  the finding, with the severity from the table above.

### 2. Fix or next investigation
- When there is a well-grounded fix, present the snippet with the smallest
  diff.
- When information to choose the fix is missing, spell out the gap and the
  next check. Keep the finding and its severity without inventing a patch.
- If there is a relevant trade-off (e.g. memory usage vs. latency), state it
  in one line.

### 3. Overall assessment & verdict
- Acknowledge what was done well (clear naming, good edge-case test coverage,
  an elegant solution to a rule).
- State the scope that was checked and what was left out, and why.
- State the verdict.

---

## Review closing checklist
- [ ] Calm, respectful and didactic tone kept in every comment?
- [ ] Does every criticism have evidence read in the code, impact, and a
      well-grounded fix or a pending investigation?
- [ ] Were correctness, security and data loss checked before aesthetics?
- [ ] Were N+1, leaks and concurrency checked before readability?
- [ ] Was the smallest diff favored over unnecessary refactors?
- [ ] Were tests judged by the behavior they verify, without demanding findings
      where there is no problem?
- [ ] Was what fell outside the review scope declared, not omitted?
