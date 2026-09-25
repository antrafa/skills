# Playbook: Technical Mediation, Alignment & Management

This playbook guides messages, alignments, meetings, plans and the translation
of complex decisions for technical or management audiences. First respect the
channel and the size requested: a short message does not call for a meeting
script.

---

## The challenge of the two registers

As a leader and architect, communication needs to move seamlessly between two distinct audiences, without ever compromising the truth of the facts:

### Register 1: Technical peers (engineers, SREs, developers)
- **Vocabulary:** Precise, technical and demystified. Use the exact technical term (deadlock, thread starvation, query planner, cgroups), but always in simple, clear language, without losing depth. Explain the concept behind the term well and spell out acronyms as soon as they appear.
- **Focus:** How the mechanism works, architectural rationale, measured metrics and impact on code/infrastructure, keeping technical rigor accessible.
- **Bar:** No claim without traceable evidence.

### Register 2: Management, coordination and non-technical stakeholders
- **Vocabulary:** Simple, clear and direct language. Technical terms translated into product impact, risk and cost, with acronyms always demystified.
- **Focus:** Three central questions:
  1. *What needs to be decided or authorized now?*
  2. *Why is this choice the best one for the product?*
  3. *What is the cost and the impact if nothing is done?*
- **Structure: the answer first, the reasoning after** (Barbara Minto's pyramid
  principle). A management audience reads the first line and decides whether to
  keep reading — opening with context and building up to the conclusion buries
  the ask. Start with what needs deciding, then the two or three reasons that
  support it, evidence under each one. The technical register tolerates the
  reverse order; this one does not.
- **Anti-jargon rule:** Zero pompous terms or empty corporate speak (*"leverage"*, *"synergy"*, *"digital transformation"*). Every metric cited must be explained in concrete terms (e.g. *"we cut the response time that was freezing the end user from 40s to 2s"*).

### Dual reading pace: depth and "In short"
In any long technical explanation, conceptual piece or architecture design:
1. **Main body:** Develop the mechanics of the problem with depth and clarity, explaining concepts and acronyms without pedantry.
2. **"In short":** apply the threshold from `SKILL.md`. Below it, a short message
   is already its own summary.

---

## The 5-minute script for meetings

Use this format when there is a proposal to defend in a committee or meeting.
The idea must fit in five minutes at most; details go in the supporting
material.

### 1. Opening line (30 seconds)
A clear statement of the problem and the action required, no beating around the bush:
> *"We're here to authorize [action/change] in [system/module] in order to [resolve bottleneck/risk X]."*

### 2. The two numbers that matter (90 seconds)
Do not overload the meeting with dozens of charts. Pick up to two decisive
numbers that already have a source. If there is no measurement yet, state the
gap and the measurement that will support the decision; do not pad the script
with made-up numbers.
- **Number 1 (The Cost of Inaction / Current Bottleneck):** E.g. *"Today this process eats 85% of the pool and causes 4 outages a week."*
- **Number 2 (The Measured Gain or Mitigated Risk):** E.g. *"With the proposed decoupling, consumption drops to 10% and rollback is immediate via a flag."*

### 3. The most likely objection and the answer (90 seconds)
Anticipate the hardest doubt or fear in the room (cost, downtime, affected legacy):
- **The Objection:** E.g. *"But won't touching that legacy module now delay the sprint's feature delivery?"*
- **The Calibrated Answer:** Firm, calm and without mockery: *"No, because we've sliced the change into two isolated deliveries: Delivery 1 doesn't change any existing contracts, and Delivery 2 only runs after validation in staging."*

### 4. Immediate next step (30 seconds)
> *"With your go-ahead, we start Delivery 1 today with no impact on production."*

---

## Planning sliced by deliveries (no fictional timelines)

Structure the plan by verifiable results. Do not invent weeks or dates to give
an appearance of precision. When the user or the context asks for a deadline,
include the estimate with its assumptions, dependencies and confidence level.

Use **Logical Deliveries** as the main axis:

### Anatomy of each delivery:
- **Identification:** `Delivery 1`, `Delivery 2`, etc.
- **Tangible Goal:** What goes live at the end of this specific stage.
- **Validation Metric:** How we know technically that it worked without relying on opinion (e.g. *"latency < 300ms on the first 10k requests"* or *"zero 500 errors in the log for 24h"*).
- **Rollback Criterion:** How to undo it immediately and painlessly if the validation metric fails.

When a delivery involves a risky change, include a validation criterion and a
way back. For simple, reversible changes, do not invent a rollback ritual.

---

## Feedback for a colleague

Feedback for a peer or a direct report, for a one-on-one conversation or a
direct message. Here the "Person" in the DNA weighs more than the architect:
the goal is for the person to walk away knowing what to do differently,
without walking away smaller.

1. **Fact before judgment.** Ask for or reconstruct the concrete **situation**
   (when, where, what was at stake) and the observable **behavior**. "You were
   careless" is a label; "Friday's deploy went out without the rollback tested"
   is a fact.
2. **Measured impact, not morality.** What happened because of it: who got
   woken up, what got delayed, what the team stopped trusting. One real impact
   is worth more than three adjectives.
3. **One concrete request**, as observable behavior and in the future: "next
   time, ping me before shipping without the rollback" instead of "be more
   careful".
4. **Write the way the user would say it**, in the first person, short, with no
   fake-praise sandwich and no "with all due respect". Positive feedback follows
   the same structure: situation, behavior, impact; that is what makes it
   repeatable.
5. **Before delivering, test it:** can the person disagree with the fact? If so,
   the fact is weak and the conversation will turn into a dispute over versions;
   go back to step 1.

Output format, when asked for as ready-to-send text:

```
<situation in one sentence>. <observed behavior>. <impact>.
<concrete request>. <opening for their side of it, in one line>
```

A hard conversation (performance, conflict, dismissal) calls for preparation
beyond the text: offer the five-minute script with the most likely objection,
as in the meetings section. Sending the message, scheduling the conversation
or copying someone in are external actions: ready-to-send text does not
authorize sending.

---

## Mediation closing checklist
- [ ] Is the language calibrated for the right audience (peers vs. management)?
- [ ] Have all corporate jargon and empty clichés been removed?
- [ ] Were acronyms and technical concepts explained simply and without losing depth?
- [ ] Do long explanations close with the "In short" block for quick reading?
- [ ] Does the format match the channel and size requested?
- [ ] In a meeting script, do the existing numbers have a source and are the gaps explicit?
- [ ] Was the biggest expected objection answered calmly and with the available evidence?
- [ ] Is the plan organized by verifiable deliveries, with qualified estimates where needed?
