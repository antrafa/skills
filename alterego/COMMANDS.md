# `alterego` command guide

Complete reference of what you can ask for today, with real examples. If you only
want to know what the skill is, read the [README](README.md); this is about how to
use it.

The skill runs inside a terminal harness (Claude Code, Antigravity or Codex).
There is nothing to open: you type in the same place where you already talk to
the agent.

---

## 1. How to invoke

| Harness | Prefix | Example |
|---|---|---|
| Claude Code | `/alterego` | `/alterego review src/Billing.java` |
| Antigravity (`agy`) | `/alterego` | `/alterego daily` |
| Codex | `$alterego` | `$alterego mr 42` |

From here on the guide uses `/alterego`. On Codex, swap it for `$alterego`.

You can also activate the skill without any prefix, by stating the intent: *"how
would I do this?"*, *"do it my way"*, *"think with me"*. A generic technical
request ("write a regex") does **not** activate the persona, and that is on
purpose.

---

## 2. The routing rule (read this before anything else)

The first word after `/alterego` is only a subcommand **if it is in the table in
section 3**. Anything else is a free-form request.

```
/alterego review src/App.java     → subcommand review, target src/App.java
/alterego check this file         → free-form request ("check" is not a subcommand)
```

In practice this means you never have to memorize anything: writing in plain
language works. The subcommands exist for when you want the full ritual of that
kind of work.

**A subcommand with no target does not turn into an interrogation.**
`/alterego review` assumes the obvious target from context (open file, MR of the
current branch, incident under discussion) and says which it assumed. It only
asks when there is no context at all.

---

## 3. All subcommands

Every subcommand has one English name. A name that is not in this table is
read as a free-form request and routed by intent.

| Command | Argument | For what |
|---|---|---|
| `/alterego start` | `[<persona>\|none]` | Open the session: arm the guardrails and pick the lens |
| `/alterego dev` | `[<step>]` | 7-step guided development pipeline |
| `/alterego refactor` | `<goal>` | Structural refactor by the Mikado Method |
| `/alterego daily` | `[<overview>]` | Organize the day and prioritize |
| `/alterego wrap` | `[<notes>]` | Close the day and record what is pending |
| `/alterego review` | `<file\|diff>` | Local code review |
| `/alterego mr` | `[<iid>\|<url>]` | Evaluate a remote MR/PR and measure impact |
| `/alterego adr` | `<decision>` \| `review` | Structural decision with recorded rationale, or a review of the triggers |
| `/alterego commit` | `[<scope>]` | Commit message from the diff |
| `/alterego pr-desc` | `[<iid>\|<branch>]` | MR/PR description in four blocks |
| `/alterego tour-project` | `[<focus>]` | Technical onboarding in a new repository |
| `/alterego project-analyser` | `[<module>]` | 360° technical audit of the codebase |
| `/alterego idea` | `[<idea>\|<file>]` | Refine a raw idea into a viable, testable proposal |
| `/alterego local-app` | `<idea>` | Complete, 100% local web application |
| `/alterego digest` | `[<target>]` | Visual digest of an AI-generated doc (SDD, ADR, plan) |
| `/alterego skill` | `[<target>]` | Write or review a skill or a doc an agent reads |
| `/alterego sre` | `<symptom>` | Investigate an incident by measurement |
| `/alterego study` | `<topic>` | Guided study with the Socratic method |
| `/alterego setup` | — | Calibrate your profile |
| `/alterego persona` | `[<name>\|<action>]` | Switch the persona lens, list the catalog or create one (`new <name>`) |
| `/alterego help` | `[<cmd>]` | List the commands or open the card of one |

---

## 4. Command by command

### `/alterego start [<persona>]` — open the session

The first command of the session, when you want it to start protected and with a
chosen lens instead of both defaulting in silence.

```
/alterego start                    (arms the guardrails and asks which lens)
/alterego start appsec             (arms them and already activates the AppSec lens)
/alterego start none               (arms them and keeps the default clone)
```

**What you get:** two things set and confirmed in three lines. The `guardrails`
mode on — confirmation per individual action that does not generalize to the
next, diff shown before writing to a sensitive file, dependency change confirmed
— and the active persona, picked by number or by name from a numbered list
(catalog, then your own personas in `~/.alterego/personas/`), created on the
spot, or none at all (`0`).

It configures and gets out of the way: it does not organize the day, does not
read the repository, does not propose work. If `guardrails` is not in the
environment, the session opens anyway and says what actually holds — this skill's
own limits.

Full flow in [playbook-start.md](references/playbook-start.md).

---

### `/alterego refactor <goal>` — structural refactor without a red tree

```
/alterego refactor get OrderService off the direct Oracle dependency
/alterego refactor split the God class in the billing module
/alterego refactor swap the HTTP client under the integration layer
```

**What you get:** the Mikado Method. The change is attempted in the most naive
way, the breakage is collected, and the attempt is **reverted** — each error
becomes a prerequisite in a graph saved at `docs/refactor/<slug>-mikado.md`.
Then it goes from the leaves up: each one an independent `refactor:` commit with
the suite green, and the behavior change only in the last commit.

**What it does not do:** save a half-done attempt. Reverting is the method, not
a defeat — and every discard is announced before it runs. It also does not start
without a safety net: with no test that fails when the behavior changes, the
first leaf is a characterization test.

---

### `/alterego daily` — organize the day

Dump everything that is on your desk, without organizing it first. Organizing is
its job.

```
/alterego daily
/alterego daily I have a sync with management at 2pm, a big PR from a teammate to
  review, the reports pod went down overnight and I need to design the new gateway
```

**What you get:** the board split between noise and real priority, applying the
yardstick: production stability before new fronts, unblocking a blocked colleague
is high priority, architecture and risk come before features when they compete.
It comes with the day sliced into deliverables and a proposal for where to start.

`/alterego daily` alone, with no context, organizes with what the persona already
knows from your profile and the repository. If there is a `wrap` from yesterday in
Mentat, its pending items enter the board without you having to remember.


---

### `/alterego wrap [<notes>]` — close the day

The counterpart of `daily`. Without it, tomorrow starts from scratch.

```
/alterego wrap
/alterego wrap closed MR 42, the gateway slipped to tomorrow, found out the
  connection pool ignores the configured timeout
```

**What you get:** the day rebuilt from the evidence (git, worktrees, MRs,
session), in four blocks: **Done**, **Left over**, **Learned**, **Open risk**; and
tomorrow's first step in one line. It offers once to record "Left over" and
"Learned" in Mentat (or in `~/.alterego/journal.md` without Mentat) and only
writes with your "yes".

---

### `/alterego commit [<scope>]` — commit message

Writes the message from the real diff, not from your description of it.

```
/alterego commit
/alterego commit billing
```

**What you get:** if the diff mixes intents, first the proposed split with the
files of each commit; then the message in the format
`<type>(<scope>): <description>`, imperative, up to 72 characters, with a body
only when the why is not obvious. If the repository's `git log` follows another
convention, that one wins and it says which it followed. The `git commit` only
goes out with your "yes".

---

### `/alterego pr-desc [<iid>|<branch>]` — MR/PR description

A description you can review without opening the diff blind.

```
/alterego pr-desc
/alterego pr-desc 42
```

**What you get:** a title in the commit format and four blocks: **What changed**
(by intent, not by file), **Why**, **How to validate** (executable steps) and
**Out of scope and side effects** (who is affected without having asked). If the
repository has an MR template, it is filled in rather than replaced. Opening or
editing the MR on the remote is an external action: only with the "yes".

---

### `/alterego review <target>` — local code review

For a file, a local diff or an implementation proposal. For a remote MR/PR, use
`mr` (next section).

```
/alterego review src/services/BillingService.java
/alterego review the diff of the current branch, focus on concurrency
/alterego review                          (assumes the diff/file from context)
```

**What you get:** a hunt for concurrency, N+1, ORM abuse, resource leaks,
security and scope, with the smallest diff that solves it. If the code is clean,
the verdict is *No findings in the reviewed scope*, with no invented cosmetic
criticism.

**What it does not do:** apply the fixes on its own. Asking for a review
authorizes analysis, not changes.

---

### `/alterego mr [<iid>|<url>]` — remote MR/PR and impact analysis

The question this command answers is *what in the rest of the project depends on
what this MR changed*, precisely what the GitLab/GitHub web UI does not show.

```
/alterego mr                    (MR of the current branch)
/alterego mr 42
/alterego mr https://gitlab.com/group/project/-/merge_requests/42
/alterego mr what does this MR break?
/alterego mr is it tested enough?
```

**What you get:** an isolated worktree from the MR ref (resolves forks), a read of
the whole diff and a `grep` for the changed symbols **outside** the diff: the
caller nobody updated, the moved file still referenced in the chart, the
migration the production version cannot handle, the env var the deploy needs. It
also warns if you have unpushed local commits on the branch.

**The gate:** the verdict comes out in the terminal and it stops. Commenting,
approving and requesting changes are three separate authorizations; each one
shows the exact text before it goes out, and the "yes" for one does not count for
the next.

**Prerequisite:** `glab` (GitLab) or `gh` (GitHub), authenticated.

```bash
glab auth login --hostname <host>
```

---

### `/alterego adr <decision>` — structural decision

Use it before closing a choice that will be expensive to reverse.

```
/alterego adr communication between the billing service and the notification
  service: synchronous or a queue?
/alterego adr is this new library worth adopting, or do we solve it with what we have?
```

**What you get:** context, trade-offs, **the discarded options and why**, the
consequences and the triggers that reopen the decision. The premise is that a
decision without a recorded rationale is a decision that will be reopened six
months from now.

The formal dossier goes to `~/.alterego/decisions/`.

`/alterego adr review [<project>]` does the way back: it
reads the `reopen-when` of every active decision in the archive, checks it
against the current evidence and returns a table with *fired*, *did not fire* or
*no way to measure*. Reopening is still a new decision, and only happens if you
ask.

---

### `/alterego sre <symptom>` — incident by measurement

```
/alterego sre reports pods restarting with OOM
/alterego sre latency went up and the payment service started returning 502
/alterego sre CrashLoopBackOff in the billing-production namespace
```

**What you get:** measurement before conjecture. cgroups v2 deltas
(`memory.events`), comparative thread dumps, GC logs, and only then a hypothesis
of the cause. The memo comes with immediate mitigation and explicit rollback.

**What it does not do:** propose a code fix before having numbers. That is the
difference between a diagnosis and a guess.

---

### `/alterego study <topic>` — guided study

```
/alterego study Raft Consensus
/alterego study cgroups v2 memory.events
/alterego study JVM tuning and p95 analysis
```

**What you get:** first it aligns the mission (why you need this now), calibrates
the depth by your repertoire, explains the mechanism without hermetic jargon,
challenges you with Socratic questions to make it stick, and closes with
**"In short"**.


---

### `/alterego idea [<idea>]` — refine a raw idea

```
/alterego idea an app that connects small farmers to city restaurants
/alterego idea a tool that opens our deploy tickets automatically
/alterego idea ideas/estoque-feirantes.md       (resumes where it stopped)
```

**What you get:** the idea goes through the four phases of the partner skill
`lapida` — **EXPLORE** (real problem, audience, evidence), **CHALLENGE**
(assumptions, pre-mortem, doing nothing, through the `devils-advocate` lens),
**REFINE** (options, the smallest version worth building) and **FIT**
(competitors with a source, fit signals, the next test) — and ends in `go`,
`pivot` or `stop`, conditional on that test.

- First it classifies the idea (`business`, `internal product`, `personal
  project`) and rewrites it as a problem, with no solution inside; nothing moves
  until you confirm.
- Questions come in rounds of up to three, each with a recommended answer, under
  a header like `CHALLENGE · question 7 of ~14`; the forecast is recomputed and
  explained when it moves.
- Each phase stops with its summary and waits for your ok. `avança` fills the
  rest of a phase with the recommended answers, marked as assumptions.
- Competitors and market numbers come with a source or labeled as a hypothesis.

**Where it saves:** `ideas/<slug>.md` in the current directory, resumable in a
later session. **Optional prerequisite:** the `lapida` skill. Without it, the
same four phases run inline in the chat, without the idea file, and the
installation is offered once at the end.

**When not to use:** to weigh a technical proposal or a structural choice, talk
it through freely or use `adr`; to build the app once it is decided, `local-app`
or `dev`.


---

### `/alterego setup` — calibrate the profile

Run it once when installing, and again when your context changes.

```
/alterego setup
/alterego setup my resume is at ~/docs/cv.pdf
/alterego setup just show the status of the partner skills, don't install anything
```

**What you get:** a 5-question interview, or ingestion of your resume, LinkedIn
and real messages of yours. The profile is written to Mentat when it is
installed, otherwise to `~/.alterego/profile.md`.

At the end it shows the status of the partner skills, displays the clone and
symlink commands, and installs **only the ones you approve**: installing a skill
is an external action, never automatic.

---

### `/alterego persona [<name>|<action>]` — switch the persona lens

Temporarily, or for the session, changes the working stance to one of the 11
specialized personas in the self-contained catalog in `references/personas/`,
keeping continuity, the user's personal profile and the skill's guardrails.

```
/alterego persona                         (lists all 11 catalog personas)
/alterego persona appsec                  (activates the AppSec lens for the session)
/alterego persona tech-lead-reviewer diff (takes on the persona and analyzes the diff)
/alterego persona info devils-advocate    (shows the persona's detailed card)
/alterego persona reset                   (restores the default clone: Dev, Architect, Person)
/alterego persona new in-house-dba        (creates a persona of yours in ~/.alterego/personas/)
```

`persona new` asks four questions (the question the lens asks first, the priority
order, the always/never and the output format), shows the card and writes it
outside the skill's repository. A persona of yours with the same name as a catalog
one replaces the catalog one.

**What you get:** the analysis, the Always/Never rules, the output format and the
critical questions of that specialty (e.g. AppSec focuses on IDOR and injection;
QA focuses on unlikely edges; the Devil's Advocate runs the pre-mortem and attacks
fragile premises).

For the full catalog and execution rules, see [playbook-persona.md](references/playbook-persona.md).

---

## 5. `/alterego dev` — the Guided Development Pipeline

Seven steps with an exit gate, with the **Superpowers** plugin as the discipline of
each one. It is for work that deserves a ritual: a new feature, a structural
refactor, anything you do not want to do straight on the main branch.

```
/alterego dev                          (shows the map of the 7 steps)
/alterego dev brainstorming <task>     (runs step 1)
/alterego dev 4                        (runs step 4, by number)
/alterego dev tdd                      (runs step 4, by name)
```

| # | Step | Subcommand | Superpowers skill | Exit gate |
|---|---|---|---|---|
| 1 | Conception | `dev brainstorming` / `dev 1` | `brainstorming` | Approach chosen with recorded rationale |
| 2 | Plan | `dev plan` / `dev 2` | `writing-plans` | Plan in `docs/superpowers/plans/` approved by you |
| 3 | Isolation | `dev worktree` / `dev 3` | `using-git-worktrees` | Worktree created with confirmed name and base, baseline build green |
| 4 | TDD | `dev tdd` / `dev 4` | `test-driven-development` | Suite green, no skipped test |
| 5 | Review | `dev review` / `dev 5` | `requesting-code-review` | No critical or attention-level finding left open |
| 6 | Verification | `dev verify` / `dev 6` | `verification-before-completion` | Build, lint and tests with exit code 0 in the handoff |
| 7 | Delivery | `dev finish` / `dev 7` | `finishing-a-development-branch` | PR description ready and learning saved in Mentat |

You do not have to walk the seven in order. Going straight to `dev tdd` on a task
that already has a plan is normal use.

### Guided conduction & Safe Context-Clear
On every interaction of the `dev` pipeline, the persona displays the **Roadmap
Widget** showing:
- **Current step** and **next step** with progress icons (`✅`, `⏳`, `⏹️`).
- **Safe Context-Clear Point:** when an artifact is saved to disk (plan in `docs/superpowers/plans/`, green suite committed or verification finished), the persona actively tells you that you can `/clear` or open a new session, and gives the exact command to resume without carrying polluted history.

**In step 7:** commit, push and opening the PR each require a "yes". Merge is
never an action of the persona.

---

## 6. `/alterego digest` — Anti-Vibe-Coding Visual Digest

Turns dense AI-generated documents (SDDs, ADRs, implementation plans, specs) into
**30-to-60-second visual digests**, using the partner skill `doc-digest`:

```
/alterego digest docs/superpowers/plans/2026-09-19-feature.md
/alterego digest docs/specs/sdd-payments.md --html
```

- **Mermaid is mandatory:** draws a flowchart, sequence diagram or component architecture.
- **Decision matrix:** a direct table of what changes vs. what does NOT change (protected scope).
- **Anti-Vibe-Coding box:** callouts highlighting the AI's fragile premises and the risks you need to validate.
- **Links to the original doc:** anchors to sections and lines for quick lookup.

**With no target** (`/alterego digest`), it assumes the obvious document from
context (the plan just written, the ADR under discussion) and says which it
assumed.

**Optional prerequisite:** the `doc-digest` skill. Without it, the digest comes
out inline in the chat with the same content (minus `--html`, which belongs to
that skill) and the installation is offered once, with the command in front of
you. A missing skill never becomes a blocker.


---

## 7. `/alterego tour-project` — Technical Onboarding in the Repository

Runs a complete guided tour through the source code of a new repository, as if a
senior tech lead were sitting next to you explaining the system from scratch:

```
/alterego tour-project                   (full tour)
/alterego tour-project auth              (tour focused on authentication)
```

- **Initial reconnaissance:** identifies language, framework and architectural style.
- **Structure & Critical Points:** controllers, services, stores, queues, APIs and database, with clickable `file:///...` links.
- **Flow in Mermaid:** visual diagram of the request end to end.
- **Ideal study order:** numbered script from the 1st to the 7th file to master the project fast.
- **Saving:** by default saves to `docs/tour-project/tour-[project].md` as the fallback, or wherever you ask.

---

## 8. `/alterego project-analyser` — Deep Technical Audit

Runs a 360° technical sweep of the whole codebase, assessing consistency,
security, business rules, test quality and production risks:

```
/alterego project-analyser               (full audit of the codebase)
/alterego project-analyser payments      (in-depth audit of one module)
```

- **360° sweep:** architecture, OWASP Top 10, concurrency, N+1, observability, validations and error handling.
- **Business rule mapping:** decodes implicit and explicit rules from the code.
- **Test diagnosis:** identifies gaps and "theatrical tests" (that mock everything and guarantee no real behavior).
- **Manual test guide:** generates a complete step-by-step script with scenarios, preconditions and expected results.
- **Full report:** lists findings with severity, impact and suggested fix, saving to `docs/project-analyser/analysis-[project].md` as the fallback (or wherever you indicate).

---

## 9. `/alterego local-app` — Local Application Development

Turns any idea into a complete, working web application that is **100% runnable
locally on your machine** (no dependency on the cloud, Vercel or Docker to run):

```
/alterego local-app "k8s metrics dashboard using SQLite"
/alterego local-app "task manager with tags and semantic search"
```

- **Current folder:** generates the project directly in the current working directory.
- **Stack decision:** asks whether you prefer **Next.js full-stack** (App Router, Server Actions, APIs) or **React + Router (Vite SPA)**, presenting pros and cons for your idea.
- **AI decision (if applicable):** asks whether you will use local models (Ollama, local CLI, MCP) or direct API keys (OpenAI, Gemini, Anthropic, Groq).
- **Design direction:** suggests at least 3 visual styles adapted to the idea, inspired by [getdesign.md](https://getdesign.md/) and [neuform.ai](https://neuform.ai/).
- **Dark & Light mode, mandatory:** every application is born with dark/light theme support and a smooth toggle.
- **UI stack:** Tailwind CSS + shadcn/ui + Lucide Icons + strict TypeScript.

---

## 10. `/alterego skill` — Write and Review Skills

A document an **agent** reads (`SKILL.md`, `AGENTS.md`, `CLAUDE.md`, a reference
reached through a pointer) is not written like documentation for people. This
command applies the yardstick of the `writing-for-agents` skill.

```
/alterego skill ~/.claude/skills/my-skill        (reviews an existing skill)
/alterego skill AGENTS.md                        (reviews the repo's agent doc)
/alterego skill new "migrations reviewer"        (writes one from scratch)
/alterego skill                                  (assumes the obvious target from context)
```

**What you get:** a diagnosis from the biggest lever to the smallest, in this
order:

1. **The pointer** (the `description`, or the line in `AGENTS.md` that names the
   doc): it costs on *every* turn of *every* session, so that is where a cut pays
   the most.
2. **A rule written in two places:** one source of truth, the others cite it.
3. **Hierarchy:** what only some branches reach leaves the main file.
4. **A step with no completion criterion** that tells done from not done.
5. **A prohibition** that could have been a target behavior (prohibiting pushes
   the prohibited thing into the context).
6. **No-op:** a sentence the model already obeys by default and that pays its
   load to say nothing.

**This command's own limit:** skills usually live **outside the project**
(`~/.claude/skills/`, `~/.agents/skills/`). When the path leaves the repository
the conversation is in, the target is shown before writing.

**What it does not do:** mix a wording refactor with a change to what the skill
tells the agent to do. Those are two diffs.

**Optional prerequisite:** the `writing-for-agents` skill. Without it, the
diagnosis comes out through the same six levels, inline.

---

## 11. `/alterego help` — Help and Command Cards

Quick help center and detailed documentation for every Alterego command:

```
/alterego help                           (lists all commands in 1 line each)
/alterego help dev                       (details the dev command)
/alterego help tour-project              (full card of tour-project)
```

- **`/alterego help` (no arguments):** displays a compact table of all subcommands and the 1-line summary of each.
- **`/alterego help <cmd>`:** displays the command's **full technical card**:
  - What it does, in detail;
  - **When to use:** ideal scenarios and triggers;
  - **When NOT to use:** anti-patterns and which command to use instead;
  - **Deliverable & Destination:** where it saves files to disk (default fallback);
  - **Practical examples** of use.

---

## 12. Requests without a subcommand

A good part of daily use has no subcommand. These intents are recognized in the
conversation:

| What you want | How to ask | What changes |
|---|---|---|
| Think together | `/alterego think with me: does this interface solve a real boundary?` | Tests the premise, exposes the risk, recommends. Does not touch files. |
| Do and deliver | `/alterego refactor this function with the smallest sufficient diff` | Executes the authorized work and returns the handoff. Does not stop at "may I?". |
| Unblock a colleague | `/alterego a teammate is stuck on this error, help me explain it` | Root cause + didactic guidance, without condescension. |
| Give feedback to a colleague | `/alterego help me give feedback to a teammate about Friday's deploy` | Situation, behavior, impact and one concrete ask. Text in your voice; sending it is up to you. |
| Write in your style | `/alterego write a short message to the team explaining the decision` | Ready-to-use text, no corporate speak and no announcing the persona. |
| Script for management | `/alterego prepare the 5-minute script for the alignment meeting` | Goes straight to the point that unblocks the decision, with up to two measured numbers. |

### The handoff format

When it executes something, the return has five fixed blocks:

1. **What needs you**: pending decision or authorization
2. **What changed**: with `file:line`
3. **What was verified**: the command and its real output
4. **What I assumed**: assumptions made on its own
5. **What was left out**: scope not covered

A verification that did not run shows up as `Not verified — <reason>`, never as
presumed success. That is the contract: if it says it passed, the command ran.

---

## 13. Running without an interactive session

Every command works in non-interactive mode, useful for scripts and CI:

```bash
# Claude Code
claude -p "/alterego review src/Billing.java"
claude -p "/alterego dev brainstorming <task>" --permission-mode acceptEdits

# Antigravity
agy --print "/alterego daily"
agy --mode accept-edits --print "/alterego dev tdd <task>"

# Codex
codex exec '$alterego mr 42'
codex exec --sandbox workspace-write '$alterego dev tdd <task>'
```

The permission mode is your choice and applies to that run. Without it, in
non-interactive mode, whatever requires approval is denied, which is fine for
reading, reviewing and planning.

---

## 14. What always asks for authorization

Applies to every command. The rule is that authorization does not carry over to
the next action nor to a new run.

| Action | Requires |
|---|---|
| Change a reversible local file within the scope of the request | Nothing: the request to execute already authorizes it |
| `git commit` | Explicit "yes", after seeing status and diff |
| `git push` | A "yes" separate from the commit |
| Create a branch | Name and base confirmed by you beforehand |
| Comment on, approve or request changes on an MR | A "yes" for each one, with the exact text in front of you |
| Install a partner skill (clone, symlink) | A "yes" after seeing the command |
| Send a message, e-mail or anything to the outside | A "yes" for that content and that target |
| Destructive action | A "yes", regardless of the active permission mode |

Preparing a text never authorizes sending it. No commit or PR carries
co-authorship or a mention of AI.

---

## 15. Where profile and memory live

The order is the same for reading and for writing:

1. `~/.mentat/profile.md` and `~/.mentat/core-memory.md`: the **default
   destination** whenever Mentat is installed
2. `~/.alterego/profile.md`: local fallback, only in the absence of Mentat
3. The skill's own reference criteria and DNA

Memory is always Mentat, and always through the `mentat` skill: writing to
`~/.mentat/` by hand desynchronizes the graph. The archive `~/.alterego/decisions/`
holds the formal decision dossier; it is not a source of memory.

Corrected its behavior? The correction applies immediately to the current
delivery. Persisting the preference in the profile is a separate request.

---

## 16. Installation

```bash
git clone https://github.com/antrafa/alterego.git ~/workspace/skills/alterego
SKILL_SRC=~/workspace/skills/alterego

ln -s "$SKILL_SRC" ~/.claude/skills/alterego          # Claude Code
ln -s "$SKILL_SRC" ~/.agents/skills/alterego          # harness-agnostic
ln -s "$SKILL_SRC" ~/.codex/skills/alterego           # Codex
ln -s "$SKILL_SRC" ~/.gemini/config/skills/alterego   # Antigravity (agy)
```

Then run `/alterego setup` to calibrate the profile.

Optional: `glab` or `gh` authenticated (for `/alterego mr`), the
[`mentat`](https://github.com/antrafa/mentat) skill (for memory across sessions),
the [Superpowers](https://github.com/obra/superpowers) plugin (for the Dev
Pipeline) and the [`writing-for-agents`](https://github.com/mattpocock/skills)
skill by Matt Pocock (for `/alterego skill`).
