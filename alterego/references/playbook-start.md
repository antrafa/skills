# Playbook: Opening the Session (`/alterego start`)

Two things are decided once per session and shape every answer after it: **how
much friction stands between the agent and an irreversible action**, and **which
lens it thinks through**. Both default silently if nobody sets them. This
playbook makes them an explicit, ten-second choice at the top of the session.

It is not profile calibration — that is `/alterego setup`, and it happens once
in a lifetime, not once a session.

---

## Invocation modes

```
/alterego start                  (arms the guardrails and asks which lens)
/alterego start <persona>        (arms the guardrails and activates that lens directly, no question)
/alterego start none             (arms the guardrails and keeps the default clone)
```

In Codex: `$alterego start`.

---

## 1. Arm the guardrails

`guardrails` is a catalog skill and a **session mode**: once invoked it stays on
until the user turns it off or the session ends. It layers a stricter discipline
on top of this skill's *Autonomy and limits*: confirmation per individual action
that never generalizes to the next one, the diff shown before a sensitive file is
written, dependency changes confirmed, and the consequence stated in the question
itself rather than a bare "may I run X?".

1. **Detect it** the same way as any catalog skill — the loop in
   [sources.md](sources.md#missing-catalog-skill-degrade-deliver-offer).
2. **Invoke it.** On Claude Code, the `Skill` tool with `guardrails`. On a
   harness with no skill tool, read its `SKILL.md` and apply it for the rest of
   the session.
3. **Missing?** Say so in one line and carry on — the session still opens. This
   skill's own *Autonomy and limits* already cover commit, push, branch, external
   actions and AI attribution; what is lost is the per-action strictness. The
   catalog maps no public repository for `guardrails`, so what gets offered at
   the end — once, never as a condition for continuing — is the
   [public fallback](onboarding.md#public-fallback-for-the-internal-skills),
   which blocks mechanically through a hook and does not read intent.

<critical>Arming the guardrails is not a promise to be careful. It is a mode that
is either loaded in context or is not. Never report the session as protected
without having invoked the skill or read its rules — an announced guardrail that
was never loaded is worse than none, because the user stops watching.</critical>

---

## 2. Choose the lens

Show the catalog compactly and **numbered** — name and *when to use it*, one
line each, no full table. Pull the *When to Use* column, not *Main Focus*: it
answers "does my situation fit this lens", which is what the person is
actually deciding here — the focus label alone reads as a job title, not a
reason to pick it. The source is the catalog in
[playbook-persona.md](playbook-persona.md#2-available-persona-catalog); never a
second copy kept here. Numbering is assigned fresh each time, in catalog order
with the user's own personas following; it is a picker convenience for this
prompt, never a stored identifier — do not reuse a number from an earlier list
in the same session.

If `~/.alterego/personas/` has files, continue the same numbering into a second
short block, **Yours**, with the `description` from each frontmatter.

Close with the two ways out that are not numbered, in this order:

```markdown
Which lens for this session? Answer with a number or a name.

  1  devils-advocate         validate a decision, test a plan, find the fragile assumption
  2  requirements-analyst    refine an issue, remove ambiguity before any code
  …

Yours
  9  <name>                  <description from the frontmatter>

  0  none          the default clone (pragmatic Dev + Architect + Person)
     new <name>    a lens that is not here yet
```

- **A number, or a catalog/user name** → resolve the number against the list
  just shown, then activate it as in
  [playbook-persona.md](playbook-persona.md#b-switch-persona-for-the-session-alterego-persona-name),
  including restating the lens at the top of every reply while it is active.
- **`0`, `none`, an empty answer or "no persona"** → keep the default clone.
  This is a valid choice, not a fallback for not having decided; do not insist.
- **`new <name>` or a description of a lens that does not exist** → run the
  creation interview from
  [playbook-persona.md](playbook-persona.md#f-create-your-own-persona-alterego-persona-new-name)
  and activate the result.

**Ask once.** No answer, or an answer that skips the question and goes straight to
a task, means `none`: open the session with the default clone, say so in the same
line, and do the task. Asking twice turns a ten-second opening into a form.

---

## 3. Confirm and get out of the way

Close with the session state in at most three lines, then stop. `start`
configures; it does not organize the day, read the repository or propose work —
that is `daily`, and it is the user's call whether it comes next.

```markdown
Session open. Guardrails: **on** (confirmation per action, diff before writing).
Lens: **appsec** — where uncontrolled data gets in, IDOR and abuse surfaces.
To swap the lens: `/alterego persona <name>`. To go back to the clone: `/alterego persona reset`.
```

Without the skill in the environment, the first line states what actually holds:

```markdown
Session open. `guardrails` is not installed — what applies is this skill's own
limits: commit, push and external actions each need their own yes.
```

---

## 4. Running it twice

`start` in a session that already has it does not reset anything silently. Show
the current state and ask what to change — the lens, the guardrails or nothing.
A user who types `start` again usually wants to swap the lens, and the shortcut
for that is `/alterego persona <name>`; say so.
