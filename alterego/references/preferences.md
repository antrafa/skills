# Preferences — what the user chooses once

Three behaviors are a matter of taste or of company policy, not of good
practice, so the user picks them instead of the skill imposing them. They are
asked once, on the first invocation ever, and live in
`~/.alterego/preferences.md`.

That file is machine configuration for this skill, not part of who the user
is: it stays in `~/.alterego/` even when Mentat holds the profile, and the
shadow-profile rule in `SKILL.md` does not apply to it.

## The file

```markdown
# Alterego preferences
guardrails: on
review-editor: none
ai-attribution: off
```

| Key | Values | Default | What it changes |
|---|---|---|---|
| `guardrails` | `on` \| `off` | `on` | `on`: every session opening invokes the `guardrails` skill ([playbook-start.md](playbook-start.md#1-arm-the-guardrails)). `off`: the session opens without it, and this skill's own *Autonomy and limits* still hold |
| `review-editor` | `vscode` \| `intellij` \| `none` | `none` | Where a change ready for review is opened before the commit is proposed. `vscode` runs `code -n <paths>`, `intellij` runs `idea <paths>`; if the binary is not on `PATH`, say so in one line and fall back to `none`. `none`: show `git diff --stat` with the commit proposal |
| `ai-attribution` | `off` \| `harness` | `off` | `off`: commits, PRs and deliverables carry no co-authorship and no mention of AI. `harness`: follow whatever the harness or the project configures; the skill neither adds nor removes attribution |

## Reading it

The first alterego invocation in a session reads the file, in parallel with
whatever else that invocation runs (the report lookup, on an opening). Later
invocations in the same session reuse what was read.

## First invocation: the file does not exist

1. Apply the defaults for this turn and do what was asked — the questions
   never block the work.
2. Write the file with the defaults in the same turn, so the questions are
   asked only once even if nobody answers.
3. Close the reply with the questions, as its last lines:

```markdown
First time here — three choices, saved in `~/.alterego/preferences.md` (defaults already applied):
1. Arm `guardrails` at every session opening? **on** / off
2. Open changes for review in: vscode / intellij / **none** (just the `git diff --stat`)
3. Commits and PRs without any mention of AI? **yes** / no (follow the harness)
```

An answer, even partial (`1 off, 2 vscode`), rewrites the file with what was
given and keeps the defaults for the rest; say which file changed. Silence or a
new task keeps the defaults already written.

## Changing it later

`/alterego setup` shows the current values and offers to change them, and
`start` run twice offers it too. The user can also edit the file by hand; the
next session reads it.
