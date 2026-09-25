# Playbook: Writing and Reviewing Skills (`/alterego skill`)

A document an agent reads — `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, a reference
reached through a pointer — is not written like documentation for people. The
target is not the right answer in one round: it is the agent following **the
same process** in every round.

The writing criteria belong to the `writing-for-agents` skill; alterego routes
and conducts the ritual, it does not reimplement the bar.

---

## Invocation modes

```
/alterego skill <path>          (reviews an existing skill, AGENTS.md or agent doc)
/alterego skill new <name>      (writes a skill from scratch)
/alterego skill                 (assumes the obvious target from context)
```

In Codex: `$alterego skill <path>`.

**No target does not turn into a generic question.** Assume the obvious from
context — the current repository's `SKILL.md`, the open file, the skill under
discussion — and say which one you assumed.

---

## 1. Resolve `writing-for-agents` before starting

It is a skill by Matt Pocock
([github.com/mattpocock/skills](https://github.com/mattpocock/skills)), not part
of the harness. Detect it and follow the rule in
[sources.md](sources.md#missing-catalog-skill-degrade-deliver-offer):

- **Claude Code:** installed as a plugin, it shows up in the `Skill` tool's list
  as `writing-for-agents` or `mattpocock-skills:writing-for-agents`; that list
  decides, not `ls`.
- **Other harnesses:** the directory loop in
  [sources.md](sources.md#missing-catalog-skill-degrade-deliver-offer).

**Installed:** invoke it (the `Skill` tool when it exists) and work with its bar.
When the target is a skill — frontmatter, invocation choice, router skill — it
tells you to read its `SKILL-MECHANICS.md` as well.

**Not installed:** work through the levels in section 3 in the same response and
offer the installation at the end, once per session, with the link and the
command for the harness in use (Claude Code: `/plugin install mattpocock-skills`;
others: `npx skills@latest add mattpocock/skills`), as in
[onboarding.md](onboarding.md#third-party-skills-and-plugins). A missing skill
is never a blocker.

---

## 2. Two branches

**Reviewing an existing document** is the common case. Read the whole document
before proposing any cut — including the references it points to, because
duplication only shows up when you see both sides. Diagnose in the order of
section 3, propose, and only then edit.

**Writing from scratch** starts with two questions, in this order:

1. **Who invokes it?** If only the human types the name, the skill is
   *user-invoked* (`disable-model-invocation: true`) and pays no context load at
   all. A description with a list of triggers is only justified when the agent —
   or another skill — needs to reach it on its own.
2. **What is a step and what is a reference?** A step is what the agent does, in
   order. A reference is what it consults on demand. Whatever only some branches
   reach leaves the main file and becomes a pointer.

Start smaller than seems necessary. An agent document fattens on its own; it
does not slim down on its own.

---

## 3. Order of attack for the diagnosis

From the biggest lever to the smallest. Stop when the cost of continuing
exceeds the gain.

1. **The pointer.** The skill's `description`, or the `AGENTS.md` line that names
   the document, costs on **every** turn of **every** session. It is where a cut
   pays the most. Trigger in the first word; one trigger per branch, no synonym
   renaming the same one; out with the identity the body already carries.
2. **Duplicated meaning.** The same rule written in two places costs maintenance,
   costs tokens and inflates its apparent importance. One source of truth; the
   other spots cite it. The environment (`package.json`, config, directory
   layout) is also a source of truth: a document that repeats it is a cache, and
   a cache only pays off when the lookup is expensive.
3. **Hierarchy.** What is inline and only some branches reach should be behind a
   pointer. What is behind a pointer and every branch needs should be inline.
   Material on the same concept scattered across the file goes back under a
   single heading.
4. **Completion criterion.** Each step ends in a condition that says *done*. Too
   vague ("understanding reached") and the agent wraps up early, its attention
   already on the following steps. Sharpen the criterion first; splitting the
   sequence is the next resort, not the first.
5. **Leading word and negation.** A triad repeated in three places wants to
   become a single token. And a prohibition pushes the prohibited thing into the
   context — prefer naming the target behavior. A hard guardrail survives,
   accompanied by the positive.
6. **No-op and sprawl.** A sentence the model already obeys by default pays load
   to say nothing: delete the whole sentence, do not trim the words. A document
   that is too long dilutes attention even with every line alive.

---

## 4. Limits

A skill usually lives **outside the project** (`~/.claude/skills/`,
`~/.agents/skills/`, the harness config directory). Editing there is a change
outside the current repository: *Autonomy and limits* from `SKILL.md` applies,
so show the target before writing when the path leaves the project the
conversation is in.

- **Touching the bar is not touching the behavior.** Refactoring the wording
  and changing what the skill tells the agent to do are two diffs, never the
  same one.
- **The document keeps its language.** A skill in English stays in English.
- **A proposed cut justifies itself.** "This is a no-op" is a claim about the
  model's default behavior, and it is settled by running the document, not by
  arguing. When in doubt, keep it and record the doubt.

---

## Closing checklist

- [ ] Was the pointer (description or index line) reviewed before the body?
- [ ] Does each rule have a single source of truth, with the other citations pointing to it?
- [ ] Did whatever only some branches reach leave the main file?
- [ ] Does every step have a completion criterion that distinguishes done from not done?
- [ ] Was every prohibition that could become a target behavior converted?
- [ ] Do the internal links and anchors still resolve after the cuts?
- [ ] Were the wording refactor and the behavior change kept in separate diffs?
