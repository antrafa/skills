# forja

A mentor skill for AI coding agents that teaches by making you build — not by building for
you. Point it at a track (currently: [Mastra](https://mastra.ai) or the
[Vercel AI SDK](https://ai-sdk.dev)) and it walks you through a sequence of real
deliverables, critiques your proof of work, and refuses to hand you a finished file.

Works with **Claude Code**, **Codex**, **Gemini CLI**, and **opencode** out of the box, and
with any agent that can read a Markdown file and follow instructions.

## Why this exists

Most "learn X with AI" prompts degrade into the AI writing the code and you watching. `forja`
enforces the opposite: the agent is not allowed to write to your implementation files. It can
show you a snippet in chat, explain the reasoning, point at the exact file path — but the
keystrokes are yours. Progress only advances after you paste real proof of execution (terminal
output, a screenshot, an actual response) and the agent has picked it apart.

On Claude Code that rule is enforced **in code**, not just in the prompt: `install.sh`
registers a `PreToolUse` hook (`hooks/forja-guard.py`) that denies every write outside
`~/.forja/`, plus the obvious shell equivalents (`>`, `tee`, heredocs, `npm install`,
`git commit`). It arms itself only while `~/.forja/tutor-active` exists, so your other
sessions are untouched. On hosts without hooks the rule is prose, and prose drifts — that's
the honest limit, and it's the same lesson the guard-rail deliverable teaches.

Progress is written to `~/.forja/progress/`, outside any project directory, so it survives
`rm -rf`, doesn't leak into a commit, and can be picked up again from a different agent or a
different machine.

## What you get

- **A strict mentor persona** — no flattery, criticizes weak decisions first, never writes
  implementation code (see [Core rules](#core-rules)).
- **A gated delivery sequence** — each deliverable has a concept, an artifact to build, an
  acceptance bar, and known pitfalls. No proof, no advancing.
- **A minimum path** — each track marks a 4-deliverable short route that still ends in
  something defensible, because eleven deliverables is weeks of work and the acceptance bars
  don't get softer. The skipped ones are logged as debt, not as done.
- **No pinned versions anywhere** — the tracks carry a name map (which symbol lives in which
  package) and never a version list. The agent resolves the current version with `npm view`
  before the first deliverable, then defers to whatever is actually installed in your project.
- **Domain adaptation** — each track's example artifacts are written for one reference
  profile (a backend engineer moving into architecture/SRE for `mastra`, a full-stack
  product engineer for `vercel-ai-sdk`), but the underlying concept-to-artifact mapping is
  meant to be translated to whatever you actually do. See the track file's adaptation table.
- **A foundations safety net** — if you're shaky on the language, the package manager, Git,
  or basic LLM concepts, the mentor answers those questions inline without treating it as an
  interruption, then returns you to the deliverable.
- **Persistent, portable progress** — one file per track under `~/.forja/progress/`,
  readable by any agent that supports this skill.

## Available tracks

| Track | File | Covers |
|---|---|---|
| `mastra` | [`tracks/mastra.md`](tracks/mastra.md) | Building production AI agents with the [Mastra](https://mastra.ai) TypeScript framework — tools, structured output, memory, deterministic workflows with human-in-the-loop, MCP exposure, RAG, guard-rails/evals, runtime context, multi-agent tradeoffs, cost, observability, and CI. |
| `vercel-ai-sdk` | [`tracks/vercel-ai-sdk.md`](tracks/vercel-ai-sdk.md) | Shipping AI features with the [Vercel AI SDK](https://ai-sdk.dev) — typed tools and structured output, streaming chat UI, generative UI with approval gates, MCP as a client, RAG, guard-rail middleware, durable workflows, multi-agent tradeoffs, cost, observability, and testing with mock models. |

Each track file is self-contained and versioned independently of `SKILL.md`. Adding a new
track means adding a new file under `tracks/` — the mentor rules apply to all of them.

## Installation

### Via [skills.sh](https://skills.sh) (recommended)

```bash
npx skills add antrafa/forja -g
```

`-g` installs at the user level for every supported agent; drop it to install into the
current project only. This path does **not** run `install.sh`, so `~/.forja/progress/` is
created by the mentor on first use and **the guard hook is not registered** — the No-write
rule falls back to prose. If you want it enforced, run `install.sh` from wherever skills.sh
put the files, or register the hook yourself:

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash",
  "hooks": [ { "type": "command",
    "command": "python3 <path-to-forja>/hooks/forja-guard.py" } ] } ] } }
```

### Via git clone

```bash
git clone https://github.com/antrafa/forja.git ~/.agents/skills/forja
bash ~/.agents/skills/forja/install.sh
```

`install.sh` is idempotent. It symlinks the skill into whichever supported agents are
present on your machine, creates `~/.forja/progress/`, and registers the guard hook in
`~/.claude/settings.json` (backing the file up to `settings.json.forja-bak` first):

| Agent | Symlink target |
|---|---|
| Shared agents directory | `~/.agents/skills/forja` |
| Claude Code | `~/.claude/skills/forja` |
| Codex | `~/.codex/skills/forja` and `~/.codex/prompts/forja.md` |
| Gemini CLI | `~/.gemini/skills/forja` and `~/.gemini/commands/forja.md` |
| opencode | `~/.config/opencode/commands/forja.md` |

Don't copy the files by hand — the symlinks are what let one edit to `SKILL.md` or a track
file propagate to every agent at once.

For any other agent: paste `SKILL.md` plus the track file you want at the start of a session
and tell it to adopt the role described there.

## Usage

### Recommended workflow

Use one track per conversation and name it explicitly on the first turn. Prefer the
host-native, fully qualified form because it reliably activates the skill and avoids command
collisions:

| Host | Start or select a track | Run a command |
|---|---|---|
| Codex | `$forja mastra` | `$forja map` |
| Claude Code / Gemini CLI | `/forja mastra` | `/forja map` |

Then work in this loop:

1. Read the current Delivery and answer its prediction — one guess about what your code is
   about to do. Guess wrong freely: the run is what settles it, and nothing here is scored or
   held against you.
2. Build the artifact yourself, then paste raw evidence of execution — terminal output, a
   screenshot, or the real agent response. A summary such as "it worked" does not unlock the
   next Delivery.
3. Read the mentor's explanation of why it worked, starting from wherever your prediction and
   reality diverged. The mentor teaches the reason instead of quizzing you for it.
4. Use `basics` for language or tooling questions and `stuck` when you need the next hint.
   This keeps the question inside the track without asking the agent to take over the build.
5. Use `map` to see the route and `progress` before ending a work session. When the
   conversation gets noisy, start a fresh one and invoke `$forja` or `/forja`; the progress
   file resumes the active track.

Use `off` only when you intentionally want to leave tutor mode and delegate implementation.
It does not mark a Delivery complete or erase its acceptance gate. Invoke `on` before
returning to the guided build. Short aliases such as `/map` remain supported, but the fully
qualified forms above are the recommended interface.

Start a track:

```
/forja mastra
```

Resume wherever you left off — reads `~/.forja/progress/`, matches it to the right track,
and picks up from your last completed deliverable:

```
/forja
```

List available tracks without starting one:

```
/forja tracks
```

Hosts with native skill mentions, such as Codex, accept the equivalent `$forja`,
`$forja mastra`, and `$forja tracks` forms. Every command below supports both host forms.

### In-conversation commands

Once a track is running, use `/forja <command>` on slash-command hosts or
`$forja <command>` on skill-mention hosts such as Codex. Short aliases remain supported.

| Portable invocation | Short alias | Effect |
|---|---|---|
| `/forja next` or `$forja next` | `/next` | Proof accepted → describe the next deliverable |
| `/forja example <thing>` or `$forja example <thing>` | `/example <thing>` | Show an illustrative snippet with a source |
| `/forja why` or `$forja why` | `/why` | Explain the engineering reason behind the last instruction |
| `/forja basics <question>` or `$forja basics <question>` | `/basics <question>` | Answer a language, tooling, or environment question and return |
| `/forja review [target]` or `$forja review [target]` | `/review` | Read the files you point at and critique them |
| `/forja stuck` or `$forja stuck` | `/stuck` | Give the next hint, not the solution |
| `/forja skip` or `$forja skip` | `/skip` | Skip the current deliverable, logged as debt |
| `/forja map` or `$forja map` | `/map` | Show where you are and what's left |
| `/forja progress` or `$forja progress` | `/progress` | Update the progress file without advancing |
| `/forja debt` or `$forja debt` | `/debt` | List everything skipped or pending |
| `/forja recap` or `$forja recap` | `/recap` | Have the mentor teach back the whole system you built |
| `/forja tracks` or `$forja tracks` | — | List available tracks |
| `/forja off` or `$forja off` | `TURN OFF TUTOR` | Disable tutor restrictions for this conversation |
| `/forja on` or `$forja on` | — | Restore tutor restrictions for this conversation |

### First run

The mentor doesn't start teaching immediately. It first asks three calibration questions —
your experience with the track's language, your experience building with LLMs, and a real
repetitive task from your job — because the artifacts you build are adapted to your answers,
not fixed in advance. Answer them, and it opens the first deliverable.

### A typical loop

1. The mentor describes a deliverable: a concept, an artifact to build, and an acceptance bar.
2. You write the code yourself, in your own editor.
3. You run it and paste the real output back into the conversation.
4. The mentor critiques what's wrong or fragile first, then explains *why* it worked — the
   mechanism and the trade-off — and unlocks the next deliverable. It teaches the reason
   instead of quizzing you for it; the artifact you just ran is the test.
5. Repeat. `~/.forja/progress/<track>.md` is updated as you go, so a new session — even in
   a different agent — resumes exactly here.

Every deliverable opens with one prediction: what do you expect your code to do? The run
answers it, not you, so a wrong guess costs nothing and blocks nothing — it just makes the
explanation in step 4 land instead of washing over you.

## Core rules

These apply across every track and are the actual contract of the skill (full text in
[`SKILL.md`](SKILL.md)):

1. **No implementation writes.** The agent never uses a write tool on your project files.
   The one exception is `~/.forja/`. Enforced by a hook on Claude Code.
2. **No API and no version answered from memory.** Before showing any framework-specific code,
   the agent resolves the current version (`npm view`, then your lockfile) and checks
   documentation for *that* version, citing the source. Nothing in this repository pins a
   version, because a pin written once reads as verified while being wrong.
3. **Hard gate on proof.** No deliverable advances without pasted evidence of a real run.
4. **Depth adapts, rigor doesn't.** A beginner gets more foundational explanation; the
   acceptance bar for a deliverable is identical regardless of stated experience level.
5. **Foundations questions are in-scope, not an interruption.** Ask anything about the
   language, the tools, or the environment at any time.

## Repository layout

```
forja/
├── SKILL.md               mentor rules + track routing (loaded on every invocation)
├── README.md              this file
├── install.sh             idempotent symlink installer + hook registration
├── commands/
│   └── forja.md           pointer used by agents without native skill support
├── hooks/
│   └── forja-guard.py     PreToolUse guard enforcing the no-write rule
└── tracks/
    ├── mastra.md          the Mastra track content (loaded only when selected)
    └── vercel-ai-sdk.md   the Vercel AI SDK track content (loaded only when selected)
```

`SKILL.md` stays small on purpose — it's read on every invocation. Track content only loads
once a track is actually selected.

## Contributing a track

A track is a single Markdown file under `tracks/`. It should follow the same shape as
`mastra.md`:

- a concept-to-artifact adaptation table;
- an **unpinned** API name map (which symbol lives in which package) plus the `npm view`
  commands the agent runs to resolve versions itself — never a version list;
- a minimum path: the shortest subset of deliverables that still ends in something defensible;
- a sequence of gated deliverables, each with concept, artifact, acceptance, pitfalls, a
  `Predict first` prompt, and a `Why it matters` directive — all six, on every deliverable;
- a consolidation section where the mentor teaches the finished system back.

No exams — the artifact is the assessment. Reference mentor rules **by name**
("the Progression-gate rule"), never by number; `SKILL.md` gets reordered and a number rots
silently. Open a PR.

Two things live in more than one file and have to move together in the same commit:

- **Commands and routing** — `SKILL.md`'s tables and the README command table below.
- **The track list** — the README track table mirrors the `tracks/` directory, which is
  the source of truth; `SKILL.md` reads the directory and carries no list of its own.

## License

MIT
