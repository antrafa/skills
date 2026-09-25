---
name: mentat
metadata:
  turbo_safe: false
  requires:
    - python3
description: >-
  Persistent knowledge vault at ~/.mentat that carries bugs, decisions,
  features, learnings and snippets across sessions as a linked Obsidian graph.
  Use this skill whenever the user leans on knowledge from an earlier session —
  "what was that CORS fix?", "we already decided this", "how did I solve this
  last time", "didn't I write this down?" — or asks to remember, save, note or
  jot something down, to load project context or their profile, or to check
  vault activity, health, grooming, auditing, merging or splitting entries.
  Reach for it even when the user never says "mentat" or "vault": any request
  that depends on what happened in a past session is a recall, and any durable
  fact the user hands over is worth capturing.
---

The vault lives at `~/.mentat/` and opens directly as an Obsidian vault.

**Bookkeeping belongs to `scripts/vault.py`, judgment belongs to you.** The script
handles frontmatter arithmetic, MOC and index updates, decay and integrity checks
in one call each; doing that by hand means a dozen file edits per operation and
salience math that quietly comes out wrong. Every tunable — decay rate, archive
threshold, starting salience — is defined in that script and nowhere else, so
read it rather than assuming a value. What the script cannot do is decide what
deserves remembering, how to phrase it, or what it connects to. That is your part.

**Paths.** Every `scripts/...` path below is relative to this skill's own
directory, not to the working directory — you are almost always invoked from the
user's project, so resolve them against the skill directory before running
anything. The vault path is separate and absolute: `~/.mentat`, or `$MENTAT_VAULT`
when it is set.

**Bootstrap.** If `~/.mentat/entries/` is missing, run `scripts/init-vault.sh`
before anything else. It is safe to re-run and repairs a partial vault.

## Routing

`/mentat` takes free-form input, so the first job is picking the operation. The
two high-traffic ones share a surface — `/mentat nginx cors bug` could mean save
or search — so resolve it deliberately instead of guessing.

| Signal in the input | Operation |
|---|---|
| A leading keyword: `load`, `profile`, `review`, `status`, `amend`, `groom`, `restore`, `audit`, `merge`, `split`, `forget`, `export`, `import`, `consolidate` | That operation |
| Asserts something — "we fixed X", "decided on Y", "remember that Z", a pasted snippet, a postmortem | [Remember](#remember) |
| Asks something, or is a bare topic — "what was the CORS fix?", "nginx cors", "did I note anything about retries?" | [Recall](#recall) |
| Genuinely ambiguous | [Recall](#recall) first |
| Nothing at all — a bare `/mentat` | [Status](#status), then offer the operations |

Recall wins ties because reading costs nothing and reverses itself, while writing
leaves a file the user has to clean up. A recall on an ambiguous input also
doubles as the deduplication check — if the entry already exists you should amend
it, not duplicate it. Say what you did: "Nothing in the vault on this — want me
to save it?" is a better outcome than a surprise entry.

For frontmatter, tagging rules and naming conventions, read
[FORMAT.md](references/FORMAT.md) before writing; for the body template of the
type you are writing, [TEMPLATES.md](references/TEMPLATES.md) — one section per
type, so read the one you need rather than all ten.

For Groom, Restore, Audit, Merge, Split, Forget, Export, Import and Consolidate,
read [OPERATIONS.md](references/OPERATIONS.md).

## Three dynamics

- **Reconsolidate** — using an entry strengthens it. `vault.py touch <slug>`
  applies the boost, increments `usage_count` and resets the idle clock.
- **Fade** — idle transient entries decay and eventually archive. `vault.py groom`
  applies it. Permanent types never fade.
- **Sieve** — recall weighs where a term matched. A hit in the slug is what
  past-you chose to call the entry, a hit in the frontmatter is a deliberate
  classification, a hit in the body may be an aside. `vault.py search` applies
  that weighting; the MOCs are the layer you read yourself when it comes up thin.

## Remember

Create a new entry.

1. **Curate.** Judge whether this will still matter in a month. Trivia, restated
   documentation and anything reconstructible from the repo cost more to maintain
   than they return — say you think it is trivial and why. Proceed if the user
   insists; it is their vault.
2. **Classify.** Pick the type from context: `note`, `idea`, `journal`, `bug`,
   `decision`, `feature`, `learning`, `snippet`, `episodic`, `schema`. The choice
   decides whether the entry is permanent or fadeable, so it is worth a moment.
3. **Deduplicate.** `vault.py search <key concepts>` before writing. On a strong
   match, ask whether to [Amend](#amend) instead — a second entry on the same
   subject splits the knowledge and neither copy stays current.
4. **Thread.** Name every concept worth linking: people, projects, technologies,
   related entries. Each becomes a `[[wiki-link]]` in kebab-case. Err toward more
   links, including ones with no target yet — an unresolved link is Obsidian
   showing you a knowledge gap, not an error. Pass sibling entries through
   `--related` rather than writing them into the body alone: the script mirrors
   each one back onto its target, and a link the other side cannot see is a link
   the graph does not have.
5. **Write.** Join the vocabulary already in use — `scripts/vault.py tags` lists
   every tag with its count, and picking `infra/nginx` because it is already there
   beats coining `tool/nginx`, which splits the same knowledge across two tag
   queries that each look complete. Compose the body from the type's template in
   [TEMPLATES.md](references/TEMPLATES.md) using atomic bullets, not
   paragraphs — a bullet can be scanned, moved and reused; a paragraph has to be
   reread. Then hand it to the script, which writes valid frontmatter and indexes
   the entry into its MOC, today's daily note and the dashboard in one step:

   ```bash
   scripts/vault.py write --type bug --slug nginx-strips-cors-header \
     --title "Nginx strips CORS header on 502" \
     --summary "Nginx dropped CORS headers on 502" \
     --project myapp --tags "infra/nginx, domain/auth" \
     --related 2026-01-04-api-gateway-timeout --body - <<'EOF'
   ## Symptoms
   ...
   EOF
   ```

Completion: dedup checked, `vault.py write` reported a path, and the user knows
what was saved and where. When you passed `--related`, it also printed one
`backlink:` line per target — check they all appear, and treat
`(no such entry yet)` as fine rather than as a failure: it means the target has
not been written, which is a gap worth seeing. With no `--related`, the path is
the only confirmation there is, and that is enough.

## Recall

Search the vault and present what matches.

1. **Sieve.** Expand the query into key terms plus likely synonyms and hand them
   all to the script at once — the user's wording rarely matches what past-you
   wrote, and passing more terms only improves the ranking:

   ```bash
   scripts/vault.py search cors nginx header origin preflight
   ```

   It scans slugs, frontmatter and bodies in one pass and returns
   `salience  type  slug — summary`, ranked by how many of your terms an entry
   matched and then by salience. That is the first three layers of the sieve
   collapsed into one call, so there is no reason to hand-roll `grep` for it.

   `--project <slug>` and `--type <type>` narrow it when a vault spanning several
   projects returns the right answer for the wrong one. Reach for them once the
   noise is real — a filter that hides the single matching entry costs more than
   the noise it removes, so an unfiltered pass first is the safer order.
2. **Read the MOCs when search comes up thin.** Under 3 hits, scan the one-line
   summaries in the two or three `maps/*.md` files whose type could plausibly hold
   the answer — `bugs.md` and `learnings.md` for "why did this break",
   `decisions.md` for "why did we choose this". This is the one layer the script
   cannot do for you: a summary can match a question semantically while sharing no
   literal term with it. Reading all ten MOCs is not thoroughness, it is the cost
   of not having formed a hypothesis about where the answer lives.

   Still nothing, and the topic is old enough to have faded? `search
   --include-archived` also ranks what Groom archived; hits come back marked
   `[archived]`. If one of them answers the question, it belongs in the working
   set again — `vault.py restore <slug>` moves it back and re-indexes it at full
   salience, which `touch` alone cannot do from the archive.
3. **Present.** Clickable file links in the order search returned them, each with
   its one-line summary. Carry over any marker the search line carried:
   `[superseded]` means the entry records what was true before something replaced
   it, and presenting it unmarked is how a stale decision gets quoted as current.
   On zero hits say so plainly and offer to remember it — a miss is a gap worth
   filling, not a dead end.
4. **Follow threads.** If the user wants depth, read the matches and follow their
   `[[wiki-links]]` one hop out. Stop there unless asked; the graph is connected
   enough that two hops reaches almost everything.
5. **Reconsolidate.** `vault.py touch <slug> ...` for every entry that actually
   helped answer the question. Skip the ones you opened and discarded — boosting
   those teaches the vault the wrong lesson about what matters. Search
   deliberately does not touch what it returns: appearing in a result list is not
   the same as being useful, and conflating them would flatten salience toward
   whatever term the user happens to search often.

Completion: `search` ran, results presented (or absence stated), and `touch`
applied to exactly the entries that earned it.

## Load

Load a core memory to anchor the session.

1. **Resolve.** With a project name (`/mentat load myapp`), use
   `~/.mentat/core-memory-myapp.md`; without one, `~/.mentat/core-memory.md`. If
   neither exists, ask what the Intent Anchor should be and create it.
2. **Adopt.** Read it and treat its intent and constraints as context for the
   rest of the session. Only on explicit invocation — silently adopting rules the
   user did not ask for makes later behavior impossible to explain.

Completion: file read, intent and constraints stated back so the user can correct
them before they take effect.

## Profile

Maintain who the user is, so the vault can work in their idiom.

1. **Resolve.** If `~/.mentat/profile.md` exists, read it, summarize it, and ask
   what to change. Otherwise continue.
2. **Interview.** Ask about name, role, primary stack, preferred language and any
   working preferences worth respecting. Keep it a conversation — start with
   identity, offer to go deeper. A half-filled profile beats an abandoned form.
3. **Write.** Create `~/.mentat/profile.md` from the template in
   [FORMAT.md](references/FORMAT.md), linking technologies as `[[wiki-links]]` so
   the profile joins the graph instead of sitting beside it.
4. **Thread.** Add backlinks from core-memory files that mention the same projects
   or tools.

Completion: profile exists with at least name and language, and the user has
confirmed it reads correctly.

## Review

Show what happened recently.

1. **List.** Accept an optional day count (default 7). Read today's daily note
   and the previous N-1, and present entries chronologically with file links,
   type and one-line summary.
2. **Summarize.** Run `scripts/vault.py stats` for the counts rather than
   recomputing them. Report activity in the window; leave health to
   [Status](#status).

Completion: entries in the window listed (or the window stated as empty), with
counts from `stats`.

## Status

Health dashboard. `scripts/vault.py stats` computes everything:

```bash
scripts/vault.py stats
```

It reports vault path, total and per-type entry counts, archived count, unique
link targets, disk size, entries nearing the archive threshold, orphans, unresolved
links and invalid frontmatter — flagging with ⚠️ when a threshold is crossed.

1. **Run it** and pass the table through; do not recount by hand.
2. **Act on the flags.** Suggest [Groom](references/OPERATIONS.md#groom) when it
   flags fading entries and [Audit](references/OPERATIONS.md#audit) when it flags
   integrity issues. Explain what each would do before running it.

Completion: table presented, and any ⚠️ turned into a concrete suggestion.

## Amend

Fold new information into an existing entry.

1. **Find.** Locate it via the [Recall](#recall) sieve.
2. **Edit.** Update the body, preserving `type`, `date` and `project` — the entry's
   identity should survive its content changing. Then `vault.py touch <slug>` to
   reconsolidate.
3. **Re-thread.** Add `[[wiki-links]]` for anything new. For sibling entries use
   `vault.py relate --slug <entry> --related <a>,<b>` rather than editing both
   files: it writes the link and its mirror in one call, the same way `write
   --related` does, and a link only one side can see is a link the graph does not
   have.
4. **Re-index.** If what the entry is about changed, give it a new summary:

   ```bash
   scripts/vault.py reindex --slug nginx-strips-cors-header \
     --summary "Nginx dropped CORS headers on 502 and 504"
   ```

   That rewrites the label on every bullet pointing at the entry — its MOC, the
   index and every daily note — from the one place the summary is stored. Editing
   those by hand means finding three or more copies and getting them to agree,
   which is how a MOC ends up describing an entry that no longer says that.

Completion: body updated, `touch` applied, new links threaded both ways, and
`reindex` run if the summary changed.
