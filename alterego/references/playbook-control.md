# Playbook: Control Report (`/alterego control`, `/alterego clear`)

A long piece of work outlives the session that started it. The **control
report** is one HTML file per piece of work that carries it across sessions: a
**handoff** at the top that a fresh session can resume from, and the status of
the activities below it. With it, clearing the context costs nothing — the state
the next session needs is on disk, not in the chat history.

---

## Invocation modes

```
/alterego control <goal>     (creates the report for this piece of work)
/alterego control            (updates the report of the current work; creates one if there is none)
/alterego control <path>     (updates that report)
/alterego clear              (updates the handoff and hands over to a fresh session)
```

In Codex: `$alterego control`, `$alterego clear`.

---

## 1. Where it is saved

Ask once, when the report is created, offering the two places:

- **In the repository:** `<repo root>/.alterego/reports/<slug>.html`. Add
  `.alterego/` to `.git/info/exclude` on the same write — that file is local
  and never committed, so the folder stays out of `git status` and out of the
  MR. Outside a git repository, the current folder.
- **Global:** `~/.alterego/work/<project>/reports/<YYYY-MM-DD>-<slug>.html`,
  with `<project>` resolved as in
  [archive.md](archive.md#working-files-outside-the-repository-always).

No answer means global. A path the user names wins. The slug describes the
work (`login-migration`), lowercase, hyphens, no accents.

**One report per piece of work, updated in place.** A new session does not get
a new file; it rewrites the same one.

---

## 2. Design

The default is [report-design.md](report-design.md). If the user has their own
design document — a `DESIGN.md` in their instructions or in the agent's config
directory — ask once which to use, this skill's default or theirs, and record
the answer in the profile (Mentat, else `~/.alterego/profile.md`, as in
[SKILL.md](../SKILL.md#personal-context-and-continuity)). With the answer on
record, do not ask again. With no design document of their own, use the
default without asking.

---

## 3. What goes in the report

A self-contained HTML file, in this order:

1. **Status markers** in `<head>`, read by the lookup without opening the body:
   ```html
   <meta name="alterego-status" content="open">   <!-- open | done -->
   <meta name="alterego-updated" content="2026-10-02T18:40">
   ```
2. **The handoff**, first thing on the page, with a copy button, between
   markers the lookup reads alone:
   ```html
   <!-- alterego:handoff -->
   <pre id="handoff">…</pre>
   <!-- /alterego:handoff -->
   ```
3. **Activities**: one row each — activity, state (`pending`, `in progress`,
   `done`, `blocked`), evidence (commit sha, file, command output) and date.
4. **Decisions** taken along the way, each with its why in one line.
5. **Update log**: date and one line per update, most recent on top.

**The handoff is a prompt that works pasted into any session, with or without
this skill.** It carries, in up to ~25 lines: the goal in one sentence; where
the work stopped; the next step, concrete enough to start without asking; the
decisions already taken, so they are not reopened; the files and paths that
matter; open questions; and how to verify the current state. It ends with the
report's own path.

---

## 4. Updating it

Rebuild the handoff and the activities **from evidence** — `git log`, `git
status`, the plan and the files on disk — never from what the chat remembers.
An activity is `done` only with its evidence in the row. When every activity is
done, set `alterego-status` to `done`: the lookup skips it from then on.

Who updates it:

- `/alterego control` and `/alterego clear`, on request.
- **`dev`**, at each Safe Context-Clear point
  ([playbook-dev.md](playbook-dev.md#safe-context-clear-points)), and
  **`refactor`**, after each leaf committed — **only when the current work
  already has a report**. Neither creates one on its own.

Updating a report is a local, reversible write inside the task: no question
needed.

---

## 5. Lookup when the session opens

`/alterego` and `/alterego start` look for an open report and offer to resume
it. The rule lives in [SKILL.md](../SKILL.md#routing) (*Report lookup*), because
the bare `/alterego` reads no reference. The `./*.html` step in it is what
catches reports written by hand before this command existed.

---

## 6. `/alterego clear`

Clearing the context is a command of the harness (`/clear` in Claude Code), and
a skill has no way to run it. What this command does is leave the next session
ready to resume:

1. **Ask whether to keep a control report.** Yes → create or update it (§1–§4).
   No → write the handoff in the chat, ready to copy, and create no file.
2. **Hand over** in two lines:

```markdown
Handoff saved at `<path>`.
Type `/clear`, then `/alterego` — it finds the report and offers to resume.
```

Without a report, the second line becomes: *Type `/clear` and paste the
handoff above.*

---

## Closing checklist

- [ ] Was the location asked on creation, with global as the default for no answer?
- [ ] On a repository report, is `.alterego/` in `.git/info/exclude`?
- [ ] Does the handoff stand alone, ending with the report's path?
- [ ] Is every `done` activity backed by evidence in its row?
- [ ] Is `alterego-status` `done` only when every activity is done?
