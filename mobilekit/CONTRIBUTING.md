# Contributing

This repo is the skill, not an app built with it. Prompts are the product.

## Layout

```
SKILL.md            frontmatter + the phase model. The entry point for Claude Code.
AGENTS.md           the entry point for every other agent. Points at SKILL.md.
workflow/           one file per phase — the engine. init, discovery, design, plan,
                    next, build, ship, status.
prompts/            the library. RULES.md + one folder per phase.
commands/           three-line slash-command aliases for workflow/ files.
docs/               documentation for humans, not for the agent.
install.sh          symlinks the skill into the agents on this machine.
```

Two invariants:

1. **`prompts/RULES.md` is the single source of truth** for how prompts are run. Nothing restates it — `SKILL.md`, `AGENTS.md` and the README all point at it. A copied rule drifts.
2. **Filenames in `prompts/` are the ids.** A prompt keeps its name wherever it moves, because `BUILD-PLAN.md` entries and the cross-references between prompts are filenames. Renaming one is a breaking change; moving one between folders is free.

## Adding a prompt

Put it in the folder matching its phase, add a row to `prompts/README.md`, and add it to the `SKILL.md` index table. If it changes the recommended order, update the build order in `prompts/README.md` too.

### The required shape

````markdown
# Title

One to three lines: when this applies, when to skip it, and what it costs if skipped.
Prereqs line, if any: accounts, a server, a physical device, another prompt.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

One sentence stating the task.

### Grill

3–7 questions, one per bullet, each a decision the developer owns. Where there are
named alternatives, lay them out as **A / B / C** with one line each and mark one
"Recommended default:" with the reason.

### Build

Bolded sub-headings grouping the work. Prose and bullets.

### Done when

- [ ] 5–7 items, each verifiable by running something on a real device or build
````

### The rules that make a prompt good

**Name the failure mode.** This is the whole difference between a prompt worth reading and generic advice. One concrete consequence beats three sentences of guidance:

> A resizing button on submit is a visible jump.
> A table with per-user data and no policy is a data leak, not a TODO.
> An alert with no next step gets muted within two weeks.

**A question is a decision, never a fact.** Anything the agent can read — the installed version, the folder layout, which tables exist — is looked up. `RULES.md` §1 makes this binding; a Grill block that asks for a fact wastes the developer's attention on something free.

**No code, no snippets, no version-specific setup.** The prompt states the concern; the agent resolves the API against the installed version. Where a library's setup matters, one line pointing at `RULES.md` §3 and at most the canonical docs URL, in the form `(RULES.md §3 · canonical: <url>)`. Never name a version. A snippet in a prompt is a snippet that is wrong within a year.

**Every `Done when` item is runnable.** "Accessibility is good" is not a checklist item. "The full core journey completed using only a screen reader, on both platforms" is. If an item cannot be run, it does not belong in the checklist — put it in `Build` as a requirement.

**Cross-reference by filename**, in backticks, and only to prompts that exist.

**45–75 lines.** Longer means you are explaining rather than instructing. A multi-scenario prompt may go further — `domain-model.md` and `legacy-modernization.md` are the precedents — but it earns that with `## Scenario A/B/C/D` sections, not with prose.

**Prompt the positive.** State the target behaviour rather than banning its opposite; a prohibition drags the forbidden behaviour into context and makes it more available, not less. Where a hard guardrail genuinely needs stating, pair it with the target.

### Adding a vertical

The library covers content, productivity and SaaS-style apps. Maps and geofencing, Bluetooth, health platforms, media streaming, cart-based commerce, widgets and Live Activities, and advertising SDKs each need their own prompt and are all welcome. A vertical usually needs three things the existing library does not carry: its permission story (extend `native-permissions.md` rather than duplicating it), its background-execution story, and its store-review implications (add to `store-compliance.md`).

## Adding a phase

Rare, and it costs the reader. A phase earns its place when it has a distinct prerequisite and a distinct output document. Add `workflow/<phase>.md`, a three-line `commands/<phase>.md` alias, a row in the `SKILL.md` phase table, and a row in the README's command table.

## Changing the rules

`prompts/RULES.md` changes the behaviour of all 59 prompts at once. Say in the commit body which failure the change prevents, and check that no prompt now contradicts it.

## Testing a change

There is no test suite; the artefact is prose an agent executes. Verify by running it:

1. `install.sh --check` — the links are intact.
2. Run the changed prompt end to end on a real project, in a fresh session, and watch for the two failure modes that matter: the agent asking for something it could have looked up, and the agent ticking a box it did not test.
3. Confirm no cross-reference is broken:

```bash
grep -ohE '`[a-z][a-z-]+\.md`' prompts/*/*.md | tr -d '`' | sort -u \
  | while read f; do [ -n "$(find prompts -name "$f")" ] || echo "broken: $f"; done
```

## Commits

Conventional Commits, imperative subject, one logical change per commit. The body explains **why** — which failure the change prevents — not what the diff already shows.

```
feat(prompts): add native-permissions

Camera, photos and location permissions were handled inline by three
prompts, each inventing its own denial path. A permanently-denied
permission has no recovery except the OS settings screen, and none of
the three reached it.
```
