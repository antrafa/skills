# Setup and Sync

Invoked as `/mentat setup` and `/mentat sync`. The mechanics live in two
scripts: `scripts/setup.py` wires this machine, and `scripts/vault.py sync`
shares the vault through git. Your part is the consent and the judgment around
them.

- [Setup](#setup) · [Absorb](#absorb) · [Uninstall](#uninstall) · [Sync](#sync) · [Choosing what syncs](#choosing-what-syncs) · [Resolving a stopped sync](#resolving-a-stopped-sync)

---

## Setup

Make this machine's agents share one memory.

1. **Ask about the memory, first.** "Do you want Mentat as the main memory? For
   which of these agents?" — name the installed ones. Mentat as main memory
   means a pointer block in that agent's global instructions and absorbing what
   it remembered on its own. An agent left out keeps its own memory and still
   gets the skill to consult. Map the answer to `--agents`: `all`, `none`, or
   keys from `claude,codex,antigravity,opencode`. Never assume `all` from
   silence; ask.
2. **Plan.** Run `scripts/setup.py --dry-run --agents <answer>` and show the plan as it prints it.
   It edits other agents' global instruction files and may install a timer, so
   the person should see every target before anything changes.
3. **Ask about sharing, once.** If the plan notes `sync off`, ask whether they
   want the vault in a private git repository so other machines can share it.
   Yes → ask for the URL of a repository they already created; you never create
   one on their behalf. No → carry on. Mentat works fully on one machine.
   Yes → also ask which topics may leave this machine, and run
   [Choosing what syncs](#choosing-what-syncs) before the first sync.
4. **Run** on an explicit yes: `scripts/setup.py --agents <answer>`, with `--remote <url>` if they
   gave one and `--no-timer` if they want to sync only on request. Re-running is
   safe: a second run only fixes what drifted.
5. **Absorb.** If the closing inventory lists native memory files, offer
   [Absorb](#absorb). It lists only the chosen agents.

What setup does, so you can explain it: clone or create the vault, install the
merge rules, add a short pointer block (between `<!-- mentat:start -->` and
`<!-- mentat:end -->`) to each chosen agent's global instructions, link the
skill where it is missing or its link is broken, and schedule `vault.py sync`
every 30 minutes when there is a remote.

Completion: the memory question answered, the plan shown and approved, setup ran and printed its steps,
and the native memory inventory was either absorbed or explicitly left for later.

## Absorb

Bring what an agent remembered on its own into the vault, so there is one
memory instead of two that drift apart.

1. **Inventory.** Read every file setup counted. For each fact, run
   `vault.py search` and classify it: **new**, **duplicate** (the vault already
   has it — name the entry), or **trivia** (reconstructible from the repo, or
   stale).
2. **Show** the inventory grouped by those three, one line per fact, and wait.
   Nothing is written before a yes; the person may move items between groups.
3. **Write** the approved new facts through [Remember](../SKILL.md#remember),
   and fold duplicates that add detail through [Amend](../SKILL.md#amend).
4. **Redirect**, with a separate yes: copy each absorbed project's `MEMORY.md`
   to `MEMORY.md.pre-mentat` — Uninstall restores it from there — then replace
   its contents with the pointer below. Leave the topic files where they are;
   deleting them is the person's call, never yours.

   ```markdown
   There is no separate memory layer here: memory lives in the Mentat vault at ~/.mentat.
   Recall from it through the `mentat` skill, and write anything durable there, never here.
   ```

A later setup run counts any file an agent wrote since, so absorbing again is
how drift gets caught.

Completion: every counted file classified, approved facts written, and each
redirect done or declined.

## Uninstall

Stop using Mentat as the main memory, for every agent or only some.

1. **Plan.** `scripts/setup.py --uninstall --dry-run`, adding `--agents <keys>`
   to undo only those agents. Show it.
2. **Run** on a yes, without `--dry-run`. It removes the pointer blocks, restores
   every `MEMORY.md.pre-mentat`, and removes the sync timer only when no
   `--agents` was given.

The vault, its repository and the skill links stay. Deleting memory is
[Forget](OPERATIONS.md#forget), and only on request.

Completion: blocks removed and backups restored as planned, the person told the
vault is intact.

## Sync

`scripts/vault.py sync` commits local changes, merges the remote, reconciles the
indexes and pushes. The timer runs it on its own; run it by hand when the person
asks, or before reading the vault on a machine that may be behind.

It does nothing, and says why, when the vault is not a git repository, has no
remote, or its branch has no upstream. That is a supported setup, not an error:
relay the message and offer [Setup](#setup) with a remote.

What merges on its own: index, MOC and daily bullets from both sides; entry
counters by rule (stronger salience, uses from both sides, latest dates, union of
`related`). One gap: when two machines leave an entry byte-identical (the same
single touch on the same day), git never calls the rule and that use counts
once. What stops: a body, `profile.md` or `core-memory.md` edited
differently on two machines, or an entry archived on one and changed on the
other.

Completion: `sync ok`, a `sync off` reason relayed, or a stop handled below.

## Choosing what syncs

`sync-topics` at the vault root decides which entries leave the machine.
Without it, every entry syncs. With it, an entry syncs only when its `project`
or one of its tags matches a line, and no `!` line matches; everything else
stays local. Unmatched means local on purpose: forgetting to allow a topic
costs one sync, while a client's name on a personal GitHub cannot be taken back.

```text
# Topics that sync; every other entry stays on this machine.
# A line matches a project or a tag; * is a wildcard; ! keeps matches local.
lang/*
pattern/*
estudos
!cliente/*
```

1. **Ask** which subjects are fine on the remote, and which must never go
   (clients, employer systems). Show `vault.py tags` so the answer uses the
   vault's own vocabulary.
2. **Write** the file from the answer and run `vault.py topics`. It lists every
   entry as `syncs` or `local` and changes nothing. Show it and adjust until the
   person agrees with the split.
3. **Sync** on a yes. A topic that was shared before is removed from the
   remote's current files and kept on disk here and on the other machines.
4. **Say what is still out there.** Removing a file from the remote does not
   remove it from the repository's history. Clearing that means rewriting the
   history and force-pushing, which is destructive and a separate decision:
   offer it, never run it on your own.

What stays local is more than the entry file. Its index bullets, its slug in
the `related` lists, and every link to it are left out of what gets
committed. A link in a shared entry's body reaches the remote as the text
`local entry`. This machine keeps the full text: sync sets it aside in
`.git/mentat-local` before committing and merges it back after pushing. A
pre-commit hook refuses any commit that carries a local entry, so a commit
made by hand, or by an editor plugin, cannot leak one. `profile.md` and
`core-memory.md` always sync. Keep client details out of them.

Each sync applies the stricter of this machine's file and the remote's.
Withdrawing a topic takes effect on the next sync everywhere. Allowing a new
one takes two syncs, because it only counts once the remote has the new file.

## Resolving a stopped sync

The vault is left mid-merge with the listed files conflicted; the timer will not
run again until it is settled.

1. **Read** each conflicted file and its two versions — both are real memory.
2. **Propose** the merged text: keep every fact from both sides, and when they
   genuinely disagree, ask which is current rather than picking one.
3. **Settle** on a yes: write the file, `git -C ~/.mentat add <file>`, then
   `git -C ~/.mentat commit --no-edit`, then run `vault.py sync` again. Lines of
   local entries are missing from the files until that sync puts them back, so
   do not re-add them by hand.

An entry archived on one machine and touched on the other: keep the touched
version in `entries/` and delete the archived copy, since being used is the
signal that it should not have faded.

Completion: no conflicted files, `sync ok` printed.
