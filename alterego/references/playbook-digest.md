# Playbook: Visual Digest of a Technical Document (`/alterego digest`)

A dense AI-generated document — SDD, ADR, implementation plan, spec, RFC, MR
description — gets approved on sight with dangerous frequency. This playbook
exists so that the decision to go ahead with the document is a conscious one:
the developer understands what changes, what does **not** change and where the
AI assumed, in 30 to 60 seconds.

---

## Invocation modes

```
/alterego digest <doc-path>              (digest in markdown, in the chat)
/alterego digest <path> --html           (standalone page in docs/digests/)
/alterego digest                         (assumes the obvious doc from context)
```

In Codex:
```
$alterego digest <doc-path>
```

**No target does not turn into a generic question.** Assume the obvious document
from context — the plan just saved in `docs/superpowers/plans/`, the ADR under
discussion, the open file — and **say which one you assumed**. Only ask when
there is no context at all.

---

## 1. Resolve the `doc-digest` skill before starting

The digest is a capability of the partner skill `doc-digest`; alterego routes,
it does not reimplement. Detect it and follow the rule in
[sources.md](sources.md#missing-catalog-skill-degrade-deliver-offer).

**Installed:** invoke it with the resolved target (the `Skill` tool when it
exists) and pass `--html` along when the user asks for it. The output contract
is the skill's; do not duplicate the template here or rewrite the result.

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
2. **TL;DR in up to 3 lines** — the decision the document asks for, not what it
   describes.
3. **One Mermaid diagram** of the flow, architecture or sequence, contrasting
   what exists today with what comes to exist.
4. **Decision matrix:** what changes | what does **not** change (protected
   scope) | why | where in the doc (`file:line`).
5. **Anti-Vibe-Coding box:** premise the AI assumed without the document
   backing it, the most fragile dependency, what can break in production. An
   absence becomes a declared gap, never a filled-in assumption.
6. **Quick-lookup index:** section → line in the original, so the dev can go
   back to the exact spot.

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
