# Playbook: Help Center and Command Explanation (`/alterego help`)

This playbook guides the quick listing of all Alterego subcommands and the
in-depth explanation of a specific command when the developer wants to know
exactly what it does and when to use it.

---

## Invocation Modes

```
/alterego help                           (lists every command, 1 line each)
/alterego help <cmd>                     (explains the command in detail)
```

In Codex:
```
$alterego help
$alterego help <cmd>
```

---

## 1. `/alterego help` (No Arguments) — The Quick Summary

When the user types just `/alterego help`, **render the
Intent map from [SKILL.md](../SKILL.md)**, which is already in context, in three
columns: `Subcommand` | `Argument` | `What it does`,
compressing the map's *Conduct* column into one line each.

Rendering rules:

- **Every map row that has a subcommand goes in**, including `help`. A row without a subcommand (free-form request) stays out — the
  user asked for the list of commands.
- Map order, preserved. No invented command that is not there.

The map is the skill's only list of commands. Keeping a second copy here
guarantees that one of the two goes stale.

*Footer tip:* Type `/alterego help <cmd>` to see full details of any command.

---

## 2. `/alterego help <cmd>` — The Full Command Card

When the user asks to explain a command (e.g. `/alterego help tour-project` or `/alterego help dev`),
provide the full card structured in the following blocks:

### Standard Card:

```markdown
# Command: `/alterego <command-name>`

> **In one sentence:** <Objective summary of the command's purpose>

- **Syntax:** `/alterego <cmd> <expected-arguments>`
- **Reference playbook:** `[playbook-<name>.md](references/playbook-<name>.md)`

---

### 1. What it does
<Clear explanation, 1 to 2 paragraphs, of the command's mechanics, what it analyzes and what it produces.>

### 2. When to use (Ideal triggers)
- <Real situation 1 where this command shines>
- <Real situation 2>
- <Real situation 3>

### 3. When NOT to use (and what to use instead)
- If you want <X>, **do not use this command**: use `/alterego <other-command>`.
- If the task is <Y>, prefer <Z>.

### 4. Deliverable & Destination (Where it saves)
- **In the chat:** <What it shows in the conversation>
- **On disk (fallback):** `<path/to/fallback/file>` (or "Does not change files").

### 5. Practical examples
```bash
/alterego <cmd> <example-1>
/alterego <cmd> <example-2>
```
```

---

## Disambiguation Catalog (Quick Reference)

The "when to use" of each command is already in the Intent map of
[SKILL.md](../SKILL.md) — do not repeat it here. This catalog keeps only what
that map does not cover: the pair of commands that look alike and the criterion
that tells one from the other. When building a command's Card, pull the "when
to use" from the map and the "when NOT to use" from here.

- **`start`** vs. `setup` / `daily`: sets the session's guardrails and lens, in seconds and once per session; calibrating who the user is happens once in a lifetime and is `setup`; organizing what to do today is `daily`.
- **`dev`** vs. free-form request: the full ritual (plan, worktree, TDD, review) is for what deserves stages; a trivial 1-line fix does not go through the pipeline.
- **`tour-project`** vs. `project-analyser`: the tour maps and teaches the architecture; it does not hunt vulnerabilities or technical debt in depth — that is `project-analyser`.
- **`project-analyser`** vs. `review` / `mr`: audits the whole codebase or a module; for a single PR or file, `review` or `mr` are enough and come out faster.
- **`local-app`** vs. free-form request / `dev`: creates a new project from scratch; to add a screen or component to a project that already exists, use a free-form request or `dev`.
- **`idea`** vs. free-form "think together" / `local-app` / `persona product-planning`: `idea` takes a raw idea (a business, an internal tool, a personal project) through the four `lapida` phases to a go / pivot / stop; weighing a technical proposal or a structural choice is the free-form "think together" or `adr`; `local-app` builds the app once it is decided; the `product-planning` lens questions scope during any task, without the guided phases.
- **`digest`** vs. `tour-project` / `review`: digests a document already written (SDD, ADR, plan); it does not read source code — that is `tour-project` or `review`.
- **`review`** vs. `mr`: local code, the current branch's diff or a specific file; for a remote MR/PR on GitLab/GitHub, `mr` sets up an isolated worktree and measures impact outside the diff.
- **`mr`** vs. `review`: remote MR/PR by number or URL; for something not yet committed, `review`.
- **`adr`** vs. trivial decision: reserved for a structural choice that is expensive to reverse; a narrow-scope implementation detail does not need an ADR.
- **`refactor`** vs. `dev` / free-form request: the change that breaks things outside the file being touched and needs a prerequisite graph; a refactor that fits in one green step is a free-form request, and a refactor that is part of a feature being built is step 4 of `dev`.
- **`daily`** vs. execution: organizes and prioritizes; does not implement code.
- **`study`** vs. `tour-project`: learning a technology or a general concept; to understand the current project's codebase, `tour-project`.
- **`sre`** vs. `review` / `dev`: a production symptom that demands measurement and rollback; a logic bug with no availability impact goes through `review` or `dev`.
- **`skill`** vs. `review`: a document an **agent** reads (skill, `AGENTS.md`, reference) and the yardstick is context load and pointers; code a **person** maintains is `review`.
- **`setup`**: profile calibration, typically once — not a day-to-day routine (an already calibrated profile needs no repetition).
- **`persona`** vs. the default clone: use `persona` to take on a surgical, hyper-specific disciplinary lens (AppSec, QA, Devil's Advocate, Tech Lead Reviewer, etc.); for balanced everyday work with the Threefold DNA (pragmatic dev + architect + human partner), Alterego's default clone is the natural choice.
