# Playbook: Visual Digest of a Technical Document (`/alterego digest`)

A dense AI-generated text — SDD, ADR, implementation plan, spec, RFC, MR
description, a long agent reply or concept round — gets approved on sight
with dangerous frequency. This playbook
exists so that the decision to go ahead with the document is a conscious one:
the developer understands what changes, what does **not** change and where the
AI assumed, in 30 to 60 seconds.

---

## Invocation modes

```
/alterego digest <doc-path>                  (digest in markdown, in the chat)
/alterego digest <path> --html               (also a standalone page, next to the markdown)
/alterego digest <path> --since <previous>   (only what changed since the previous round)
/alterego digest                             (assumes the obvious doc or reply from context)
```

In Codex:
```
$alterego digest <doc-path>
```

**No target does not turn into a generic question.** Assume the obvious document
from context — the plan just saved in `docs/superpowers/plans/`, the ADR under
discussion, the open file, the agent's last long reply — and **say which one
you assumed**. Only ask when
there is no context at all.

---

## 1. Resolve the `doc-digest` skill before starting

The digest is a capability of the partner skill `doc-digest`; alterego routes,
it does not reimplement. Detect it and follow the rule in
[sources.md](sources.md#missing-catalog-skill-degrade-deliver-offer).

**Installed:** invoke it with the resolved target (the `Skill` tool when it
exists) and pass `--html` along when the user asks for it. The output contract
is the skill's; do not duplicate the template here or rewrite the result.
`--since` goes along too, as does a request phrased as "what changed since
the last round".

**Not installed:** produce the degraded digest from section 2 **in the same
reply** and only then offer the installation, once per session:

> `doc-digest` is not installed in this environment — I'll do the digest inline,
> without the HTML page. If you want to equip the environment, it's
> `git clone <your-repository>/doc-digest.git` plus the symlink; I'll show the
> exact command before running it.

Declined? Do not repeat the offer in the session. `--html` without the skill is
not delivered by hand: say that HTML mode depends on it and deliver the
markdown.

---

## 2. Degraded digest (without the skill)

Same discipline, lean format, straight in the chat:

1. **Read the whole document.** Never digest from an excerpt or the summary. A
   large document is read in parts; it is not sampled.
2. **Bottom line first, in one sentence:** what the text asks you to accept
   and its single most damaging problem. Then a **TL;DR in up to 3 lines**.
3. **One Mermaid diagram** answering the reader's question: the flow or
   architecture contrasting what exists today with what comes to exist, or a
   mind map of decided, open and discarded for a concept round.
4. **Decision matrix:** what changes | what does **not** change (protected
   scope) | why | where in the doc (`file:line`).
5. **Anti-Vibe-Coding box:** premise the AI assumed without the document
   backing it, the most fragile dependency, what can break in production. An
   absence becomes a declared gap, never a filled-in assumption.
6. **Your move:** what the text waits on from the dev (approve, choose,
   answer), and up to 3 questions that resolve the box, each one standing
   alone so it can be pasted straight back to the agent.
7. **Quick-lookup index**, only for 100 lines or more: section → line in the
   original, so the dev can go back to the exact spot.

**Delta (`--since`):** replace the matrix with a table of what was decided
now, changed, reopened or vanished since the previous round. An open question
that vanished without an answer goes first in the box and in Your move.

Stop there. A digest that takes more than 60 seconds to read has failed its
purpose — table and diagram in place of paragraphs.

---

## 3. Stance

- **A digest approves nothing.** It informs the user's decision; the
  authorization to go ahead with the plan is still theirs.
- **Never invent what the document does not say.** A gap is declared in the
  anti-vibe-coding box.
- **Same language as the original document.**
- **Do not rewrite the document.** A digest is reading, not editing: changing
  the original is another request, with another authorization.
- **No `--html` on your own initiative.** A standalone page only when asked.

---

## 4. Where it comes in on its own

Beyond direct invocation, the digest is offered at the end of **steps 1 and 2**
of the Dev Pipeline — before the plan becomes code. See
[playbook-dev.md](playbook-dev.md#anti-vibe-coding-visual-digest-doc-digest-in-steps-1-and-2).
