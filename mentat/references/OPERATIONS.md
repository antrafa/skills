# Vault Maintenance Operations

Invoked as `/mentat {operation}`. For Remember, Recall, Load, Profile, Review,
Status and Amend, see [SKILL.md](../SKILL.md).

Groom, Restore, Status and Audit are implemented by `scripts/vault.py` — run it
rather than walking the vault by hand. The rest need judgment and are described as
procedures.

- [Groom](#groom) · [Restore](#restore) · [Audit](#audit) — scripted
- [Consolidate](#consolidate) · [Merge](#merge) · [Split](#split) · [Forget](#forget) — judgment
- [Export](#export) · [Import](#import) — backup

---

## Groom

Fade idle transient memory.

```bash
scripts/vault.py groom --dry-run   # preview
scripts/vault.py groom
```

For each fadeable entry the script computes how many days it sat unused — measured
from whichever came later, the last access or the last decay pass — and applies
exponential decay from there. Entries that fall to the archive threshold move to
`~/.mentat/archive/` with their MOC, daily-note and index references removed. The
file itself is kept, so archiving is recoverable. Permanent types are skipped
entirely.

**Why the script owns this.** Anchoring decay on `decayed_at` is what makes Groom
cadence-insensitive. Decaying from `last_accessed` alone re-applies the same idle
window on every run: an entry groomed daily for two weeks lost 88% of its salience
while the same entry groomed once on day 14 lost 25%. Running maintenance more
often would delete the vault faster. `scripts/vault.py --selfcheck` asserts that
this stays fixed.

> **Cadence:** weekly, or whenever the vault passes ~100 entries. Since results no
> longer depend on frequency, running it more often is harmless.

Completion: script run and its summary reported. Anything archived named to the
user — naming it is what makes [Restore](#restore) possible later, since the
archive is invisible to recall unless it is asked for.

## Restore

Bring an archived entry back into the working set.

```bash
scripts/vault.py search <terms> --include-archived   # find it
scripts/vault.py restore <slug>                      # bring it back
```

Groom archives rather than deletes so that fading stays reversible, but an
archived entry is out of recall's reach until this puts it back: it is re-indexed
into its MOC, `index.md` and its original daily note. It also returns at full
salience with the idle clock reset — restoring at the value it faded to would just
hand it to the next Groom.

What the script cannot decide is whether it should come back. An entry archived
once and restored twice is telling you its type was wrong: a `note` that keeps
proving useful is a `learning` or a `decision`, and changing the type is what
stops the cycle.

Completion: entry back in `entries/`, re-indexed, and its type reconsidered if
this is not the first time it was archived.

## Audit

Validate integrity.

```bash
scripts/vault.py audit          # report
scripts/vault.py audit --fix    # repair what is mechanical
```

Five checks: orphan entries missing from every MOC, MOC lines pointing at entries
that no longer exist, stale daily-note references, body wiki-links to deleted
entries, and frontmatter that no longer parses.

`--fix` repairs only bookkeeping damage — dropping dead references and re-indexing
orphans. The last two checks are deliberately left alone: a wiki-link to a deleted
entry might need the link removed, restored from `archive/`, or repointed
elsewhere, and only reading the surrounding text tells you which. Broken
frontmatter is the same. Fix those yourself and explain each change.

> **Cadence:** alongside Groom, and after any bulk delete or archive.

Completion: report presented. If `--fix` ran, say what it changed. Judgment-call
findings resolved individually or flagged to the user.

## Consolidate

Distill scattered entries into a Schema.

1. **Analyze.** Find clusters of 3+ entries sharing at least two wiki-links or
   tags. Present the candidate cluster and the pattern you think it shows, and get
   approval — a schema the user does not recognize is noise that outranks real
   entries in recall, since schemas carry double salience.
2. **Synthesize.** Write the schema with `vault.py write --type schema`, passing
   `--related` with every source entry — the script mirrors the link back onto each
   source, so they show the abstraction they fed. Keep the sources; the schema is a
   lens on them, not a replacement.

Completion: schema created with its sources listed in `related`, and the user has
confirmed the abstraction is real.

## Merge

Combine two redundant entries.

1. **Identify.** Read both fully. Redundancy has to be verified, not assumed from
   similar titles.
2. **Confirm.** Show both side by side and ask which survives (**target**) and
   which is absorbed (**source**). If the types differ, ask which type the result
   should carry — merging a `note` into a `decision` changes whether it can fade.
3. **Combine.** Fold the source's content into the target as atomic bullets. Union
   `tags` and the wiki-links in the body by hand; for `related`, pass the source's
   siblings through `vault.py relate --slug <target> --related <a>,<b>` so each one
   gets the reverse link too. Sum `usage_count`; take the higher `salience`.
   Both entries earned their strength, so nothing should be lost by merging.
4. **Relink.** Repoint every entry, MOC line and daily-note reference from source
   to target. If the combined entry now covers more than its summary says, give it
   the new one with `vault.py reindex --slug <target> --summary "..."` so all three
   indexes agree.
5. **Delete source.** Remove the file and its index lines, then run
   `vault.py audit` to confirm nothing still points at it.

Completion: source gone, target holds the combined content, audit clean.

## Split

Break a multi-topic entry into atomic ones.

1. **Analyze.** Read it and identify the distinct topics. Present the proposed
   split for approval — where the seams fall changes what each piece will be
   findable by.
2. **Create.** One entry per topic via `vault.py write`, inheriting the original's
   `tags` and `project`, cross-linked through `--related`. Each starts fresh at
   base salience: the new entries have no usage history of their own.
3. **Relink.** Repoint references to the original at whichever new entry is most
   relevant. Reading each reference is the only way to know which.
4. **Archive original.** Move it to `~/.mentat/archive/` with a note recording the
   split and linking the new entries, so the trail back is not lost —
   [Restore](#restore) brings it back if the seams turn out to be wrong.

Completion: one entry per topic, original archived with a split note, references
repointed, `vault.py audit` clean.

## Forget

Delete an entry permanently, at the user's request.

1. **Confirm.** Show title, type, creation date and summary, and ask explicitly.
   This is the one irreversible operation — Groom archives and [Restore](#restore)
   undoes that, while Forget destroys. If the user only wants it out of the way,
   suggest archiving instead.
2. **Unlink.** Remove backlinks from related entries, plus its MOC and daily-note
   lines.
3. **Delete.** Remove the file from `entries/` (or `archive/`), then run
   `vault.py audit` to catch references you missed.

Completion: file deleted, references removed, audit clean.

## Export

Back up the vault.

1. **Zip.** `zip -r ~/mentat_export_$(date +%Y%m%d).zip ~/.mentat -x "*.DS_Store"`.
   Use `~/Desktop` instead if it exists.
2. **Confirm.** Report the path and size.

Completion: archive created, location reported.

## Import

Restore from a backup.

1. **Locate.** Ask for the `.zip` path, or offer any `mentat_export_*.zip` found in
   `~/Desktop` and `~/`.
2. **Validate.** Unzip to a temporary directory and verify it contains `entries/`,
   `maps/`, `daily/` and `core-memory.md`. Abort if not — better to fail than to
   half-overwrite a working vault.
3. **Strategy.** Ask for **replace** or **merge** (import only slugs not already
   present). Before replacing, run Export first: replace discards the current vault.
4. **Apply.** In merge mode, report every slug skipped as a duplicate so the user
   can reconcile them by hand.
5. **Audit.** Run `vault.py audit --fix`. An imported vault routinely arrives with
   references to entries the merge skipped.

Completion: vault restored, skipped duplicates reported, audit run and presented.
