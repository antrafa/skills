# Playbook: Technical Decision, Trade-offs & ADR

This playbook governs the interactions where the user needs to **decide**, not just understand. It turns findings into choices, critiques options before accepting them, weighs the cost of reversibility and delivers formal, defensible records.

---

## The central rule
> *An architectural decision without a recorded rationale is a decision that will be reopened.*

Record the rationale when the decision is structural, durable or hard to
reverse. An exploratory recommendation or a cheap choice can stay in the
conversation. Proportional formalization keeps every opinion from turning into
an ADR.

---

## The Tutor rule (learning mode in architecture)
The profile says what the user has mastered and what is still developing (the
*Level per topic* field in [onboarding.md](onboarding.md#profile-file-structure),
or the *Domains* and *Gaps* sections of an older profile). Use that to calibrate
the decision:
- Topic marked **developing** in the profile: treat the gap as **decision and
  trade-off**, not a conceptual lecture, unless the developer corrects you on
  the spot. Do not explain what the technology is; **explain the trade-off and
  the choice criterion in depth**, why one approach was passed over and what
  operational constraint it imposes. Here, teaching the rationale is part of
  the deliverable.
- Topic the profile marks as a **domain**: go straight to the point, no didactic preamble.
- No profile: assume seniority and go straight; open up the rationale if asked.

---

## The 8-phase cycle

### Phase 0: Is this a decision?
Not every request deserves the full cycle. Before starting, assess:
- **Is there a real choice?** If there is only one viable path, say so in one line, deliver the path and stop. A full cycle for a non-decision is theater.
- **Is it reversible and cheap?** A decision undone with one command or a smallest diff does not need an ADR. Recommend the best option and move on.
- **Is the question a one-off?** Questions about code behavior or an error are diagnosis, not decision.
- **Is the domain complicated or complex?** (Cynefin, Dave Snowden.) *Complicated*: there is a right answer and expertise finds it — the cycle below applies in full. *Complex*: cause and effect only line up in hindsight, and no amount of upfront analysis settles it (adoption of something new to the team, the behavior of a system under a load nobody has seen, an organizational change). There, what applies is a **safe-to-fail probe**: a spike with a set budget, a signal to watch and a way back — and the ADR records the probe and what it would teach, not a choice nobody can ground yet. *Chaotic* — production on fire — is not a decision at all: stabilize first, per [playbook-troubleshooting.md](playbook-troubleshooting.md).

*The size of the answer is always proportional to the size of the question. A
trade-off table over a complex problem is an elegant document about a guess.*

### Phase 1: Rewrite the problem as a choice
A finding is not a decision. *"The gateway is the bottleneck"* is a finding; *"take the gateway out of the path, scale horizontally, or accept the current latency"* is a decision.
State it explicitly:
> **Decision:** `<choice to make>` — **Who decides:** `<role>` — **Deadline:** `<when>` — **What is blocked until it is decided:** `<consequence>`

### Phase 2: Evidence: precedents and the precedence ladder
1. **Check the history first, starting with Mentat:** invoke the `mentat` skill and search for precedents by project and by topic — it is always the first source of memory. Only then open the `~/.alterego/` archive for the full dossier of the decisions Mentat points to. If something similar was already decided, cite the earlier decision as basis, precedent or review trigger.
2. **Evidence precedence ladder:**
   - *An artifact exists* (report, benchmark, diagram) → read it and cite source and date; check version, configuration, environment and load. Reuse whatever still represents the decision. A relevant change or unknown validity requires refreshing the affected evidence; the earlier report stays as history.
   - *Evidence missing or stale, skill available* → load the corresponding skill through the environment's mechanism (`cluster-analyzer`, `performance-architect`, etc., per `references/sources.md`).
   - *Skill unavailable* → do the smallest possible collection, recording source, time and reach. Separate measured observation from **hypothesis** or **assumption**, and point out the pending measurement.
   - *Never present a hypothesis as a measurement.*
3. **A vague requirement is not evidence — turn it into a scenario.** "It has to
   be fast", "it has to scale", "it has to be secure" cannot be measured, so they
   cannot be decided on. Write it as a quality attribute scenario (SEI), six
   fields in one sentence — *source, stimulus, artifact, environment, response,
   response measure*:
   > *"1,000 concurrent users (source) submit an order (stimulus) to the checkout
   > API (artifact) at the month's peak (environment); the request completes
   > (response) with p95 under 800 ms and no 5xx (measure)."*

   The last field is what later becomes the acceptance criterion and the
   reopening trigger. When the number does not exist, the scenario states the
   **pending measurement** — never an adjective standing in for it.

### Phase 3: Critique the preferred option first
If the user (or the team) already has an option on the table, test its assumptions before comparing it with the others:
- What does this option assume that has not been measured yet?
- In which scenario does it fail or become the wrong choice?
- What hidden cost does it carry? (operations, who gets woken up at 3 a.m., licensing, complexity).
- Does it attack the root cause or just the symptom?
*Agreement comes after testing the assumptions. Every criticism carries evidence, impact and either a well-grounded alternative or the investigation needed to choose one. If no weakness is demonstrated, record that.*

### Phase 4: Real constraints first, alternatives later
Do not start from the ideal scenario. The option that is perfect on paper is a disaster if nobody can operate it.
1. **Surface the constraints:**
   - *Who operates it:* does the team have the skills to keep this running?
   - *Who maintains it in 6 months:* the person who will support it is not in this conversation; optimize for readability and simplicity.
   - *What the legacy imposes:* the legacy pays the bills. JVM versions, legacy databases and proprietary frameworks are constraints to understand and work around, never defects to insult.
   - *Window and budget:* what the organization tolerates taking down.
2. **Compare real alternatives.** Include "do nothing" when it is a viable
option and spell out the cost of inaction. Do not invent a third alternative
just to fill the table.

| Option | What it solves | What it costs | When it is the right one | Main risk |
|---|---|---|---|---|
| **Do nothing** | Avoids churn and immediate cost | Documented cost of inaction | When the tolerable impact < the cost of change | Progressive degradation |
| Option A | ... | ... | ... | ... |
| Option B | ... | ... | ... | ... |

### Phase 5: Reversibility sets the rigor
Classify in the quadrant:

| | Reversible | Irreversible |
|---|---|---|
| **Cheap** | Decide now, no ADR | Decide now, with a short ADR |
| **Expensive** | Pilot or spike first | Requires measured evidence first |

*An irreversible, expensive decision made on an unverified hypothesis is unacceptable.*
Then issue **the recommendation in one sentence**, explicitly stating what it gave up.

### Phase 6: Formal outputs when needed
If the user asks for the record or the decision requires durable documentation,
use the canonical destination `~/.alterego/decisions/<YYYY-MM-DD>-<slug>/` and
consult `references/deliverables.md`. Produce only the artifacts the reader
needs:
1. **ADR (`adr.md`):** context, decision, discarded options with the detailed why, consequences and reopening triggers.
2. **One page for whoever authorizes (`decision.md`):** language for management — what needs to be authorized, why now, the cost of not deciding. Zero unnecessary jargon.
3. **Five-minute script (`script.md` and inline):** when there is a meeting,
   how to defend the choice: opening, up to two measured numbers, the main
   objection and a firm answer. With no numbers available, spell out the
   pending measurement.

**Make the trigger executable whenever it can be.** A `reopen-when` written as a
number — "p95 above 800 ms", "more than three services depending on this
library", "the domain layer imports something from `infra`" — can become a
**fitness function**: an automated check in the pipeline that fails when the
condition fires (Ford, Parsons & Kua, *Building Evolutionary Architectures*). A
trigger that runs on its own does not depend on anyone remembering to run
`adr review`. Record in the ADR where the check lives; the mechanics are in step
6 of [playbook-dev.md](playbook-dev.md).

If there is an execution plan, organize it by verifiable **Deliveries**.
Include a validation metric and rollback for changes that demand that rigor.
When a deadline is needed, give an estimate and its assumptions instead of
fictitious precision.

### Phase 7: Authorized record in the archive
Run this phase when the request includes recording the decision or when there
is already an applicable authorization to maintain the archive. Otherwise,
present the ready content and point to the proposed destination without
writing it outside the project.
1. **Record the memory through the `mentat` skill** — an entry of type `decision`, pointing to the archive folder without duplicating the content. This step is what makes the decision retrievable later; do not write to `~/.mentat/` by hand.
2. Consult `references/archive.md` for the schema and save the dossier in `~/.alterego/decisions/<YYYY-MM-DD>-<slug>/`.
3. Add the corresponding line at the top of `~/.alterego/INDEX.md`, which indexes the dossier — not the memory.

---

## `adr review`: did the triggers fire?

The `reopen-when` field is only worth anything if someone comes back to
read it. This mode comes back.

```
/alterego adr review              (every decision with status accepted)
/alterego adr review <project>    (only that project's)
```

1. **List the decisions** from `~/.alterego/INDEX.md` (bootstrap in
   [archive.md](archive.md)); for each one with status `accepted` or `proposed`,
   read the `reopen-when` in its `adr.md`.
2. **Confront each trigger with current evidence**, using the Phase 2
   precedence ladder: existing artifact, measuring skill, minimal collection.
   A trigger that depends on a number nobody has today stays as *no way to
   measure*, with the measurement that would settle it. A trigger already
   covered by a **fitness function** is read from the pipeline's last run — do
   not re-measure by hand what a green build already answers.
3. **Return the table** and stop:

   | Decision | Trigger | State | Next step |
   |---|---|---|---|
   | <slug> | <reopen-when> | fired / not fired / no way to measure | reopen with `adr <decision>` / nothing / measure X |

4. **Reopening is a new decision**, with the full cycle and the earlier one as
   precedent; the old `adr.md` becomes `superseded`, pointing to the new one.
   None of this happens without the user asking.

Done when every active decision has a state and the user knows which one to
reopen.

---

## Decision closing checklist
- [ ] Was a one-off question answered directly, without unnecessary bureaucracy?
- [ ] Was the domain classified before the cycle — did a complex problem get a safe-to-fail probe instead of a trade-off table?
- [ ] Does every non-functional requirement carry a response measure, or an explicitly pending measurement?
- [ ] Was the reopening trigger turned into a fitness function when it was expressible as a number?
- [ ] In the full cycle, is the decision stated in one sentence with a real deadline, when there is one, and what is blocked?
- [ ] For a durable decision, were precedents checked in Mentat (first) and in the archive, and does the evidence still represent the current context?
- [ ] Were the assumptions of the option the user brought tested before the recommendation?
- [ ] Does every criticism have evidence, impact and a well-grounded fix or pending investigation?
- [ ] Was "do nothing" assessed when it was a real alternative?
- [ ] Is data labeled as *measured*, *hypothesis* or *assumption*?
- [ ] When the decision's rigor depends on it, was the reversibility quadrant declared?
- [ ] Does the recommendation spell out what it gave up?
- [ ] Was the requested deliverable produced at the right level of formality?
