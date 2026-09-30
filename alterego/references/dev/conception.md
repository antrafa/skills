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
  a flag, a small endpoint, a one-file fix. The clarifying questions that
  matter, then a short design in the chat: approach, files touched, how it is
  tested. No spec file.
- **Architectural** — a new project or subsystem, or a change to how components
  fit together or to an interface others depend on. The full path below.

When in doubt, take the heavier one. Complexity found mid-task moves the work up
a path — stop and say so; nothing moves down.

## 2. The architectural path

1. **Read the context:** files, docs, recent commits. Too big for one spec?
   Split it into sub-projects first, each with its own spec, plan and delivery.
2. **Write back the understanding** — outcome, constraints, success criteria —
   separating what the user said from what you assume. One question per
   message.
3. **2 or 3 approaches** with their trade-offs, the recommended one first, the
   comparison as in [playbook-decision.md](../playbook-decision.md).
4. **Design in sections** sized to their complexity — components, data flow,
   errors, tests — confirming each section before the next.
5. **Write the spec** in `~/.alterego/work/<project>/specs/YYYY-MM-DD-<topic>-design.md`, outside the
   repository ([where and why](../archive.md#working-files-outside-the-repository-always)). It carries the chosen approach and the discarded
   ones, and the **acceptance criteria**, numbered and observable:
   `AC-01: given <context>, when <action>, then <result>`.
6. **Self-review the spec:** any TBD or vague requirement, sections that
   contradict each other, a requirement readable two ways, scope too big for
   one plan. Fix inline.
7. **User reviews the spec file.** Committing it follows *Autonomy and limits*.

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
| "The spike worked, I'll keep the code" | A spike's output is an answer. Keeping the code is a new request — classify it. |

## Done when

The path is announced; the approach is chosen with its rationale; and, on the
architectural path, the spec is saved with numbered acceptance criteria and
reviewed by the user.
