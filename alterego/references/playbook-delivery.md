# Playbook: Commit and MR/PR Description (`/alterego commit`, `/alterego pr-desc`)

The two most written texts of the workday, and the two that come out worst when
written in a hurry. The persona writes in the user's voice, from the real diff,
and **stops before committing or posting**: writing authorizes writing, not
sending.

---

## Invocation modes

```
/alterego commit [<scope>]         (message for what is staged; nothing staged, for the working tree)
/alterego pr-desc [<iid>|<branch>] (MR/PR description for the current branch, or the one given)
```

In Codex: `$alterego commit`, `$alterego pr-desc`.

---

## 1. `commit`

1. **Read the diff, not the user's summary.** `git status`, `git diff --staged`
   (or `git diff` when nothing is staged). The message describes what the diff
   does; if the diff and the request diverge, say so.
2. **One logical intent per commit.** If the diff mixes refactoring with
   functionality, formatting with logic, infrastructure with business rules,
   propose the split with the files of each part before writing any message. A
   subject that needs an "and" is a sign of two commits. **The refactor comes
   first, the behavior after** — *make the change easy, then make the easy
   change* (Kent Beck): in that order the first commit is provably
   behavior-neutral and the second is small enough to read.
3. **Write in the format:**

   ```
   <type>(<scope>): <description in the imperative, lowercase, no period, up to 72 characters>

   <body: the why, in one or two sentences; never repeats the diff or lists files>

   Refs #123
   ```

   Types: `feat` `fix` `refactor` `perf` `style` `docs` `chore` `revert`.
   The scope is the module or area a `git log` reader recognizes. Body only when
   the why is not obvious from the subject. Footer when there is an issue.
4. **A breaking change is marked, never described in prose.** Conventional
   Commits carries it in two places, and release tooling reads both: a `!`
   before the colon (`feat(api)!: ...`) and a `BREAKING CHANGE: <what breaks and
   what the consumer has to do>` footer. This is not cosmetic — under SemVer the
   type is what picks the bump (`fix` -> patch, `feat` -> minor, breaking ->
   major), so a breaking change hidden in the body ships as a minor and breaks
   whoever trusted the version number. If the diff removes a field, changes a
   signature, renames an env var or alters an event's payload, the mark goes in.
5. **Follow the local convention if there is one.** If the repository's recent
   `git log` uses another format, ticket prefix or language, it wins over this
   playbook, and you say which one you followed.
6. **Show the message and stop.** The `git commit` command only goes out with a
   "yes" for it, under the authorship rule in *Autonomy and limits* of `SKILL.md`.

## 2. `pr-desc`

1. **Ground it in evidence:** `git log <base>..HEAD`, `git diff <base>...HEAD --stat`,
   the whole diff when it fits. The base is the MR's target branch; if it is not
   clear, ask once.
2. **Title** in the same format as the commit: `<type>(<scope>): <description>`.
3. **Description in four blocks**, in the order the reviewer reads:

   ```
   ## What changed
   <enough to review without opening the diff blind; grouped by intent, not by file>

   ## Why
   <the problem that existed before; link to the issue or incident when there is one>

   ## How to validate
   1. <concrete step someone runs>
   2. <expected result>

   ## Out of scope and side effects
   - <what was noticed and not touched, and why>
   - <who else is affected without having asked for the change: consumer, chart, migration, env var>
   ```

   An empty block does not appear, except "How to validate", which always does:
   without a validation step there is no way to review.
4. **Does the user have an MR template in the repository?** (`.gitlab/merge_request_templates/`,
   `.github/pull_request_template.md`) It wins; fill the template with this
   content instead of imposing the four blocks.
5. **Show and stop.** Opening the MR, editing the description on the remote or
   posting are external actions: only with a "yes" for each one, with the exact
   text in front of the user.

---

## Closing checklist
- [ ] Was the message written from the real diff, and was any divergence from the request stated?
- [ ] Does the diff have a single intent, or was the split proposed before the message, refactor first?
- [ ] If something breaks for a consumer, does the message carry the `!` and the `BREAKING CHANGE` footer?
- [ ] Was the local `git log` convention or MR template respected when it existed?
- [ ] Does "How to validate" have an executable step and an expected result?
- [ ] Was nothing committed, opened or posted without the "yes" for that action?
