# Track: Vercel AI SDK — from a script to a shipped AI feature

> Path for the `forja` skill. The **Mentor Rules** live in `SKILL.md` and apply here in
> full — especially the **No-write** rule, the **Progression-gate** rule, the
> **Verify-before-quoting** rule, and the **Progress-logging** rule. Those rules are Part I of
> this guide — part numbering below continues from them. Rules are always cited by name here:
> `SKILL.md` may be reordered, and a number would silently rot.
>
> **Progress for this track:** `~/.forja/progress/vercel-ai-sdk.md`

## Contents
- [How this track differs from Mastra](#how-this-track-differs-from-mastra) — read first if the student picked between the two
- [Part II — Student profile and domain adaptation](#part-ii--student-profile-and-domain-adaptation) — calibration questions, how the domain shapes every artifact
- [Part III — API name map](#part-iii--api-name-map) — concept → import → shape, no pinned versions (resolve them at runtime)
- [Part IV — The deliveries](#part-iv--the-deliveries) — the gated build sequence; the bulk of the track
- [Track 2 — Specialization](#track-2--specialization) — where the student goes after the core path
- [Part V — Consolidation](#part-v--consolidation) — the `/forja recap` teach-back
- [Glossary](#glossary)

Jump straight to the Delivery the progress file points at — reading the whole
track before answering wastes the student's turn and tells you nothing the
progress file did not already.

## How this track differs from Mastra

Both tracks teach the same underlying loop (`model + tools`, executed step by step), but they
are not interchangeable, and the mentor should say so out loud the first time it's relevant:

- **Mastra** is an opinionated framework: it ships a project registry, a dev playground, a
  memory package, a RAG package, an eval/scorer package, and an MCP **server** (it can expose
  your agents to other tools).
- **The AI SDK is a toolkit, not a framework.** `ai` gives you `generateText`, `streamText`,
  `tool`, `stopWhen`, and a growing set of higher-level packages (`@ai-sdk/react`,
  `@ai-sdk/mcp`, `@ai-sdk/workflow`) — but there is no project generator, no built-in memory
  store, no built-in eval package, and no way to *expose* your own tools as an MCP server. You
  bring your own persistence, your own evals, and (if you need it) the raw
  `@modelcontextprotocol/sdk` for the server side.
- Its actual center of gravity is **the browser**: `@ai-sdk/react`'s `useChat` and the
  message-parts model exist so a model's output can stream into a UI incrementally, and so a
  tool call can render as an arbitrary React component instead of a wall of text
  ("generative UI"). Mastra has no equivalent — it stops at the agent.

Don't let the student walk away thinking "AI SDK = Mastra but for the frontend." The honest
framing is: Mastra centralizes orchestration; the AI SDK gives you the primitives and expects
you to own the rest. Track 2 exists specifically to make that cost visible.

---

## PART II — STUDENT PROFILE AND DOMAIN ADAPTATION

### The principle

**The concept of each Delivery is fixed. The artifact is adaptable.**

The Deliveries in Part IV describe a specific domain (a product engineer shipping an
AI-assisted feature inside an existing web app). That's a **filled-in example**, not a
requirement. Swap the artifact, keep the concept, the acceptance bar, and the pitfalls.

Golden rule, same as the Mastra track: **every Delivery produces something the student's real
users (or the student themself) actually touch on Monday.** If it doesn't survive past the end
of the guide, it's the wrong exercise.

### How to adapt

Use the answer to the third calibration question (Calibration rule). For each Delivery, keep
the left column and replace the right one:

| Delivery | Concept (fixed) | Artifact (adaptable to domain) |
|---|---|---|
| 1 | Typed tool + structured output | A task they currently **write by hand, always in the same format** |
| 2 | Streaming chat UI | A workflow that's currently a form-and-wait, turned into a **live conversation** |
| 3 | Generative UI + approval gate | A tool result that's currently **dumped as raw text** the user has to parse, plus one action that's **destructive or costly** |
| 4 | MCP client | An external tool or data source they **already query by hand** (a ticket system, a docs site, a filesystem) |
| 5 | RAG | The body of documents they **look up and never remember where it lives** |
| 6 | Guard-rail + middleware | The operation that is **destructive, costly, or must never leak data** |
| 7 | Durable workflow (`@ai-sdk/workflow`) | One of their processes with **fixed steps and a real approval point that must survive a restart** |
| 8 | Multi-agent vs. single loop | Measured comparison between two versions of the **same** problem |
| 9–11 | Cost, observability, CI | About the agents/features they've **already built** — don't invent new ones |

Delivery 1 translation examples by domain: frontend dev → accessibility checklist for a
component; support → structured ticket triage; data analyst → dataset documentation; backend
dev → bugfix cause/solution report from a diff. If they don't know what to automate, don't
invent it for them — ask what task they did more than once last week and which one they hated
most. The intersection is Delivery 1.

### Reference profile (filled-in example)

This is the profile the Deliveries in Part IV were originally written for.

- **Role:** full-stack/product engineer on a Next.js app with real users.
- **Constraint:** the feature ships inside the existing product — it isn't a standalone CLI or
  internal tool, it's a UI real customers open.
- **Tools:** Next.js (App Router, Route Handlers), React, TypeScript, a Postgres database,
  GitHub, a support-ticket queue.
- **Recurring pain:** support wants an AI-drafted reply suggestion inside the ticket view;
  users ask the same "how do I..." question repeatedly; onboarding docs are scattered.
- **Target runtime:** a Next.js Route Handler calling the model, a React client consuming it
  via `@ai-sdk/react`.

### Adjusting by level

- **Never used React/Next.js:** Delivery 0 gains a step before it — `npx create-next-app`, the
  App Router's file-based routing, what a Route Handler is versus a page. Don't skip it.
- **Never called an LLM by API:** before Delivery 1, have them call the model **without** the
  AI SDK, once, straight through the provider's raw HTTP API or SDK. Feeling the boilerplate
  the AI SDK removes is worth the half hour.
- **Comes from the Mastra track already:** they know the loop and the tool-as-boundary
  concept. Compress Delivery 0–1, spend the saved time on Delivery 2–3 (UI streaming and
  generative UI have no Mastra equivalent) and on the "toolkit vs. framework" gaps in Part V.
- **No frontend at all (backend/CLI-only stack):** Deliveries 2–3 as written assume a React
  client. Don't force one. AI SDK Core is framework-agnostic: Delivery 2 becomes streaming to
  the terminal via `result.textStream`, persistence stays identical, and the `UIMessage.parts`
  lesson is taught over the wire format instead of rendered components. Delivery 3's
  generative UI has no CLI equivalent — replace it with rich terminal output keyed on the
  tool-call part, and keep the `needsApproval` gate in full (it's transport-independent).
- **Uses Vue or Svelte, not React:** the same hooks exist in `@ai-sdk/vue` and
  `@ai-sdk/svelte` — confirm both are still published (`npm view @ai-sdk/vue version`) before
  you promise them. Teach the Deliveries in their framework; re-confirm hook names against the
  docs before showing them, since the React examples dominate the documentation.

Log the level in `~/.forja/progress/vercel-ai-sdk.md` and re-check it on evidence, not
self-report.

---

## PART III — API NAME MAP

**No versions are pinned here on purpose.** A version number written into a guide is wrong
within days, and a stale pin is worse than no pin because it reads as verified. Resolve the
real ones yourself, per the Verify-before-quoting rule:

```bash
npm view ai version
npm view @ai-sdk/react @ai-sdk/anthropic @ai-sdk/openai @ai-sdk/mcp @ai-sdk/gateway @ai-sdk/workflow zod version
```

Run that before Delivery 0, log what you resolved with the date in
`~/.forja/progress/vercel-ai-sdk.md`, and once the student has installed anything, read the
**installed** version from their `package.json`/lockfile — that is what their code runs
against, not the registry's latest. Re-resolve on every resumed session. The major matters
more here than anywhere else: see the rename list below.

**AI: this is a name map, not a crib sheet.** This SDK renames things aggressively between
majors (`parameters` → `inputSchema`, `maxSteps` → `stopWhen`, `system` → `instructions`,
`generateObject` → `generateText` with `output: Output.object(...)`). Re-confirm every
signature against the docs for the resolved version before showing it — a name from a cached
memory is very likely a name from the *previous* major, and the class-name suffixes below
(`MockLanguageModelV4`, `LanguageModelV4Middleware`) track the provider-spec version, so check
them rather than assuming the digit.

| Concept | Import | Shape |
|---|---|---|
| Generate (one-shot) | `ai` | `generateText({ model, instructions, prompt \| messages, tools, stopWhen, output })` |
| Stream | `ai` | `streamText({ ...same options, onFinish, onToolExecutionEnd })` — returns `.textStream`, `.toUIMessageStream()` |
| Model | — | Gateway string `'provider/model'` (via `ai`'s built-in `gateway`) **or** a provider factory call, e.g. `anthropic('claude-sonnet-4-6')` from `@ai-sdk/anthropic` — the two are not interchangeable in the same call |
| Tool | `ai` | `tool({ description, inputSchema: z.object({...}), execute, needsApproval? })` — `inputSchema`, not `parameters` |
| Stop condition | `ai` | `stopWhen: isStepCount(n) \| hasToolCall('toolName') \| [combined...]` — **default is a single step** if omitted, even with tools defined |
| Structured output | `ai` | `generateText({ output: Output.object({ schema }) })` — `generateObject` still exists but is deprecated as of the 6.0 migration guide; don't teach it as the default path |
| Agent (stateless loop) | `ai` | `new ToolLoopAgent({ model, instructions, tools, stopWhen })` → `.generate()` / `.stream()`; `stopWhen` defaults to `isStepCount(20)` here, unlike the bare functions |
| Durable agent/workflow | `@ai-sdk/workflow` | `new WorkflowAgent({ model, instructions, tools })` inside a function marked `'use workflow'`; tool `execute` marked `'use step'` gets automatic retry + persistence |
| Human approval | `ai` | `tool({ needsApproval: true \| async (input) => boolean })` — pauses the loop; with `WorkflowAgent` it suspends/resumes durably, with the bare loop it's request-scoped only |
| UI hook | `@ai-sdk/react` | `useChat({ transport: new DefaultChatTransport({ api }) })` → `{ messages, sendMessage }`; messages are `UIMessage[]` with a `.parts` array (`text`, `tool-<name>`, `reasoning`, ...) |
| UI wiring (server) | `ai` | `createUIMessageStreamResponse({ stream: toUIMessageStream({ stream: result.stream }) })` |
| MCP client | `@ai-sdk/mcp` | `createMCPClient({ transport })` → `.tools()` merges into a `tools` object; **no MCP server export exists in the AI SDK** |
| Embeddings | `ai` | `embed({ model, value })` / `embedMany({ model, values })` |
| Middleware / guard-rail | `ai` + `@ai-sdk/provider` | `wrapLanguageModel({ model, middleware })` — `wrapGenerate`/`wrapStream` intercept before/after the call |
| Telemetry | `ai` | `generateText({ telemetry: { functionId, metadata } })` (renamed from `experimental_telemetry` in 7.0; old name still accepted) |
| Testing | `ai/test` | `MockLanguageModelV4`, `simulateReadableStream({ chunks })`, `mockId`, `mockValues` |

**Project convention:** there is no equivalent of `src/mastra/index.ts`. A typical layout is
`app/api/chat/route.ts` (server) + a client component using `useChat`, with tools defined in a
shared module both sides can import types from.

**This track deliberately touches APIs not fully mapped here** — `@ai-sdk/workflow` in
particular is young and its primitives (`'use step'`, `'use workflow'`) may still be moving.
Check the docs per Delivery, especially in Track 2.

---

## PART IV — THE DELIVERIES

Each Delivery has: **concept** (what they learn), **artifact** (what they build),
**acceptance** (what proves it worked), and **pitfalls** (where they'll get it wrong).

> **Before opening any Delivery:** the artifacts below are written for the reference
> profile's domain from Part II. Translate them using the adaptation table. Concept,
> acceptance, and pitfalls don't change — the artifact does.

| Track | Deliveries | Honest outcome |
|---|---|---|
| **1 — Operation** | 0–4 | Ships one real AI feature end to end: server call, streaming UI, and an external tool. |
| **2 — Specialization** | 5–11 | Makes that feature safe, durable, and cheap enough that someone else can run it in production. |

Track 2 is not optional — it's the half that separates "I got a demo working" from "I shipped
something." The capstone build in Part V is what closes the guide.

### The minimum path

Eleven Deliveries is weeks of real work, and several end in an artifact that is a session or
more on its own — Delivery 10 wants tracing exported and visualized, Delivery 11 wants a CI job
with an eval floor. Walked linearly, most students stop mid-track with nothing shippable.

State the short route at calibration and let them choose:

| Route | Deliveries | What they end up with |
|---|---|---|
| **Minimum** | 0 → 1 → 2 → 3 | One AI feature actually shipped: a typed tool, a streaming UI, a tool result rendered as a component, and a real approval gate on the risky action. |
| **Full** | 0 → 11 | Everything, including the durable and production half. |

Rules for the minimum path:

- **The acceptance bar of each Delivery on it does not move.** Fewer Deliveries, same bar.
- Log the choice in the progress file (`**Path:** minimum`) and log the skipped Deliveries as
  **debt**, not as done. `/forja debt` has to show them.
- Delivery 6 (guard-rail) is the first debt item to call in if the feature touches anything
  destructive or private — say so when they pick the minimum path rather than after.
- Don't sell it as equivalent: it ships a feature, it doesn't make the feature safe to leave
  running unattended. One line, then move on.

**Deliberately out of scope:** image generation, speech/transcription, and reasoning-model
specifics. The loop, the UI stream, and the production half matter more. If the student's
domain genuinely needs one of these, treat it as an artifact swap inside an existing
Delivery — not as a new Delivery.

---

### Delivery 0 — Foundation and the provider decision

**Concept.** The loop is the same one as any agent framework: the model decides to call a
tool, code executes it, the result goes back in, the model decides again — until a
`stopWhen` condition is met. The AI SDK's twist: there is no dev playground and no project
registry. The first execution is a plain script or a single Route Handler calling
`generateText` directly.

**Blocking decision — model access strategy.** Present the real trade-off, not a neutral
list:

- **AI Gateway** (`import { gateway } from 'ai'`, or a bare `'provider/model'` string):
  zero provider packages to install, one API key, and load-balancing/fallback across
  providers for free. The cost: **Vercel's Gateway is now a hop between the student and the
  model provider.** If the answer to "what will this agent read?" includes customer data or
  proprietary source, that hop is a new party in the data path — the same policy question
  Mastra's Delivery 0 raises about a public API, one layer earlier.
- **A specific provider package** (`@ai-sdk/anthropic`, `@ai-sdk/openai`, ...): the call goes
  directly to that provider, no Gateway in between, but now the model is an **object**
  (`anthropic('claude-sonnet-4-6')`), not a string — mixing the two styles in one call throws.
- **A local model** (community Ollama-compatible provider): for anything that can't leave the
  machine at all.
- If there's no restriction, simplify: Gateway or one provider package, and move on.

**Artifact.**
- `npm install ai zod` (+ a provider package if not using the Gateway).
- `.env` with the key, `.env` in `.gitignore` (check it, call it out if missing).
- A script (`tsx run.ts` or similar) calling `generateText` once and printing the result.

**Acceptance.** Terminal output pasted. Then walk them through what happened between the
prompt and the response — the acceptance bar is the run, not their retelling of it.

**Pitfalls.**
- Passing a Gateway string as the `model` for a call that also imports a provider factory —
  pick one style per call and be explicit about why.
- A committed key. Check `git status` before unlocking the next step.

**Predict first.** Have them commit to a number before editing anything: if the Gateway model
string is replaced by a direct provider import, how many files have to change? Then have them
make the swap on a throwaway branch and count what `git diff --stat` actually lists.

**Why it matters.** Walk the student through what actually changes when the Gateway string is
swapped for a direct provider import: every file that has to change is a place where the model
choice leaked out of configuration and into logic, which makes the size of that change a direct
measure of coupling. Verify the current behavior against the installed version before asserting
it (Verify-before-quoting rule).

---

### Delivery 1 — First typed tool + structured output

**Why this one first.** Same reason as the Mastra track: it's their most repetitive, fixed-
format task, and it forces the two ideas everything else depends on — a **typed tool
boundary** and **structured output** instead of prose.

**Concepts.**
- **`tool()`** with a Zod `inputSchema` — this is the system boundary. Validate here, not in
  the prompt.
- **`stopWhen`** — without it, `generateText` **stops after one step even if tools are
  defined**. This is the single most common "why didn't my tool run twice" bug in this SDK.
- **Structured output** via `output: Output.object({ schema })` on `generateText`. Don't teach
  `generateObject` as the default — it's deprecated as of the 6.0 migration guide, even though
  it still runs.

**Artifact.**
- One tool doing real, read-only work in the student's domain (a diff reader, a ticket
  fetcher, a log grep — translate via the adaptation table).
- A `generateText` call with that tool, `stopWhen: isStepCount(n)` or `hasToolCall('final...')`
  chosen deliberately, and `output: Output.object({...})` producing a validated object with at
  least 4 required fields.
- A runnable script or one Route Handler, `npm run` or `curl`-able.

**Acceptance.** A real run against real input, with the validated JSON pasted.

**Pitfalls.**
- Forgetting `stopWhen` and concluding the tool "doesn't work" when it just never got a second
  step.
- The tool's `description` is read by the model, not a human — a vague one means it never gets
  called. Have them rewrite it if weak.
- Shelling out inside a tool without sanitizing input is command injection. Cover it.

**Predict first.** Before they touch the code, have them commit to an answer: if the tool's
`description` changes and nothing else does, will the agent behave differently? Then have
them reword it — weaker, then sharper — and re-run the same prompt each time.

**Why it matters.** Explain that the tool's `description` is read by the model, not by a
human — it is the routing logic that decides whether the tool gets called at all. Half the
behavior of an agent lives in prose the compiler never checks, which is why a weak
description is a bug, not a documentation gap.

---

### Delivery 2 — Streaming chat UI

**Concept.** This is the AI SDK's actual product. `streamText` on the server, `useChat` on
the client, and the **message-parts model**: a `UIMessage` isn't a string, it's an array of
typed `parts` (`text`, `tool-<name>`, `reasoning`, ...). The client renders parts as they
arrive; nothing waits for the full response.

There is **no built-in memory** here, unlike Mastra's `Memory` package. Persisting a
conversation is the student's job — usually via the `onFinish` callback on `streamText`,
written to their own database.

**Artifact.**
- A Route Handler: `streamText({ ..., messages: convertToModelMessages(uiMessages) })`,
  returned via `createUIMessageStreamResponse({ stream: toUIMessageStream({ stream: result.stream }) })`.
- A client component using `useChat` with a `DefaultChatTransport` pointed at that route.
- Persistence: `onFinish` writing the final messages somewhere real (even a local file counts
  for this Delivery — the point is the callback exists and fires).

**Acceptance.** A live conversation in the browser, streaming incrementally, **and** a second
page load that restores the same conversation from storage.

**Pitfalls.**
- Rendering `message.content` instead of iterating `message.parts` — this breaks the moment a
  tool call shows up.
- Treating `onFinish` as guaranteed-once; ask what happens if the client disconnects mid-stream
  and whether their persistence handles a partial write.
- Forgetting `convertToModelMessages` and passing `UIMessage[]` straight to `streamText`.

**Predict first.** Before they test the reload, have them commit to an answer: if the tab
closes halfway through a streamed response, what ends up in storage? Then have them kill the
tab mid-stream, reload the page, and read back what `onFinish` actually wrote.

**Why it matters.** Explain the trade-off they just made: hand-written persistence means they
own the schema, the write path, and the partial-write failure modes, and in exchange they get
full control over where the data lives and how long it stays. Contrast that with what Mastra's
`Memory` and its `resourceId`/`threadId` scheme hand over ready-made. Verify the current
behavior against the installed version before asserting it (Verify-before-quoting rule).

---

### Delivery 3 — Generative UI, and a real approval gate

**Concept.**
- **Generative UI**: a tool's result doesn't have to become text — the client can render a
  different React component per `part.type === 'tool-<name>'`, keyed to that tool's `output`.
  This is the thing Mastra genuinely has no equivalent for.
- **`needsApproval`**: a tool property (`true` or an async function of the input) that pauses
  the loop and asks the human before `execute` runs. At the bare `streamText`/`ToolLoopAgent`
  level this is **request-scoped** — it doesn't survive a server restart. (Delivery 7 covers
  the durable version.)

**Artifact.**
- Take the tool from Delivery 1 (or a new one) and render its result as a real component
  (a card, a table — not a text blob) driven by the tool-call part in the UI.
- Add a second, riskier tool in the same domain with `needsApproval` — conditional on input
  where it makes sense (e.g. only above a threshold), matching the cookbook pattern, not a
  blanket `true` if the domain calls for nuance.
- A client-side approve/reject control that resumes the specific paused call.

**Acceptance.** A run where the risky tool call visibly pauses, the student rejects it once and
approves it once, and both outcomes are shown.

**Pitfalls.**
- Building the approval UI as a generic confirm dialog disconnected from the actual tool input
  — the whole point is showing *what* is about to run, with its real arguments.
- Assuming `needsApproval` persists across a page refresh at this level. It doesn't yet — that
  gap is the reason Delivery 7 exists.

**Predict first.** With a tool call paused waiting for approval, have them call it out loud:
does that pending approval survive a page refresh, and does it survive restarting the dev
server? Then have them do both and try to approve the same call afterwards.

**Why it matters.** Explain what durable state buys: an approval that survives a process
restart is a different guarantee from one that lives inside a single request, and the gap shows
up as a silently lost decision, not as an error. Contrast this gate with Mastra's
`suspend()`/`resume()` model. Verify the current behavior against the installed version before
asserting it (Verify-before-quoting rule).

---

### Delivery 4 — Consume an external MCP server

**Concept.** **MCP** (*Model Context Protocol*) connects agents to external tools. The AI SDK
is a **client only**: `createMCPClient` from `@ai-sdk/mcp` connects to a server (stdio, HTTP,
or SSE) and merges its tools into your `tools` object. There is **no `MCPServer` export in the
AI SDK** — if the student later wants to expose their own agent as an MCP server (the way
Mastra's Delivery 4 does), they need the raw `@modelcontextprotocol/sdk`, outside this
toolkit's scope. Say this plainly; don't let them go looking for an `MCPServer` import that
doesn't exist here.

**Artifact.**
- `createMCPClient` connected to a real external MCP server relevant to their domain (a
  filesystem server, GitHub, a docs server — whatever they already query by hand).
- The merged tool set passed into the Delivery 2/3 chat, with `stopWhen` adjusted since these
  tools add steps.
- Client closed in a `finally` block.

**Acceptance.** A conversation where the model calls a tool that only exists because of the
external MCP server, result shown end to end in the UI.

**Pitfalls.**
- Not closing the client — connections leak across requests in a long-running server.
- An MCP tool result becomes untrusted input the moment it re-enters the model's context.
  Discuss *prompt injection* arriving from a document or ticket the external server returned.
- Assuming MCP tool outputs are typed — without an explicit `outputSchema` in `.tools({ schemas })`,
  they're `unknown` until you validate them.

**Predict first.** Before they go looking, have them commit to an answer: the package that
just connected them to someone else's MCP server — does it also let them serve one? Then have
them search the installed package's exports and types for a server entry point and report what
is actually there.

**Why it matters.** Explain that consuming a protocol and serving it are separate jobs: being a
client says nothing about being a server, so exposing the Delivery 2 agent to someone else's
client means owning the transport, the tool schemas, and the connection lifecycle themselves.
Show what that work consists of instead of letting them hunt for an import that closes the gap.
Verify the current behavior against the installed version before asserting it (Verify-before-quoting rule).

---

## TRACK 2 — SPECIALIZATION

*Before entering here, run the Track 1 consolidation (Part V) and log it in
`~/.forja/progress/vercel-ai-sdk.md`. It's a teaching pass over what they built, not a gate.*

---

### Delivery 5 — RAG over their own documents

**Concept.** **RAG**: chunk → embed → store → retrieve → inject only the relevant chunks. The
AI SDK gives you `embed`/`embedMany` and nothing else — no vector store, no chunker, no
reranker. Unlike Mastra's `@mastra/rag`, the pipeline is fully DIY; the student picks a vector
store (pgvector if they already run Postgres, or a hosted one) themselves.

**Artifact.** A retrieval-backed agent over the docs from the adaptation table's Delivery 5
row, with a hard rule in `instructions`: no retrieved source, no answer — "not found," never
filled from memory.

**Acceptance.** A question answerable only from the indexed documents, answered with a correct
citation, and an out-of-scope question answered "not found."

**Pitfalls.**
- Chunking quality dominates the result more than model choice. Have them compare two
  strategies.
- No first-party reranker — if precision is bad, that's the first thing to add, not a bigger
  model.

**Predict first.** Have them state up front how the agent will answer a question the index
cannot cover when the prompt insists on an answer anyway. Then have them run three prompts
built to push past the rule and check every reply for a citation that resolves to a real chunk.

**Why it matters.** Explain the difference between a rule the model is asked to follow and a
rule it cannot break: text in `instructions` is a suggestion that degrades under pressure,
while a guard-rail is code that fails the request. Show where the "no source, no answer" rule
has to move to become one — the retrieval path itself, refusing to generate when the result set
is empty.

---

### Delivery 6 — Guard-rails and middleware

**Concept.**
- **`wrapLanguageModel`** with a `LanguageModelV4Middleware` (`wrapGenerate`/`wrapStream`) is
  the AI SDK's native interception point — for redaction, blocking, or rewriting what goes in
  or out of a model call. A prompt is a suggestion; middleware and tool-level code are the law.
- **No first-party eval/scorer package.** Unlike `@mastra/evals`, there's nothing shipped here
  to score relevancy or toxicity automatically. The honest path is a small scoring function
  (even an LLM-as-judge call) with a numeric floor, asserted in a test — DIY, and say so.

**Artifact.**
- A tool that runs a query against a real data source, with code-level validation rejecting
  anything destructive (mirrors Mastra's SQL-advisor case) plus a mandatory `needsApproval`.
- A `wrapLanguageModel` middleware redacting one class of sensitive data from model output,
  applied to the model actually used by the agent.
- A minimal eval: a handful of reference cases, a scoring function, and a numeric floor that
  fails loudly when not met.

**Acceptance.** An attempt to induce the destructive action via the prompt, blocked **in
code**, not by the model refusing.

**Pitfalls.**
- Streaming guardrails are genuinely harder — you don't have the full output until the stream
  ends. Ask how they'd redact a token that's still arriving.
- Treating the eval floor as decoration instead of a real assert that can fail a build.

**Predict first.** With the output middleware in place, have them commit to an answer: if a
sensitive value arrives inside a *tool result* rather than being generated by the model, does
the redaction catch it? Then have them feed exactly that — a tool returning a fake secret — and
read both the model's output and what the middleware saw.

**Why it matters.** Explain that redaction on the way out does nothing for what came in: tool
results, retrieved documents, and MCP payloads enter the context unfiltered, and once a
sensitive value is in the prompt it has already crossed the boundary. Make the point that every
edge where data enters the model needs its own filter, not only the edge where text leaves.

---

### Delivery 7 — Durable workflow with real approval

**Concept.** Everything up to here runs in one request; state dies with the process.
**`@ai-sdk/workflow`**'s `WorkflowAgent`, combined with `'use step'` on tool `execute`
functions and `'use workflow'` on the orchestrating function, gets automatic retries and
persistence. `needsApproval` on a `WorkflowAgent` tool **actually suspends and resumes the
run** — the durable version of Delivery 3's request-scoped approval.

Flag this to the student explicitly: this package is younger than the rest of the SDK.
Confirm its current API shape against the docs before building on it for anything real.

**Artifact.** Re-implement Delivery 3's risky tool inside a `WorkflowAgent`, with the
`'use step'`/`'use workflow'` directives and the Route Handler wired through `start(...)` and
`createModelCallToUIChunkTransform()`.

**Acceptance.** The run pauses for approval, the process is restarted (or the request is
dropped), and resuming still recovers the pending approval — not just the happy path running
straight through.

**Pitfalls.**
- Conflating this with Delivery 3's `needsApproval` — same property name, different
  durability guarantee. Make them state the difference before moving on.
- Retrying a step with a side effect that isn't idempotent (booking, charging) — the automatic
  retry is not free correctness.

**Predict first.** Before the restart test, have them commit to an answer: with the same tool
property (`needsApproval`) on both sides, what exactly makes the `WorkflowAgent` version
survive a process kill that the Delivery 3 version doesn't — where is the pending decision
physically stored in each case? Then have them kill the process in both versions and watch
which pending approval comes back.

**Why it matters.** Explain the cost of making a step durable and retryable: anything with a
non-idempotent side effect, a dependency that must be observed live, or a payload too large to
persist is a bad candidate, because an automatic retry re-runs it. Walk the student through
classifying their own steps on that basis. Verify the current behavior against the installed
version before asserting it (Verify-before-quoting rule).

---

### Delivery 8 — Multi-agent, and when not to use it

**Concept.** Composing multiple agents (an orchestrator calling specialist `ToolLoopAgent`s,
or agents exposed to each other as tools) versus one agent with a bigger tool set and a good
`stopWhen`. Same lesson as Mastra's Delivery 8, and just as true here: every hop is more
latency, more tokens, one more failure point.

**Artifact.**
- An orchestrator delegating between two of the earlier Deliveries' agents.
- The competing version: one agent, all the tools, a single `stopWhen`.
- Side-by-side measurement — tokens, latency, correctness — across ~10 real requests.

**Acceptance.** A comparison table and the student's own recommendation, defended with the
numbers, not intuition.

**Pitfalls.**
- Recursion between agents with no depth limit.
- Multiplicative cost, not additive — walk through why.

**Predict first.** Before the ten runs, have them write down which build wins on tokens, on
latency, and on correctness — and by how much. Then have them fill the comparison table from
the measurements and put the prediction next to it.

**Why it matters.** Explain that routing errors are silent: a misroute returns a plausible
answer, so nothing in production flags it unless a correctness check was built on purpose. Then
walk through the bill on the nine correct requests — the extra hop's latency and tokens are
paid every time it routes right, which is the actual price of the architecture.

---

### Delivery 9 — Cost, caching, and fallback

**Concept.**
- **Token accounting**: `usage`/`totalUsage` on every result — input, output, total.
- **Prompt caching**: provider-specific (`providerOptions.anthropic.thinking`/cache controls,
  or the provider's own cache fields) — reordering stable content first is what makes it work.
- **Gateway fallback**: `providerOptions.gateway.order` lets you rank providers for the same
  model call; a genuinely free reliability win over a single provider.
- **Retry and idempotency**: retrying a tool with a side effect duplicates the effect unless
  the operation is idempotent.

**Artifact.**
- Per-run cost logged for each agent built so far.
- `providerOptions.gateway.order` configured and **tested** by forcing the primary provider to
  fail.
- One agent's prompt reordered to put stable content first, with a before/after cache-hit
  measurement.

**Acceptance.** A real cost-per-run number per agent, and the fallback demonstrably kicking in.

**Pitfalls.**
- Optimizing the model before optimizing the context. Context first.
- Retrying the non-idempotent tool from Delivery 6. Name it specifically.

**Predict first.** Have them name a percentage before measuring anything: of the cost of one
run, how much is context resent unchanged every time — system prompt, tool definitions, static
preamble? Then have them derive the real number from `usage` on a live run and compare.

**Why it matters.** Show the student how to split the cost of a run into what the request
genuinely needs and what is resent unchanged every time — system prompt, tool definitions,
static context. That second number is the one to attack first: it scales with traffic and buys
nothing, while swapping models trades quality for a discount.

---

### Delivery 10 — Observability

**Concept.** The SRE-breaking fact still holds here: **the most common failure returns 200.** A
wrong answer, a tool that never got called, a loop that burned steps without converging — none
of that is an error rate.

- **`telemetry`** (the 7.0 rename of `experimental_telemetry`) attaches OpenTelemetry spans per
  call — `functionId`, `metadata`. Confirm the current exporter setup against the docs; this
  area (`registerTelemetry`, `@ai-sdk/otel`) is one of the more actively changing corners.
- **Agent SLIs**: same questions as Mastra's Delivery 10 — p95 latency, completion rate without
  human intervention, cost per run within budget.

**Artifact.**
- Exported, visualized tracing for at least one multi-step agent.
- Three written SLIs for the most-used agent, with numeric targets.
- Redaction of sensitive data in whatever logs the student's own persistence writes.

**Acceptance.** A trace showing every model/tool span for a real multi-step run, and an alert
firing on a deliberately bad run (cost or step count over a threshold).

**Pitfalls.**
- Prompts and responses land in the spans. Telemetry with customer data in it is a leak
  vector — check what the exporter records before pointing it at a hosted backend.
- Tracing only the final call: a multi-step run's cost lives in the intermediate steps.
- An alert on error rate alone — the whole point of this Delivery is that the failure mode
  returns 200.

**Predict first.** Before they break anything, have them list which of their own signals fires
on a run that returns a confidently wrong answer at normal cost and latency. Then have them
force exactly that run and check the alert, the dashboards, and the trace against the list.

**Why it matters.** Explain why a wrong answer at 200 and normal latency is invisible to every
default signal they have — error rate, uptime, and latency all read healthy. Correctness has to
be measured deliberately, through evals, sampled human review, or an outcome signal from
whoever consumes the answer; otherwise it is simply not measured.

---

### Delivery 11 — Testing, and shipping without a build step

**Concept.**
- **`ai/test`**: `MockLanguageModelV4` + `simulateReadableStream` let you unit-test a
  `streamText`/`generateText` call deterministically, without hitting a real model.
- A tool is a pure function — test it directly, no mock needed.
- **No `mastra build` equivalent.** Shipping is just shipping the Next.js/Node app normally —
  there's no separate agent-build artifact. That's a real simplification versus Mastra; say so.
- **Eval as a merge gate**, same principle as Mastra: run the Delivery 6 eval floor in CI,
  block the PR if it drops.

**Artifact.**
- Unit tests for the tools from Deliveries 1 and 6.
- A `streamText` test using `MockLanguageModelV4` asserting on the tool-call sequence, not just
  the final text.
- The Delivery 6 eval suite running in CI with a score floor.
- The app deployed (or deploy-ready) with no extra agent-specific build step.

**Acceptance.** A red CI run caused by a deliberately worsened prompt dropping the eval score,
and green after reverting it.

**Pitfalls.**
- A non-deterministic eval makes CI flaky — ask how variance is controlled (temperature,
  sample count, a floor instead of an exact value).
- An API key in CI. Cover secret management.

**Predict first.** Before they worsen the prompt, have them commit to two numbers: how far the
eval score drops, and how much the *same* prompt varies between two consecutive runs of the
suite. Then have them run it twice on each prompt. If the run-to-run spread is close to the
drop they engineered, the floor can't tell a regression from noise — and that's the finding.

**Why it matters.** Explain that an eval floor is a claim about acceptable quality, and a
number with no recorded reasoning behind it gets lowered the first time it blocks a release.
Show the student to write down what the floor was derived from and what evidence would justify
moving it — that record is the only thing that makes the gate hold under deadline pressure.

---

## PART V — CONSOLIDATION

There are no exams here. Nothing the student has to recite, nothing scored, nothing repeated
as a penalty. The shipped feature is the evidence; what's left is making sure they understand
the system they now own. Run this with `/recap` and log it in
`~/.forja/progress/vercel-ai-sdk.md`.

### Track 1 consolidation — reading back what they built

Open their own files and teach the whole feature as one thing, tracing real code they wrote.
No questions, no scoring. Cover these five, each anchored to a specific line of theirs:

1. **The tool-calling loop** — walk the actual path of one of their runs, and explain what
   `stopWhen` decides, what it defaults to, and what breaks when nobody sets it.
2. **Model wiring** — show the difference between a Gateway model string and a
   provider-factory model object in their own code, and why mixing the two styles in one call
   fails.
3. **The message model** — go through their UI rendering and explain what `UIMessage.parts`
   carries that flat content does not, and what silently disappears from the screen when they
   render the wrong one.
4. **The two approval gates** — put their Delivery 3 gate next to their Delivery 7 one and
   explain exactly which durability guarantee changes between them.
5. **Prompt injection surface** — go through the feature and mark every untrusted input that
   reaches the model: tool results, MCP responses, retrieved documents, user-controlled text.

Verify anything version-specific against the installed package before asserting it (Verify-before-quoting rule).
If a topic lands and they clearly hadn't seen it, note it in the progress file — that's a gap
to revisit inside Track 2, not a reason to send them back.

**Then run the Track 1 retrospective, and lead it — this is analysis, not interrogation:**

1. Where each feature fails in production, and the plan for it.
2. Cost per run for each agent, and which could run on a cheaper model via the Gateway.
3. Which decisions coupled the project to a specific provider or to Vercel's Gateway
   (portability debt).
4. What they built that shouldn't be an agent at all and could be a plain function.

Item 4 matters here as much as it does in Mastra: knowing when *not* to reach for a
tool-calling loop is worth more than knowing the API.

### Track 2 closing — the capstone build

Not an exam either: a build, reviewed like a peer's PR. Hand over only the prompt:

> Ship a new AI feature for a real problem at your job that hasn't been covered yet, meeting
> all of these criteria:
>
> - A tool with boundary validation and a unit test using `ai/test`.
> - A real `needsApproval` gate — durable if the operation would survive a restart in
>   production, request-scoped if it genuinely wouldn't need to.
> - A code-level guard-rail for the domain's destructive operation, via middleware or the tool
>   itself.
> - Exported tracing and 2 SLIs with numeric targets.
> - An eval suite with a floor, running in CI.
> - Cost per run measured and documented, with the Gateway fallback configured.
> - A one-page document: why this needed a tool-calling agent and not a plain deterministic
>   function, and what was deliberately left out (memory? RAG? multi-agent?) and why.

They're an expert when they deliver this without asking how. Review it like a peer's merge
request: name what's fragile, then explain the reasoning behind each criterion they met — and
where the one-page document only describes a choice instead of justifying it, supply the
justification yourself. Then mark the guide complete in `~/.forja/progress/vercel-ai-sdk.md`.

If they want a target beyond this: the next step is reading the `ai` package's source for
`generateText`'s step loop and `streamText`'s stream-transform pipeline. Whoever has read the
loop no longer needs a guide.

---

## Glossary

- **AI SDK Core** (`ai`): the headless functions — `generateText`, `streamText`, `tool`,
  `embed`. Framework-agnostic, runs anywhere Node/edge runtimes do.
- **AI SDK UI** (`@ai-sdk/react` and equivalents): the framework hooks — `useChat`,
  `useCompletion`, `useObject` — that consume a streamed response in a client component.
- **Tool**: a typed function the model can call. System boundary — validate here.
- **`stopWhen` / `StopCondition`**: the replacement for the old `maxSteps` — a function
  deciding when the tool-calling loop stops. Defaults to one step if omitted.
- **`ToolLoopAgent`**: a stateless class wrapping the loop with a default `stopWhen` of 20
  steps. The AI SDK's closest thing to Mastra's `Agent`, without persistence.
- **`WorkflowAgent`** (`@ai-sdk/workflow`): the durable version — `'use step'`/`'use workflow'`
  directives give automatic retry and persistence across restarts.
- **`needsApproval`**: a tool property pausing execution for a human decision. Request-scoped
  on the bare loop, durable (suspend/resume) on `WorkflowAgent`.
- **Generative UI**: rendering a tool-call result as a specific React component instead of
  text, keyed on the tool-call's `part.type`.
- **`UIMessage` / parts**: the message shape used by `@ai-sdk/react` — an array of typed parts
  (`text`, `tool-<name>`, `reasoning`, ...), not a plain string.
- **MCP** (*Model Context Protocol*): the open protocol connecting agents and tools. The AI SDK
  is a **client** for it (`@ai-sdk/mcp`); it does not ship a server exporter.
- **AI Gateway**: Vercel's hosted routing layer — a bare `'provider/model'` string resolves
  through it, adding Vercel as a hop versus a direct provider package call.
- **Middleware** (`wrapLanguageModel`): the native interception point on input/output of a
  model call — where a guard-rail belongs, not in the prompt.
- **Embedding**: a vector representation of text, used for similarity search (RAG).
- **Idempotency**: the property that repeating an operation produces the same effect — a
  prerequisite for safe retries.
- **Telemetry**: the `telemetry` option (renamed from `experimental_telemetry`) attaching
  OpenTelemetry spans to a call.
- **Mock provider** (`ai/test`): `MockLanguageModelV4` + `simulateReadableStream` — deterministic,
  no real model call, for unit tests.
