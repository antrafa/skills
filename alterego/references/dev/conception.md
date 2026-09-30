# Step 1 — Conception

The outcome is an understanding the user recognizes and corrects, grounded in
what they want to get done — not a feature list.

## 1. Classify before the first question

Say the path out loud so the user can override it:

- **Spike** — a feasibility question ("can we…", "does it work if…"). The output
  is an answer, not code that stays. Present the question and the probe in 2–3
  sentences, get a nod, find out as cheaply as correctness allows, report a
  recommendation. Anything built is labeled throwaway.
- **Bounded** — a change to a flow that **already exists in this repository**:
  a flag, a small endpoint, a one-file fix. The questions that matter, then the
  design in the chat, always in this shape:

  ```markdown
  **Current:** what happens today, with the file:line that shows it
  **Expected:** what happens after the change
  **Probable files:** path — why, one per line
  **Tested by:** the test that goes red first
  **Criteria:** AC-01 given <context>, when <action>, then <result> (one to three)
  ```

  No spec file. The criteria in the chat are the contract the review's
  Acceptance lens checks and step 6 rereads before the commit.
- **Architectural** — a new project or subsystem, or a change to how components
  fit together or to an interface others depend on. The full path below.

When in doubt, take the heavier one. Complexity found mid-task moves the work up
a path — stop and say so; nothing moves down.

## 2. The architectural path

1. **Read the context:** files, docs, recent commits. Too big for one spec?
   Split it into sub-projects first, each with its own spec, plan and delivery.
2. **Write back the understanding** — outcome, constraints, success criteria —
   separating what the user said from what you assume, then ask as in
   [Asking](#asking) below.
3. **2 or 3 approaches** with their trade-offs, the recommended one first, the
   comparison as in [playbook-decision.md](../playbook-decision.md).
4. **Design in sections** sized to their complexity — components, data flow,
   errors, tests — confirming each section before the next.
5. **Write the spec** in
   `~/.alterego/work/<project>/specs/YYYY-MM-DD-<topic>-design.md`, outside the
   repository ([where and why](../archive.md#working-files-outside-the-repository-always)).
   Its sections, in this order: **Context** (the problem and the outcome it
   serves), **Current behavior**, **Expected behavior**, **Scope** (in and,
   explicitly, out), **Approach** (the chosen one and the discarded ones),
   **Probable files** (path and why, per repository), **Risks and dependencies**,
   **Acceptance criteria**, **Sources** (only what was actually read: file:line,
   doc, the user's words). The acceptance criteria are numbered and observable:
   `AC-01: given <context>, when <action>, then <result>`.
6. **Self-review the spec:** any TBD or vague requirement, sections that
   contradict each other, a requirement readable two ways, scope too big for
   one plan. Fix inline.
7. **User reviews the spec file.** It stays outside the repository; nothing to commit.

## Asking

Every question costs the user a round trip. Ask fewer, better, at once.

1. **Look before asking.** Pair each doubt with what already answers it: the
   request, this conversation, the code, the repository's docs, Mentat. Never ask
   what is answered there; a partial but plausible answer counts as answered —
   state it as an assumption instead.
2. **Hypothesis first.** Open with your reading of the impact — the files or
   repositories it touches, why, and how sure you are — so the user corrects a
   draft instead of dictating one.
3. **One round, every open question in it,** numbered, grouped: *Scope* (what
   is in, and explicitly out), *Actors*, *Constraints*, *Data and integrations*.
   Each is one sentence plus why you ask; a closed one lists its options as
   (a), (b).
4. **At most three rounds.** Still not converging means the discovery is
   failing, not that a fourth round is needed: say so, list what is still open,
   and suggest settling it live with whoever owns the answer.
5. **Ask rather than write around a hole.** A TBD in the spec or the design is a
   question that was not asked.

## The gate

Nothing that implements — product code, scaffolding, installing a dependency —
before the path's approval: the nod for a spike, the yes to the in-chat design
for bounded work, the reviewed spec for architectural work. An approval covers
the stage that was presented: approving the idea is not approving a spec that
does not exist yet. Reading the project is allowed all along.

| Excuse | Answer |
|---|---|
| "Too simple to need a design" | Bounded work gets two sentences in the chat — and still waits for the yes. |
| "I'll call it bounded and skip the spec" | Reaching for the lighter label to skip work is the doubt: take the heavier path. |
| "I know this kind of app, so it's bounded" | Bounded measures the repository, not your familiarity. No existing flow, not bounded. |
| "One question per message is friendlier" | Five questions are five round trips. One numbered round respects the user's time. |
| "The criteria are obvious for a bounded change" | Then they take one line to write, and review has something to check. |
| "The spike worked, I'll keep the code" | A spike's output is an answer. Keeping the code is a new request — classify it. |

## Done when

The path is announced; the approach is chosen with its rationale; the bounded
design is in the chat with its criteria; and, on the architectural path, the
spec is saved with numbered acceptance criteria and reviewed by the user.
