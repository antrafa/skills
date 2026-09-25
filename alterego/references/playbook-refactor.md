# Playbook: Structural Refactoring (`/alterego refactor`)

A refactor that compiles only at the end is not a refactor, it is a rewrite with
hope. This playbook governs the change that is too big for one green step:
extracting a module, inverting a dependency, swapping a framework underneath a
flow, splitting a class the whole system leans on.

The discipline comes from the **Mikado Method** (Ola Ellnestam and Daniel
Brolund) — the change is discovered by attempting it and reverting, never by
designing the graph from the armchair.

---

## Invocation modes

```
/alterego refactor <goal>        (drives the full Mikado cycle toward that goal)
/alterego refactor               (assumes the refactor under discussion; asks once if there is no context)
```

In Codex: `$alterego refactor <goal>`.

---

## 0. Does this deserve Mikado?

Mikado costs a graph and several commits. It pays off when the naive attempt
breaks things **outside the file being changed**. Before starting:

- **The change fits in one green step?** Do it and stop. A Mikado graph for a
  two-file rename is ceremony.
- **Is there a safety net?** If the target has no test that fails when the
  behavior changes, the first prerequisite is a **characterization test**
  (Michael Feathers): it records what the code *does today*, not what it should
  do — including the bug, if there is one. Without it, there is no way to tell
  refactoring from breaking.
- **Is the goal verifiable?** "Improve the billing module" is not a goal.
  "`OrderService` no longer imports anything from `infra.oracle`" is.

---

## 1. The cycle

```
[Goal at the top of the graph]
         │
         ▼
[Naive attempt] ──────► change it the simplest way, on a clean tree
         │
         ▼
[Collect the breakage] ► compilation, red test, runtime error — each one is a node
         │
         ▼
[REVERT] ─────────────► git checkout/restore; the tree goes back to green
         │
         ▼
[Recurse on each leaf] ► a leaf that needs nothing else is done and committed
         │
         ▼
[Goal, last] ─────────► now the naive attempt passes on the first try
```

### The four non-negotiable rules

1. **Reverting is the method, not a defeat.** The naive attempt exists to
   *reveal* prerequisites, not to be saved. Keeping a half-done attempt on disk
   destroys the property that makes this work: every commit is green.
2. **Never build on a red tree.** If the suite is red, the only allowed work is
   making it green. A prerequisite discovered on top of broken state is noise.
3. **Leaves first, the goal last.** Each leaf is an independent `refactor:`
   commit, releasable on its own, that changes no behavior. The goal is the only
   commit that changes behavior — Kent Beck's *make the change easy, then make
   the easy change*, with the graph deciding what "easy" requires.
4. **The graph is written down, not remembered.** A Mikado session spans days
   and context windows; a graph living only in the chat dies at the first
   `/clear`.

---

## 2. The graph on disk

Save it at `docs/refactor/<slug>-mikado.md` and update it **on every commit**,
so an interrupted session can be picked up without replaying the history:

```markdown
# Mikado: <goal in one verifiable sentence>

Started: <YYYY-MM-DD> · Naive attempt: <command or diff that was tried>

- [ ] **Goal:** OrderService no longer imports infra.oracle
  - [x] Extract the OrderRepository interface — `refactor(order): ...` (a1b2c3d)
  - [ ] Move the Oracle mapping into the infra adapter
    - [x] Characterization test for the legacy mapping — (e4f5g6h)
    - [ ] Remove the direct dependency in the scheduler
```

Mermaid is optional and only pays off past about ten nodes; the checklist is
what gets updated. A checked node carries its commit sha — that is the evidence
the step is green and integrated.

---

## 3. Conducting it with the user

- **Announce each revert before running it.** `git restore`/`git checkout` on a
  dirty tree destroys work. Show what will be discarded and confirm — this is
  the destructive action of the method and it is not covered by a generic "go
  ahead".
- **Work in a worktree**, per step 3 of [playbook-dev.md](playbook-dev.md).
  Mikado on a branch shared with someone else turns their day into a rebase.
- **Report state in one line per interaction:** which node is open, how many
  leaves are left, whether the tree is green.
- **Stopping midway is legitimate and safe** — every leaf already committed is
  a standalone improvement. Say so explicitly when handing back: a graph with
  the goal still open is not an unfinished delivery, it is a smaller delivery.

---

## 4. Relation to the other commands

| Situation | Where it goes |
|---|---|
| The refactor is part of a feature being built | [playbook-dev.md](playbook-dev.md), and Mikado enters at step 4 |
| The change is structural and has more than one viable design | [playbook-decision.md](playbook-decision.md) first; Mikado executes what was decided |
| The target has no test and behavior is unknown | characterization test as the first leaf, before any node |
| Someone else's diff mixes refactor with feature | [playbook-review.md](playbook-review.md), finding of scope |

---

## Closing checklist
- [ ] Is the goal stated in one verifiable sentence, not an adjective?
- [ ] Did the target have a safety net, or was a characterization test the first leaf?
- [ ] Was every naive attempt reverted, with the discard announced first?
- [ ] Is every commit green and releasable on its own, with the graph updated and the sha recorded?
- [ ] Does the goal commit contain the behavior change, and the leaves none?
