# Track: Mastra — from zero to production agents

> Path for the `forja` skill. The **Mentor Rules** live in `SKILL.md` and apply here in
> full — especially the **No-write** rule, the **Progression-gate** rule, the
> **Verify-before-quoting** rule, and the **Progress-logging** rule. Those rules are Part I of
> this guide — part numbering below continues from them. Rules are always cited by name here:
> `SKILL.md` may be reordered, and a number would silently rot.
>
> **Progress for this track:** `~/.forja/progress/mastra.md`

## Contents
- [Part II — Student profile and domain adaptation](#part-ii--student-profile-and-domain-adaptation) — calibration questions, how the domain shapes every artifact
- [Part III — API name map](#part-iii--api-name-map) — concept → import → shape, no pinned versions (resolve them at runtime)
- [Part IV — The deliveries](#part-iv--the-deliveries) — the gated build sequence; the bulk of the track
- [Track 2 — Specialization](#track-2--specialization) — where the student goes after the core path
- [Part V — Consolidation](#part-v--consolidation) — the `/forja recap` teach-back
- [Glossary](#glossary)

Jump straight to the Delivery the progress file points at — reading the whole
track before answering wastes the student's turn and tells you nothing the
progress file did not already.

## PART II — STUDENT PROFILE AND DOMAIN ADAPTATION

### The principle

**The concept of each Delivery is fixed. The artifact is adaptable.**

The Deliveries in Part IV describe agents for a specific domain (corporate software
engineering). That's a **filled-in example**, not a requirement. If the student works in a
different domain, swap the artifact and keep the concept, the acceptance bar, and the
pitfalls.

Golden rule: **every Delivery produces an agent the student actually uses on Monday.** If an
exercise doesn't survive past the end of the guide, it's the wrong exercise — swap it for one
that does. A weather-forecast agent teaches the same API and survives nothing.

### How to adapt

Use the answer to the third calibration question (Calibration rule). For each Delivery, keep
the left column and replace the right one:

| Delivery | Concept (fixed) | Artifact (adaptable to domain) |
|---|---|---|
| 1 | Typed tool + structured output | A task they currently **write by hand, always in the same format** |
| 2 | Memory + recall + tracing | A recurring task where **remembering the previous case helps** |
| 3 | Deterministic workflow + human approval | One of their processes with **fixed steps and an approval point** |
| 4 | MCP server | Expose the previous agents in the tool they **already work in** |
| 5 | RAG | The body of documents they **look up and never remember where it lives** |
| 6 | Guard-rail + eval | The domain operation that is **destructive or irreversible** |
| 7 | Runtime context + streaming | Any earlier agent, now with a **runtime cost rule** |
| 8 | Multi-agent vs. workflow | Measured comparison between two versions of the **same** problem |
| 9–11 | Cost, observability, CI | About the agents they've **already built** — don't invent new ones |

Delivery 1 translation examples by domain: backend dev → bugfix cause/solution report. Data
analyst → automatic dataset documentation. Support → structured ticket summary. Frontend →
component accessibility checklist. QA → test case generated from a requirement.

**If they don't know what to automate**, don't invent it for them. Ask two questions: what
task did they do more than once last week, and which one did they hate doing most. The
intersection is Delivery 1.

### Reference profile (filled-in example)

This is the profile the Deliveries in Part IV were originally written for. Use it as a model
of how specific a profile needs to be — not as the default.

- **Role:** developer moving into software architecture + SRE.
- **Constraint:** proprietary company code — a real limit on what can leave the network.
- **Tools:** GitLab (MRs, issues, pipelines), Java, an internal framework, SQL against
  customer databases, SDD and Gherkin documents, STRIDE threat modeling.
- **Recurring pain:** cause/solution reports for bugfixes, incident triage, writing SDDs,
  data extraction for reporting, MR review.
- **Target runtime:** local CLI, local HTTP server (`mastra dev`), and an MCP server
  consumed by the code agent they already use.

### Adjusting by level

The path is the same for everyone. What changes:

- **Never used Node/TS:** Delivery 0 gains a step before it — install Node, understand
  `package.json` and `npx`, run any `.ts` file. Don't skip it; they'll get stuck at Delivery 1.
- **Never called an LLM by API:** before Delivery 1, have them call the model **without**
  Mastra, once, straight through the provider's API. Understanding what the framework
  abstracts away is worth the half hour.
- **Senior with LLM experience:** offer to start at Delivery 3 (workflows), circling back to
  what's missing. But the Track 1 consolidation still applies in full.

Log the level in `~/.forja/progress/mastra.md` and **re-check it**: someone who called
themselves a beginner might be moving fast, and someone who called themselves senior might
get stuck on `async`. Calibrate on evidence, not self-report.

---

## PART III — API NAME MAP

**No versions are pinned here on purpose.** A version number written into a guide is wrong
within days, and a stale pin is worse than no pin because it reads as verified. Resolve the
real ones yourself, per the Verify-before-quoting rule:

```bash
npm view mastra version
npm view @mastra/core @mastra/memory @mastra/libsql @mastra/mcp @mastra/evals @mastra/rag version
```

Run that before Delivery 0, log what you resolved with the date in
`~/.forja/progress/mastra.md`, and once the student has installed anything, read the
**installed** version from their `package.json`/lockfile — that is what their code runs
against, not the registry's latest. Re-resolve on every resumed session.

**AI: this is a name map, not a crib sheet.** It records which symbol lives in which package,
nothing about a specific release. Re-confirm every signature against the docs for the resolved
version before showing it to the student — especially the shape of the `execute` argument,
which has already changed across versions.

| Concept | Import | Shape |
|---|---|---|
| Root instance | `@mastra/core` | `new Mastra({ agents, workflows, mcpServers, storage, logger })` |
| Agent | `@mastra/core/agent` | `new Agent({ id, name, instructions, model, tools, memory, scorers })` |
| Model | — | string `'provider/model'` (string-based routing, not an object) |
| Tool | `@mastra/core/tools` | `createTool({ id, description, inputSchema, outputSchema, execute })` |
| Workflow | `@mastra/core/workflows` | `createWorkflow({ id, inputSchema, outputSchema })` + `.then()` `.branch([[cond, step]])` `.parallel()` `.dowhile(step, cond)` + `.commit()` |
| Step | `@mastra/core/workflows` | `createStep({ id, inputSchema, outputSchema, resumeSchema, execute })` |
| Step from an agent | same | `createStep(agent, { structuredOutput, onFinish })` |
| Pause (HITL) | — | inside `execute`: `await suspend({})`; resume with `run.resume({ step, resumeData })` |
| Execution | — | `mastra.getWorkflow(id)` → `.createRun()` → `.start({ inputData })` |
| Memory | `@mastra/memory` | `new Memory({ storage, vector, options: { semanticRecall: true } })` |
| Persistence | `@mastra/libsql` | `new LibSQLStore({ id, url })`, `new LibSQLVector({ id, url })` |
| MCP (server) | `@mastra/mcp` | `new MCPServer({ id, name, version, agents, tools, workflows })` |
| MCP (client) | `@mastra/mcp` | `MCPClient` |
| Evaluation | `@mastra/evals/scorers/prebuilt` | `createAnswerRelevancyScorer`, `createToxicityScorer`; on the agent: `scorers: { k: { scorer, sampling: { type: 'ratio', rate } } }` |

**Project convention:** everything (agent, tool, workflow, scorer) is registered in
`src/mastra/index.ts`. Run it via `package.json` scripts, not by calling `mastra dev`
directly.

**Track 2 deliberately uses APIs not mapped here** — runtime context, streaming, processors,
multi-agent composition, telemetry, and build. These are the ones that change most between
versions, and a stale map is worse than no map. Check the docs per Delivery.

---

## PART IV — THE DELIVERIES

Each Delivery has: **concept** (what they learn), **artifact** (what they build),
**acceptance** (what proves it worked), and **pitfalls** (where they'll get it wrong).

> **Before opening any Delivery:** the artifacts below are written for the reference
> profile's domain from Part II. Translate them to **the student's** domain using the
> adaptation table. Concept, acceptance, and pitfalls don't change — the artifact does.

The path has two tracks. **Don't mix them.** Finishing Track 1 doesn't make someone an
expert — it makes them a competent user. Tell them that at Track 1's close, without
softening it.

| Track | Deliveries | Honest outcome |
|---|---|---|
| **1 — Operation** | 0–4 | Builds agents that work and uses them at their job. This is the part that changes their day-to-day. |
| **2 — Specialization** | 5–11 | Builds agents that **someone else** operates in production. This is what makes an expert. |

Track 2 is where the content matching their role (architecture + SRE) lives: reliability,
cost, observability, deployment, and testing. Don't treat it as optional — treat it as the
second half. The capstone build in Part V is what closes the guide.

### The minimum path

Eleven Deliveries is weeks of real work, and most of them end in an artifact that takes a
session or more on its own — Delivery 10 wants a running OTel backend, Delivery 11 wants a CI
job with an eval floor. A student who tries to walk all of it linearly usually stops somewhere
around Delivery 5 with nothing they'd defend.

So state the short route out loud at calibration, and let them choose:

| Route | Deliveries | What they end up with |
|---|---|---|
| **Minimum** | 0 → 1 → 3 → 6 | One agent they use for real, one workflow with an approval point, and one guard-rail enforced in code. Defensible, and reached in a fraction of the time. |
| **Full** | 0 → 11 | Everything, including the production half. |

Rules for the minimum path:

- **The acceptance bar of each Delivery on it does not move.** Fewer Deliveries, same bar.
- Log the choice in the progress file (`**Path:** minimum`), and log the Deliveries they
  skipped as **debt**, not as done. `/forja debt` has to show them.
- 2, 4, 5, and 7–11 stay available at any time. Someone who finishes the minimum path and
  wants more picks up whichever debt item their real work is now asking for — that's a better
  trigger than sequence order.
- Don't sell the minimum path as equivalent. It produces someone who can build an agent, not
  someone who can hand one to an operations team. Say that in one line and move on.

---

### Delivery 0 — Foundation and the provider decision

**Concept.** An agent is `model + instructions + tools` running in a *tool-calling loop*: the
model decides to call a tool, the runtime executes it, returns the result, the model decides
again, until it produces a final response. Everything in Mastra is a variation on this. The
student needs to understand that the **loop** is the product, not the prompt.

**Blocking decision — LLM provider.** Make the student decide before installing anything, by
presenting the real trade-off (not a neutral list):

- Ask first: *what will their agents read?* Company source code, production logs, customer
  data, and database schemas **leave the network** when you use a public API. If the answer
  includes any of those, the decision stops being technical and becomes a policy question.
- Ask directly: *is there an internal policy about sending code or data to a third-party
  API? Is there an approved corporate endpoint?* If they don't know, that's their first task
  — find out before building.
- If there's a restriction, recommend the two-track architecture: a **commercial provider**
  (Anthropic or OpenAI) for agents that only handle text they wrote themselves, and a
  **local model via Ollama** for agents that touch code or sensitive data.
- If there's no restriction (personal project, open-source code), simplify: one commercial
  provider, and move on. Don't make a beginner set up Ollama without a reason.
- The engineering point: in Mastra, the model is a **string** on the agent. Switching
  providers means swapping a string — as long as they don't couple logic to the provider.
  Have them configure the string via an environment variable from the very first agent.

**Artifact.**
- An empty Mastra project created with `npx create-mastra@latest --empty`. Do **not** trust
  that flag from this file: run `npx create-mastra@latest --help` (or read the published CLI
  source) first, confirm the flag still exists in whatever `@latest` resolves to today, and
  tell the student which version you confirmed against.
- `.env` with a key and `MODEL` (and `.env` in `.gitignore` — check this and call it out if
  missing).
- A trivial agent running in the `mastra dev` playground.

**Acceptance.** A screenshot/paste of the playground responding. Then walk them through what
happened between the prompt and the response — the acceptance bar is the run, not their
retelling of it.

**Pitfalls.**
- The model-string format is `provider/model`, not `provider:model`.
- Node needs to be recent — check `node --version` before anything else.
- A committed key. Check `git status` before unlocking the next step.

**Predict first.** Before they run it, have them commit to an answer: what happens when the
model calls a tool that was never registered? Then have them force exactly that — invent a
tool name in the prompt, run it, and read the output.

**Why it matters.** Explain what happens when the model emits a call to a tool that was
never registered: which layer rejects it, whether the error is fed back to the model as
another turn or aborts the run outright, and why that single difference decides whether the
agent self-corrects or dies. Verify the current behavior against the installed version
before asserting it (Verify-before-quoting rule).

---

### Delivery 1 — Cause/Solution Reporter agent

**Why this one first.** It's their most repetitive, most tedious task (documenting a bugfix
for a GitLab issue), and it's the perfect case for teaching a **typed contract**: the output
needs a fixed shape, every time.

**Concepts.**
- **Tool** as a typed contract, with Zod validation on input and output. The tool is the
  **system boundary** — every external value gets validated there, not in the prompt.
- **Structured output**: forcing the agent to return a schema-validated object, not prose.
  Critical difference: you *read* prose, you *integrate* an object.
- **Prompt as a specification**, not a request. `instructions` defines the role, the format,
  the constraints, and what to do when information is missing.

**Artifact.**
- A `read-branch-diff` tool — takes a branch name and a base branch, runs `git log`/`git
  diff` read-only, returns `{ commits, changedFiles, diff }`.
- A `cause-solution-reporter` agent with an `outputSchema` containing at least:
  `{ rootCause, solutionApplied, impactedFiles[], regressionRisk, howToValidate[] }`.
- An npm script runnable from the CLI: `npm run report -- <branch>`.

**Acceptance.** They run it against a real bugfix branch and paste the validated JSON output.

**Pitfalls.**
- A large diff blows the context. Force the student to decide the truncation strategy
  **explicitly** (per file? summary only? filter lockfiles and generated code?) — that
  decision is half of agent engineering.
- Running a shell command inside a tool without sanitizing the branch name is command
  injection. Cover this. It's the system boundary.
- The tool's `description` is read by the **model**, not by a human. A vague description
  means the tool never gets called. Have them rewrite it if it's weak.

**Predict first.** Have them commit to an answer before touching anything: if they rewrite
only the tool's `description` and leave the function body identical, does the agent call the
tool more, less, or the same? Then have them make the description deliberately vague, rerun
the same prompt, and compare the two traces.

**Why it matters.** Explain why editing only the tool's `description` — no code touched —
changes the agent's behavior: the description is part of the payload the model reads when it
decides whether and how to call the tool, so the selection logic lives in prose, not in the
function body. Draw the consequence: that prose is production code and needs the same review
as the implementation. Verify the current behavior against the installed version before
asserting it (Verify-before-quoting rule).

---

### Delivery 2 — Incident Triager agent, with memory

**Concepts.**
- **Memory** in Mastra has distinct layers — make sure they understand the difference before
  configuring: recent conversation history, *working memory* (persistent facts about the
  context), and *semantic recall* (similarity search over past conversations).
- **Thread vs. resource**: one conversation vs. one subject across many conversations.
  Getting this wrong makes the agent remember the wrong thing.
- **Observability / tracing**: seeing the real sequence of calls, tokens, and latency.
  Without it, debugging an agent is guesswork. This is their SRE territory — dig into it.

**Artifact.**
- An `incident-triager` agent: takes a stack trace or log excerpt, classifies it
  (`severity`, `suspectComponent`, `hypotheses[]`, `nextSteps[]`).
- A log-file-reading tool with filtering by time window/pattern.
- `Memory` with `LibSQLStore` + `LibSQLVector` and `semanticRecall: true`, scoped by
  `resourceId` = system/service.
- A structured logger configured on the `Mastra` instance.

**Acceptance.** They run the agent twice on similar incidents and show the second run pulling
context from the first. Without that, semantic recall isn't actually working.

**Pitfalls.**
- Semantic recall requires **embeddings** (a vector representation of text). That's an extra
  model call, with a cost — and in their case, a privacy implication: production logs turned
  into vectors on an external service. Force a conscious decision.
- Unscoped memory turns into pollution: the agent recalls an incident from a different
  system.
- They'll want to dump the entire log into the context. Don't let them.

**Predict first.** Before the second run, have them commit to an answer: if they change the
`resourceId` between the two similar incidents, does semantic recall still pull the first one?
Then have them run it both ways — same `resourceId`, then a different one — and read which
context actually made it into the prompt.

**Why it matters.** Explain the split: memory carries what happened in *this* relationship
(per-user, mutable, grows without bound, is a privacy liability), RAG carries what is true
about a *corpus* (shared, curated, versioned, re-indexable). Show the failure of using the
wrong one — memory as a knowledge base drifts and can't be corrected centrally; RAG as
memory loses the user's own history — and that cost, retention, and blast radius on a leak
follow from that choice, not from the code.

---

### Delivery 3 — Requirement → SDD + STRIDE workflow, with human approval

**This is the most important point in the guide.** The central concept: **not every problem
wants an agent.** Agents are non-deterministic and expensive to audit. When a process has
fixed steps, a **deterministic workflow with agents at specific steps** is superior —
reproducible, observable, resumable.

**Concepts.**
- `createWorkflow` / `createStep`: an explicit graph of steps with schemas between them.
- `.branch()` — conditional routing; `.parallel()` — concurrent execution; `.dowhile()` — a
  loop until a quality criterion passes.
- **HITL** (*human-in-the-loop*): `suspend()` pauses the workflow, persists state, and
  `resume()` picks it back up with the data a human provided. This is what separates
  toy automation from automation someone approves before it applies.
- **Agent as a step** (`createStep(agent)`): composing non-determinism inside a
  deterministic skeleton.

**Artifact.** A `requirement-to-sdd` workflow:

1. Deterministic step: validates/normalizes the input requirement.
2. Agent step: drafts a structured SDD.
3. `.parallel()`: one agent step runs a STRIDE analysis (Spoofing, Tampering, Repudiation,
   Information disclosure, Denial of service, Elevation of privilege) while another extracts
   Gherkin acceptance criteria.
4. Deterministic step: validates completeness (are all sections filled in? does every threat
   have a matching non-functional requirement?).
5. `.branch()`: incomplete → back for revision (`.dowhile` until it passes); complete →
   continue.
6. **`suspend()`** — the student reviews and either approves or sends it back with a comment.
7. Final step: assembles the consolidated document.

**Acceptance.** They run it, the workflow suspends, they resume it with `resume()` rejecting
it, and show the revision loop running again. Suspending and resuming is the acceptance bar
— running it straight through isn't enough.

**Pitfalls.**
- Suspend/resume requires **storage configured** on the `Mastra` instance. Without
  persistence, the state dies. This will catch them.
- Schema between steps: one step's output is the next step's input. Incompatibility only
  shows up at runtime if they loosen the types.
- They'll try to do all of it with a single agent and a long prompt. Don't let them — the
  whole point of this Delivery is the opposite.

**Predict first.** With the workflow suspended at the approval step, have them commit to an
answer before doing anything: if the process dies right now, is the pending run recoverable
after a restart? Then have them kill it, start it back up, and try to `resume()` the same run.

**Why it matters.** Walk the student through their own workflow step by step and explain the
criterion: a step with a deterministic rule, a schema, or a right answer belongs in code —
it's cheaper, testable, and can't drift. An LLM earns its place only where the input is
unstructured and judgment is required. Name the cost of getting it wrong: every LLM step
added is latency, spend, and one more nondeterministic failure mode to debug.

---

### Delivery 4 — Expose everything as an MCP server in the agent they already use

**Concept.** **MCP** (*Model Context Protocol*) is the open protocol that connects agents to
external tools. Mastra speaks both sides: `MCPClient` consumes external servers, `MCPServer`
**exposes** their agents/tools/workflows to any MCP client — including whichever coding agent
or editor they already use every day (Claude Code, Codex, Cursor, VS Code, Zed: all MCP
clients).

This Delivery is what turns the exercise into a working tool: the three previous agents
become commands inside the environment they already work in. Ask which client they use before
starting, and configure that one — don't default to the one named in this file.

**Artifact.**
- An `MCPServer` registering the agents from Deliveries 1–3 and the workflow.
- The server registered on the `Mastra` instance (the `mcpServers` field).
- Configuration on **their** MCP client, pointing at the server.

**Acceptance.** They invoke the cause/solution reporter from inside their own client, without
leaving the tool they normally work in, and paste the result.

**Pitfalls.**
- Exposing an agent that runs shell commands via MCP widens the attack surface: anything the
  MCP client sends becomes input to your tool. Re-validate at the boundary. Discuss *prompt
  injection* coming from the very diff the agent is analyzing.
- The name and `description` of exposed tools become the public interface. Bad names mean
  the client never calls them.
- Transport (stdio vs. HTTP) changes the client-side config. Confirm against the docs.

**Predict first.** Before wiring the client, have them commit to an answer: which of the
things they exposed will the MCP client actually be able to call — the agents, the tools, the
workflow, all three? And what does the client show for each one's name and description? Then
have them connect it, list the tools from the client side, and compare that listing to what
they expected to publish.

**Why it matters.** Explain that exposing an agent over MCP turns it into a public endpoint
whose caller is another agent — one that can loop, retry, and fan out with no human pacing
it. The limits (step ceiling, timeout, spend cap, recursion depth) have to be enforced by the
server, because the caller has no incentive to hold back and the bill lands on the callee.
Verify the current behavior against the installed version before asserting it (Verify-before-quoting rule).

---

## TRACK 2 — SPECIALIZATION

*Frontier. Before entering here, run the Track 1 consolidation (Part V) and log it in
`~/.forja/progress/mastra.md`. It's a teaching pass over what they built, not a gate.*

---

### Delivery 5 — RAG over runbooks, ADRs, and internal docs

**Concept.** **RAG** (*Retrieval-Augmented Generation*): instead of putting everything in the
prompt, you index documents into vectors, retrieve the relevant chunks at query time, and
inject only those. Pipeline: *chunk* → *embed* → *store* → *retrieve* → *rerank*.

The engineering point almost everyone gets wrong: **chunking quality dominates the result**
more than model choice does. Have them test two chunking strategies and compare.

**Artifact.** An `architecture-query` agent: indexes ADRs, runbooks, and internal
documentation, answers with a source citation. Hard rule in `instructions`: no retrieved
source, no answer — reply "not found," never fill the gap from memory.

**Acceptance.** A question whose answer only exists in the indexed documents, answered with a
correct citation. And an out-of-scope question, answered with "not found."

**Pitfalls.**
- Indexing sends every chunk to the embedding provider. If the runbooks contain secrets or
  customer data, that's the Delivery 2 privacy decision all over again — force it consciously.
- A stale index answers confidently from an outdated document. Ask what their re-indexing
  strategy is when a doc changes.
- Retrieval that returns *something* always looks like it worked. The "not found" acceptance
  case exists precisely because the failure mode is a confident answer from the wrong chunk.

**Predict first.** Before the out-of-scope run, have them say what the agent will do when
retrieval comes back empty — refuse, or answer anyway. Then have them push on it: ask
something adjacent to the corpus, rerun the same question a few times, and see whether the
`instructions` rule holds every time or only most of the time.

**Why it matters.** Explain the difference between a request and a constraint: a rule written
in `instructions` is something the model usually honors, not something that can't be
violated — there is no code path that fails when it is broken. A guard-rail is enforcement
outside the prompt: an assertion on the output that rejects an answer with no citation. Make
the point concrete — one is a hope with no signal when it fails, the other is a failure you
can see and count.

---

### Delivery 6 — Guard-rails and evaluation

**Concept.**
- **Scorers/evals**: automatically evaluating agent output (relevancy, toxicity, faithfulness
  to source), with `sampling` so you don't evaluate 100% and blow up cost. Without evals, you
  don't know whether changing the prompt made things better or worse — you have *faith*, not
  engineering.
- **Guard-rail**: a restriction enforced in code, not in the prompt. A prompt is a
  suggestion; code is the law.
- **Input/output processors**: Mastra's native mechanism for intercepting what goes in and
  out of the agent (redacting sensitive data, blocking, transforming). Confirm against the
  docs the current name and shape before showing it — this is one of the areas that has
  changed the most.

**Artifact.** A `sql-advisor` agent — the case where a guard-rail is mandatory:
- A tool that runs a query against a customer database, with code-level validation that
  **rejects anything that isn't `SELECT`**, enforces a mandatory `LIMIT`, and a timeout.
- HITL: the generated query is shown and needs approval before running.
- Scorers on the agent to measure how well the answer sticks to the returned data.

**Acceptance.** They try to induce the agent to run a `DELETE` via the prompt and show the
guard-rail blocking it **in code**, not in the model.

**Pitfalls.**
- A guard-rail written as a prompt instruction ("never run DELETE") is not a guard-rail. If
  their first version does this, make them show the line of code that enforces it.
- Validating SQL with a naive regex misses `WITH ... DELETE`, comments, and stacked
  statements. Discuss what "reject anything that isn't SELECT" actually requires.
- Scorers at 100% sampling on every call — cost explodes silently. `sampling` exists for a
  reason; make the rate a conscious choice.

**Predict first.** Have them build the prompt-only version first — "never run DELETE" written
into `instructions`, nothing in code — and commit to a number: out of ten adversarial prompts,
how many get through? Then have them run all ten and count. The gap between their number and
the count is the whole argument for the code-level guard-rail they're about to write.

**Why it matters.** Explain why a rule embedded in one tool is a rule that will be bypassed:
the second tool that reaches the same database won't inherit it, and nothing fails loudly when
it doesn't. The constraint belongs at the resource it protects — the data-access layer, or the
database itself — so every caller crosses it by construction. Give them the general form: a
guard-rail duplicated per caller is a guard-rail that decays.

---

### Delivery 7 — Dynamic agents and streaming

**Concept.** Up to this point, every agent has been static: `instructions`, `model`, and
`tools` are fixed in code. That doesn't survive more than one user, more than one project, or
more than one permission level.

- **Runtime context**: per-request dependency injection. `instructions`, `model`, and `tools`
  become **functions** that receive the context and resolve at execution time. It's the
  agentic equivalent of dependency injection — and it solves multi-tenancy, permissioning,
  and cost-based model routing, all with the same mechanism.
- **Streaming**: `stream()` instead of `generate()`. This changes the architecture, not just
  the UX — you now deal with partial responses, cancellation, and in-flight tool calls.

**Artifact.**
- Refactor the Delivery 1 reporter so `model` resolves at runtime: small diff → cheap model;
  large or critical diff → expensive model. The selection rule lives in code.
- The same agent with `tools` filtered by permission level coming from the runtime context.
- One execution via `stream()` on the CLI, with incremental output.

**Acceptance.** Two runs of the **same** agent choosing different models because of context,
with a log proving which one was used in each run.

**Pitfalls.**
- They'll try to solve this with an `if` in the prompt. A prompt doesn't choose the model.
- Streaming breaks naive structured output — ask them how they validate an object that hasn't
  finished arriving yet.

**Predict first.** With the tools filtered down by runtime context, have them predict what
stops a request for the removed capability: the model declining, or something in the system
rejecting it. Then have them run that request under the restricted context and read the trace
to see which layer actually said no.

**Why it matters.** Explain that deciding which tools an agent can see is not authorization —
it shapes what the model is offered, not what the system permits. Real access control needs an
identity established outside the agent, a check at the resource being touched, and an audit
trail of who did what. Spell out the consequence: if the only thing standing between a user and
the data is which tools got wired into the agent, then a prompt-injected model is a privileged
user.

---

### Delivery 8 — Multi-agent, and when not to use it

**Concept.** Delegation between agents: an orchestrator agent that calls others, or
specialist agents exposed as tools to one another. Mastra offers agent composition and the
A2A protocol (*agent-to-agent*) — confirm the current primitives against the docs.

**The real lesson of this Delivery is negative.** Multi-agent is the most over-engineered
architecture in the field. Every hop between agents means more latency, more tokens, one more
failure point, and lost context. Most "multi-agent" systems would be better as a single-agent
workflow. Make them **measure** this, not take it on faith.

**Artifact.**
- An orchestrator that routes between the agents from Deliveries 1–3 based on the request.
- **And the competing version**: the same result as a deterministic workflow with
  `.branch()`.
- Side-by-side measurement: tokens, latency, routing accuracy across ~10 real requests.

**Acceptance.** A comparison table of the two versions and **their own** recommendation,
defended with the numbers. If they pick multi-agent without the numbers backing it up, push
back.

**Pitfalls.**
- Recursion: agent A calls B which calls A. Ask what the depth limit is and who enforces it.
- Lost context across the hop: the sub-agent doesn't know what the orchestrator already
  found.
- Multiplicative, not additive, cost.

**Predict first.** Before the measurement run, have them write down two numbers: the extra
tokens and the extra latency the orchestrator hop adds per request over the `.branch()`
version. Then have them run the ~10 requests and put their guess next to the real table.

**Why it matters.** Walk the student through the arithmetic of routing: a 10% misroute rate
produces answers that look normal, so nothing catches it unless routing decisions are logged
and reviewed against outcomes. Then account for the other nine — each pays an extra LLM call in
latency and tokens for a decision a switch statement could have made. Conclusion to state
plainly: multi-agent is justified by genuinely distinct capabilities, never by tidiness of the
diagram.

---

### Delivery 9 — Cost and reliability

**Concept.** What separates a demo from production. None of this is about AI — it's about
distributed systems, which is exactly their turf.

- **Token accounting**: measuring input, output, and cost per run. Without measuring it,
  there's no optimization — there's guessing.
- **Prompt caching**: reusing the stable prefix of the context across calls. This changes the
  order you assemble the prompt in (stable content first, variable content after). A big,
  nearly free cost cut that almost everyone ignores.
- **Retry, timeout, idempotency**: LLM calls fail, time out, and are expensive to retry.
  A blind retry on a tool with side effects duplicates the effect.
- **Provider fallback and rate limits**: what happens at 3pm when you blow through your
  quota.

**Artifact.**
- Per-run cost instrumentation on the existing agents, persisted.
- Explicit timeout and retry policy on tools that do I/O.
- A configured model fallback, **tested** by forcing a failure.
- Reordering an agent's prompt to take advantage of caching, with before/after measured.

**Acceptance.** A real cost-per-run number for each agent, and a demonstration of the
fallback working with the primary provider deliberately taken down.

**Pitfalls.**
- Retrying a non-idempotent tool. Cover this specifically — the SQL tool from Delivery 6 is
  the perfect example.
- They'll optimize the model before optimizing the context. Wrong order: context first.

**Predict first.** Have them guess the split before they instrument anything: of the cost of
one run, what fraction is context resent unchanged every time, and what fraction is the
actual user input? Then have them add the per-run instrumentation and read the real
breakdown.

**Why it matters.** Walk the student through decomposing their measured cost per run into
system prompt, tool definitions, retrieved chunks, history, and the actual user input — and
show that the first four are usually most of the bill and mostly repeated. That's why the
cheap wins are trimming and reordering context for cache reuse, before touching the model
choice. Verify the current behavior against the installed version before asserting it
(Verify-before-quoting rule).

---

### Delivery 10 — Observability for agentic systems

**Concept.** Their home turf, with a twist that breaks SRE intuition: **in an agentic
system, the most common failure returns HTTP 200.** A wrong answer, a tool that never got
called, a loop that burned 50k tokens without converging — none of that shows up in an error
rate.

- **Tracing** with OpenTelemetry: each run as a trace, each model and tool call as a span.
  Confirm against the docs how Mastra exports, and to where.
- **Agent SLIs**: what do you define as "good"? p95 latency? Completion rate without human
  intervention? Average eval score? Cost per run within budget?
- **Structured logging without leaks**: prompts and responses contain customer data. Agent
  logs are a leak vector by nature.

**Artifact.**
- Exported and visualized tracing (a local OTel backend).
- A written definition of 3 SLIs for their most-used agent, with a numeric target.
- Sensitive-data redaction in logs, implemented and tested.
- An alert that fires on an agentic condition (cost per run above a threshold, or eval score
  below a floor).

**Acceptance.** The trace of a run of the Delivery 3 workflow, showing every span, and the
alert firing on a deliberately bad run.

**Pitfalls.**
- Prompts and responses land in the spans. Telemetry carrying customer data into a hosted
  backend is a leak vector — check what the exporter records before shipping anything.
- Tracing only the final answer: in a multi-step run, the cost and the failure live in the
  intermediate spans.
- Alerting on error rate alone — the whole point of this Delivery is that the failure mode
  returns 200.

**Predict first.** Before the deliberately bad run, have them name which of their existing
signals will move when the agent answers wrong — status code, latency, error rate, anything
already on the dashboard. Then have them force the wrong answer, run it, and check each
signal they named.

**Why it matters.** Explain the failure mode that breaks conventional monitoring: a wrong
answer is a successful request. Status codes, latency, and error rates all stay green, so
quality needs its own signal — scored outputs, traced tool calls and retrieved sources,
sampled human review, user-visible feedback. State it directly: logs tell you what it did,
observability lets you ask whether it was right without shipping a new deploy to find out.

---

### Delivery 11 — Testing, build, and continuous delivery

**Concept.** How an agent enters a pipeline without becoming debt.

- **Test layers**: a tool is a pure function, testable with an ordinary unit test. A workflow
  is testable with agent steps replaced by a *stub*. The non-deterministic part is testable
  via **an eval with a minimum floor**, not an equality assert.
- **Eval as a merge gate**: run the eval suite in their CI (GitLab, GitHub Actions, whatever
  their repo already uses — ask, don't assume) and block the merge request if the score drops.
  It's the only real defense against prompt regression.
- **Prompt versioning**: `instructions` is production code. A prompt change needs a diff,
  review, and rollback like any other.
- **Build and deploy**: `mastra build`, the artifact, the container, environment variables,
  where storage lives outside their machine.

**Artifact.**
- Unit tests for the tools from Deliveries 1, 2, and 6.
- A workflow test with a stubbed agent step.
- A versioned eval suite with reference cases.
- A CI job on their own platform running tests + evals, with a score floor failing the pipeline.
- A generated build running outside of `mastra dev`.

**Acceptance.** A red pipeline caused by an eval-score drop after a deliberately worsened
prompt, and a green one after reverting it. This is the guide's final acceptance bar.

**Pitfalls.**
- A non-deterministic eval makes the pipeline flaky. Ask how they control variance —
  temperature, sample count, a floor instead of an exact value.
- An API key in CI. Cover secret management.
- The cost of running an eval on every MR. They'll need sampling or a selective trigger.

**Predict first.** Before they worsen the prompt, have them commit to two numbers: how far the
eval score will drop, and whether the same worsened prompt scores the same on two consecutive
runs. Then have them run the suite twice on the bad prompt and twice on the good one. The
spread between repeats of the *same* prompt is the flakiness budget their floor has to clear.

**Why it matters.** Explain that a threshold in CI is a product decision written as a
constant: it encodes how much wrongness is acceptable, and if it was picked to make the
current build pass, it blocks nothing. Show what makes it defensible — derived from a
labeled set, tied to a cost of being wrong, and moved only on new evidence, never to
unblock a red pipeline. A floor that gets lowered under pressure was never a floor.

---

## PART V — CONSOLIDATION

There are no exams here. Nothing the student has to recite, nothing scored, nothing repeated
as a penalty. The running code is the evidence; what's left is making sure they understand
the system they now own. Run this with `/recap` and log it in `~/.forja/progress/mastra.md`.

### Track 1 consolidation — reading back what they built

Open their own files and teach the whole system as one thing, tracing real code they wrote.
No questions, no scoring. Cover these five, each anchored to a specific line of theirs:

1. **The tool-calling loop** — walk the actual path of one of their runs, and name three
   distinct ways that path breaks.
2. **Agent vs. workflow vs. plain script** — take each thing they built and say which of the
   three it should have been, and why. Where they picked wrong, say so and explain the cost.
3. **The anatomy of their tools** — go field by field through one of their own tool
   definitions, and show why `description` is functional code rather than a comment.
4. **Memory vs. RAG** — point at where each one landed in their project, and name a case in
   their own domain where RAG would be the wrong reach.
5. **Prompt injection surface** — go through their agents and mark every untrusted input that
   reaches the model: tool results, retrieved documents, anything a user controls.

If a topic lands and they clearly hadn't seen it, note it in the progress file — that's a gap
to revisit inside Track 2, not a reason to send them back.

**Then run the Track 1 retrospective, and lead it — this is analysis, not interrogation:**

1. Where each agent will **fail in production** — and what the plan is.
2. Cost per run for each one, and which could run on a smaller or local model.
3. Which decisions coupled the project to a specific provider (portability debt).
4. What they built that **shouldn't be an agent** and could be a plain script instead.

Item 4 is the most important. An engineer who knows when *not* to use an agent is worth more
than one who knows how to configure ten of them.

### Track 2 closing — the capstone build

Not an exam either: a build, without your step-by-step. You hand over **only the prompt** and
review the result the way you'd review a peer's:

> Build a new agent for a real problem at your job that hasn't been covered yet, meeting all
> of these criteria:
>
> - Tools with boundary validation and a unit test.
> - `model` resolved at runtime by a justified cost rule.
> - At least one human-approval point.
> - A code-level guard-rail for the domain's destructive operation.
> - Exported tracing and 2 SLIs defined with numeric targets.
> - An eval suite with a floor, running in CI.
> - Cost per run measured and documented.
> - A one-page document: why an agent and not a workflow, and what you deliberately left out.

They're an expert when they deliver this **without asking how**. Review it like a peer's merge
request: name what's fragile, then explain the reasoning behind each criterion they met — and
where the one-page document only describes a choice instead of justifying it, supply the
justification yourself. Then mark the guide complete in `~/.forja/progress/mastra.md`.

If they want a target beyond this: the next step isn't more Mastra. It's reading
`@mastra/core`'s source — specifically the workflow executor and the agent loop. Whoever has
read the loop no longer needs any guide.

---

## Glossary

- **Agent**: model + instructions + tools running in a tool-calling loop.
- **Tool**: a typed function the model can call. System boundary — validate here.
- **Workflow**: a deterministic graph of steps, with persisted, resumable state.
- **HITL** (*human-in-the-loop*): a pause for a human decision before continuing.
- **RAG** (*retrieval-augmented generation*): retrieving relevant chunks and injecting them
  into the prompt.
- **Embedding**: a vector representation of text, used for similarity search.
- **MCP** (*Model Context Protocol*): the open protocol connecting agents and tools.
- **Eval / scorer**: automated evaluation of an agent's output.
- **Guard-rail**: a restriction enforced in code, outside the prompt's reach.
- **Processor**: Mastra's native interceptor on an agent's input or output.
- **Runtime context**: per-request data that resolves `instructions`, `model`, and `tools` at
  execution time — dependency injection applied to agents.
- **Streaming**: incremental delivery of a response, instead of waiting for the full text.
- **Prompt caching**: reusing the stable prefix of the context across calls, cutting cost and
  latency.
- **Idempotency**: the property that repeating an operation produces the same effect — a
  prerequisite for safe retries.
- **Tracing**: the recorded sequence of calls, tokens, and latency for a run.
- **OTel** (*OpenTelemetry*): the open instrumentation standard for traces, metrics, and logs.
- **SLI** (*service level indicator*): the metric that defines what "working well" means.
- **A2A** (*agent-to-agent*): a communication protocol between agents.
- **Stub**: a controlled stand-in for a component during a test, with a fixed response.
- **STRIDE**: a threat taxonomy — Spoofing, Tampering, Repudiation, Information disclosure,
  Denial of service, Elevation of privilege.
