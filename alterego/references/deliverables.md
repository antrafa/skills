# Deliverables

Formal output templates of the `alterego` skill, standardized by reader and by
type of deliverable.

---

## 1. ADR (Architecture Decision Record) — `adr.md`
For whoever will implement, review or reopen the subject in the future.
Canonical destination: `~/.alterego/decisions/<YYYY-MM-DD>-<slug>/adr.md`.

```markdown
---
decision: <affirmative sentence>
project: <short name of the system>
context: <client / environment>
date: <YYYY-MM-DD>
status: proposed # proposed | accepted | superseded | revoked
superseded-by: null # slug of the superseding decision when status = superseded
quadrant: reversible-cheap # reversible-cheap | reversible-expensive | irreversible-cheap | irreversible-expensive
reopen-when: <concrete, measured trigger>
sources: [<paths of the artifacts used>]
---

# <The decision as one affirmative sentence>

- **Who decides:** <role with technical authority>
- **Originating context:** <report, incident, MR, issue or ticket>

## Context
What is true today and why this needs to be decided now. Every data point
labeled: **measured** (with source), **hypothesis** (measurement pending) or
**premise** (who stated it).

## Decision
<One direct sentence. What will be done.>
Quadrant: <reversible|irreversible> × <cheap|expensive>.

## Discarded options

### <Closest discarded option>
- **What it would solve:**
- **Why it was discarded:** <concrete cost/complexity reason, not "it's not best practice">
- **What would bring it back:** <trigger or number that would reopen the option>

### Do nothing
- **Cost of not deciding:** <the progressive impact of inaction>
- **How long this option holds:**

## Consequences
- **We gain:**
- **We lose / start living with:**
- **Cost:** infra, licensing, maintenance effort, who gets woken up at 3 a.m. if it fails.

## What reopens this decision
<Concrete trigger: metric, date or event specified in the frontmatter.>
```

The semantics of each frontmatter field — and what makes the archive age well —
are in [archive.md](archive.md#adrmd-frontmatter). For a text value containing
`: `, use quotes or a YAML block.

---

## 2. One Page for Whoever Authorizes — `decision.md`
For management, coordination and non-technical leadership.
Destination: `~/.alterego/decisions/<YYYY-MM-DD>-<slug>/decision.md`.

```markdown
# <Subject in Business Language>

## What is happening
<Two clear paragraphs, no cryptic terms or unexplained acronyms.>

## What needs to be decided
<The executive choice required, in one sentence.>

## Technical recommendation
<The recommended option and what it gives up.>

## If nothing is decided
<The consequence for the product or the team, with an estimated timeframe.>

## What it costs
<Impact on time, infrastructure or risk, in clear comparative terms.>

## What is already working and will be kept
<Acknowledgment of what is stable, to avoid the perception of total chaos.>

## What only management can arbitrate
<Strict separation between technical merit and budget/priority decisions.>
```

---

## 3. Five-Minute Script — `script.md`
For leading technical defenses and quick alignments in meetings (delivered to
the archive and inline).

```markdown
**Opening (1 sentence):** <the problem from the listener's perspective>

**Supporting numbers:** <up to two essential numbers with their source, or the pending measurement>

**The choice:** <recommended option> instead of <discarded option>, because <core reason in one line>.

**Most likely objection:** "<the doubt or concern most likely to come from the room>"
**Calibrated answer:** <calm, firm, data-backed answer>

**The ask:** <the agreement that needs to come out of this meeting today>
```

---

## 4. Socratic Code Review Verdict (MR / PR)
For developers and team engineers. Delivered inline; post a comment on the MR
only when asked — and only after the gate in `references/mr-flow.md`. If there
are no findings, answer with the verdict and the verified scope, without filling
in the problem and fix blocks.

This is the **formal** template. For a remote MR in the terminal, use the dense
format from `references/mr-flow.md`; the criteria, severity and verdict ruler
are in `references/playbook-review.md`.

````markdown
### Technical Review — [MR / File identifier]

#### 1. Critical Points & Scenarios
- **Location:** `path/file.ext:line`
- **Scenario:** *"[Socratic question about the edge case, concurrency or data volume]"*
- **Risk:** [Real impact on the database, pool, memory or consistency]
- **Evidence and severity:** [Code, contract or reproduction actually read; Critical, Warning or Note]

#### 2. Fix or Next Investigation
If there is a well-founded fix:
```java
// Concise snippet with the exact recommended fix
```
*Rationale:* [Why this solution is simpler and more sustainable]

If the fix depends on missing information:
- **Gap:** [Contract, context or measurement required]
- **Next check:** [How to obtain the evidence to choose the patch]

#### 3. Overall Assessment & Verdict
- **Strengths:** [Honest praise for the code's strong points]
- **Verified scope and limitations:** [Files, contracts and tests actually examined]
- **Verdict:** [No findings in the reviewed scope | Approved with minor reservations | Awaiting changes | Inconclusive review]
````

---

## 5. SRE Diagnostic Memo & Incident Investigation
For production incidents, restarting pods, stuck requests or resource
exhaustion.

```markdown
# Diagnostic Memo: [System / Incident]

- **Date / Time:** <event timestamp>
- **Environment:** <K8s cluster / Namespace / Host>
- **Target:** <Pod / Container / Service>

## 1. Symptom & Behavior
<What hung or degraded, as observed by clients/users.>

## 2. Measured Evidence (Facts)
- **Collection source and window:** <source, timestamp, duration, units and gaps>
- **Process status:** <PID, CPU/memory usage and limits>
- **Thread dumps:** <states, stacks, lock dependencies and sampling limits>
- **SQL per operation:** <correlated queries, entity count or collection pending>
- **Network:** <packets/connections observed; not equivalent to queries>
- **Container metrics:** <cgroup version and path, usage/limits and deltas of high, max, oom, oom_kill>

## 3. Conclusion and Degree of Evidence
- **Investigation state:** <proven cause | hypothesis under investigation | insufficient data>
- **Mechanism and evidence:** <what is demonstrated and what is hypothesis>
- **Pending measurement:** <what is missing to tell the hypotheses apart; not applicable if already proven>

## 4. Immediate Mitigation Action
- **Action state:** <proposed | applied | no intervention>
- **Command:** `<command proposed or actually applied>`
- **Rollback plan:** `<how to undo it if it fails>`
- **Validation:** <result measured after execution, or validation still pending>

## 5. Fix or Next Investigation
<Well-founded fix with the smallest diff, or the next experiment required; owner and validation criterion when known.>
```

---

## 6. Planning by Concrete Deliveries
Use verifiable results as the axis. Include a deadline or estimate when the
request calls for it, with explicit premises and dependencies.

```markdown
### Delivery 1 — <Observable result in the product>
- **What it touches:** <files, tables, containers>
- **How to validate it worked:** <measurable metric in production>
- **Rollback criterion:** <command or flag reversal>
- **Effort:** <logical order of magnitude>

### Delivery 2 — <Next result>
...
```

---

## 7. Closing a Step in the Dev Pipeline (`/alterego dev`)

The roadmap widget and the Safe Context-Clear notice are in
[playbook-dev.md](playbook-dev.md#guided-conduction-the-mandatory-roadmap-widget).
There is no second version of them.
