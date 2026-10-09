# Mentat (Memory Vault)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Format](https://img.shields.io/badge/format-obsidian--ready-blueviolet)

> *"It is by will alone I set my mind in motion."* — Mentat Mantra (Dune)

**Mentat** is a persistent, graph-based knowledge vault designed for AI coding agents. It ensures that critical context, bug fixes, decisions, and patterns discovered during AI sessions are never lost between context windows.

Inspired by cognitive science and agent-memory research (such as Mem-α and Engram), Mentat stores knowledge not as unstructured text, but as **Atomic Bullets** linked together in a concept graph, allowing for true reconsolidation and learning over time.

---

## 🧠 Core Capabilities

- **Atomic Knowledge Base**: Information is strictly captured as concise, trackable bullets. No rambling paragraphs.
- **Core Memory Anchoring**: On-demand intent anchors (`core-memory.md` for global context, `core-memory-{project}.md` for project-specific context) ground the agent in your overarching objective.
- **User Profile**: A persistent `profile.md` stores who the user is — name, role, stack, preferences — so the mentat personalizes its work across sessions.
- **Reconsolidation & Salience**: Memories grow stronger (`salience` increases, `last_accessed` updates) the more they are recalled and prove useful.
- **Permanent vs. Transient Memory**:
  - Structural knowledge (`bug`, `decision`, `learning`, `schema`, `snippet`, `feature`) is **immortal**. It will never decay.
  - Transient knowledge (`note`, `idea`, `journal`, `episodic`) decays based on idle time and is eventually archived.
- **Cadence-Insensitive Decay**: Fading is anchored on a `decayed_at` timestamp, so grooming daily and grooming weekly converge on the same result. Maintenance frequency never decides what the vault forgets.
- **Deterministic Bookkeeping**: Salience math, index updates, decay and integrity checks run in `scripts/vault.py`. The agent spends its judgment on what to remember and how it connects — not on hand-editing YAML across a dozen files.
- **Schema Synthesis**: The agent can synthesize multiple scattered entries into unified, abstract pattern schemas.
- **Validity Gate**: The system actively refuses to store trivial or obvious information unless explicitly instructed.
- **Health Monitoring**: A status command reports vault health, warns about entries approaching the archive threshold, and detects orphans and broken links.
- **Reversible Fading**: Archived entries stay searchable on demand (`search --include-archived`) and come back with `restore`, re-indexed and at full salience.

## 📂 Vault Architecture

Everything is stored in a flat directory structure at `~/.mentat/` that opens natively as an **Obsidian** vault:

```text
~/.mentat/
├── .obsidian/                  ← Auto-generated Obsidian config (wiki-links, graph colors)
├── core-memory.md              ← Global intent anchor and world state
├── core-memory-{project}.md    ← Per-project intent anchors (optional)
├── profile.md                  ← User identity and preferences
├── index.md                    ← Vault dashboard with recent entries
├── entries/                    ← All atomic entries (flat, connected by [[wiki-links]])
├── maps/                       ← Maps of Content by type (bugs.md, decisions.md, ...)
├── daily/                      ← Daily notes (chronological index)
└── archive/                    ← Faded transient memories (recoverable)
```

## 🚀 Installation

Mentat works with CLI-based AI agents like **Claude Code**, **Codex**, **Antigravity** or **OpenCode**, and one vault serves all of them.

### 1. Clone

```bash
git clone <this repository> ~/workspace/skills   # anywhere you like
```

### 2. Run setup

Ask any agent for `/mentat setup`, or run it yourself — preview first:

```bash
python3 /path/to/mentat/scripts/setup.py --dry-run
python3 /path/to/mentat/scripts/setup.py                 # this machine only
python3 /path/to/mentat/scripts/setup.py --remote git@github.com:you/mentat-memory.git
python3 /path/to/mentat/scripts/setup.py --agents claude,codex   # main memory only for these
python3 /path/to/mentat/scripts/setup.py --uninstall             # back out, vault kept
```

Mentat as the **main** memory is opt-in per agent. `--agents` (default `all`; also `none`, or any of `claude,codex,antigravity,opencode`) picks which agents get the pointer block and have their own memory absorbed; the others keep their own memory and can still consult the skill. Through `/mentat setup` the agent asks this before showing the plan.

Setup is idempotent — re-run it whenever, it only fixes what drifted. It:

- creates or repairs the vault at `~/.mentat` (or clones it from `--remote`);
- adds a short pointer block to the global instructions of every chosen agent (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.config/opencode/AGENTS.md`), between `<!-- mentat:start -->` markers — around 100 tokens per agent, nothing else is loaded up front;
- links the skill into each agent's skills directory where it is missing or broken;
- with a remote, installs the merge rules and a timer (systemd on Linux, launchd on macOS) that syncs every 30 minutes;
- lists what each chosen agent remembered on its own, so the agent can absorb it into the vault with your approval.

`--uninstall` removes the pointer blocks, restores each `MEMORY.md` the absorb step redirected (from its `MEMORY.md.pre-mentat` copy) and removes the timer; the vault, its repository and the skill links stay. Combine with `--agents` to back out only some agents.

`init-vault.sh` still exists for a bare vault without any of the above; it is idempotent and repairs a partial vault.

## 🔄 Sharing the vault across machines

Sync is optional. Without a git repository in `~/.mentat`, the vault is a single-machine memory and `sync` says so and changes nothing.

With one, point every machine at the same **private** repository (`setup.py --remote <url>`), and `vault.py sync` — run by the timer, or `/mentat sync` on request — commits, merges, reconciles the indexes and pushes:

| Changed on two machines | Result |
|---|---|
| New entries, index and daily bullets | Merged: both sides kept |
| `salience`, `usage_count`, dates, `related` of the same entry | Merged by rule: stronger salience, uses from both sides, latest date, union of links |
| An entry body, `profile.md` or `core-memory.md` | Sync stops and lists the files; the agent proposes the merged text and asks |

The merge driver is defined per machine in `.git/config` (git never versions it), which is why each new machine runs setup instead of a bare `git clone`.

## 🛠 Usage & Commands

Trigger the skill with `/mentat` followed by your prompt. The skill also engages on its own when you lean on something from an earlier session ("what was that CORS fix?").

### Remember vs. Recall

`/mentat [text]` and `/mentat [query]` share one surface, so the skill routes on intent: input that **asserts** something is a Remember, input that **asks** something is a Recall, and anything genuinely ambiguous is treated as a Recall first. Reading is free and reversible, and a recall doubles as the deduplication check — so an ambiguous prompt shows you what already exists and then offers to save.

### Core Commands

| Command | Action | Description |
|---------|--------|-------------|
| `/mentat [text]` | **Remember** | Curates the input via the Validity Gate. If valid, saves as an atomic entry, threads `[[wiki-links]]`, dedup-checks, and indexes it into its MOC, the daily note and the dashboard. |
| `/mentat [query]` | **Recall** | Weighted search across slugs, frontmatter and bodies, with the MOCs as the semantic fallback. Follows threads. Reconsolidates the entries that actually helped. |
| `/mentat load [project]` | **Load** | Reads `core-memory.md` (or `core-memory-{project}.md`) to ground the agent in context. |
| `/mentat profile` | **Profile** | Builds or views the user's identity profile. First time: conversational interview. After: shows current profile, allows updates. |
| `/mentat review [N]` | **Review** | Recent vault activity from the last N days (default: 7), with counts. |
| `/mentat status` | **Status** | Health dashboard — entry counts, disk size, fade warnings, orphans, broken links. |
| `/mentat amend [query]` | **Amend** | Finds and updates an existing entry. Reconsolidates salience. |

### Maintenance Commands

| Command | Action | Description |
|---------|--------|-------------|
| `/mentat consolidate` | **Consolidate** | Analyzes scattered entries and synthesizes them into a unified **Schema**. |
| `/mentat groom` | **Groom** | Applies exponential decay to idle transient entries and archives the spent ones. Permanent types are immune. |
| `/mentat restore [query]` | **Restore** | Brings an archived entry back into the working set, re-indexed and at full salience. |
| `/mentat audit` | **Audit** | Validates integrity: orphans, broken links, stale references, unparseable frontmatter. |
| `/mentat merge` | **Merge** | Combines two redundant entries, preserving all links and metadata. |
| `/mentat split [query]` | **Split** | Divides a multi-topic entry into separate atomic entries. |
| `/mentat forget [query]` | **Forget** | Permanently deletes an entry after confirmation. Cleans up all references. |
| `/mentat export` | **Export** | Creates a `.zip` backup of the entire vault. |
| `/mentat import [path]` | **Import** | Restores from a backup. Supports replace or merge strategies. |
| `/mentat setup` | **Setup** | Wires the vault into every installed agent, optionally shares it through git, and absorbs what agents remembered on their own. |
| `/mentat sync` | **Sync** | Commits, merges and pushes the vault when it has a remote; does nothing otherwise. |

### Examples

- **Remembering a fix:**
  `> /mentat tivemos um bug de CORS hoje causado pelo Nginx, salve isso como bug.`
- **Recalling it later:**
  `> /mentat o que era aquele problema de CORS?`
- **Loading context:**
  `> /mentat load myapp`
- **Checking vault health:**
  `> /mentat status`

## ⚙️ The `vault.py` CLI

The skill delegates every deterministic operation to one dependency-free script. It is usable directly:

```bash
scripts/vault.py write --type bug --slug nginx-strips-cors-header \
  --summary "Nginx dropped CORS headers on 502" --tags "infra/nginx" \
  --related 2026-01-04-api-gateway-timeout --body -   # backlinks both ways
scripts/vault.py search cors nginx origin header    # ranked, weighted by where it hit
scripts/vault.py search cors --project checkout-api --type bug   # scoped
scripts/vault.py search cors --include-archived     # also what groom archived
scripts/vault.py restore ephemeral-note             # archive → entries, re-indexed
scripts/vault.py touch nginx-strips-cors-header     # reconsolidate
scripts/vault.py relate --slug nginx-strips-cors-header \
  --related 2026-01-04-api-gateway-timeout          # link both ways, after the fact
scripts/vault.py tags                               # the vocabulary already in use
scripts/vault.py reindex --slug nginx-strips-cors-header \
  --summary "Nginx dropped CORS headers on 502 and 504"  # summary → MOC, daily, index
scripts/vault.py groom --dry-run                    # preview the fade
scripts/vault.py stats --json                       # health, machine-readable
scripts/vault.py audit --fix                        # repair bookkeeping damage
scripts/vault.py sync                               # share through git, if configured
scripts/vault.py --selfcheck                        # verify decay and index editing
```

Every tunable — decay rate, archive threshold, starting salience, index cap — is defined once at the top of that file, so documentation and behavior cannot drift apart. Set `MENTAT_VAULT` to point the CLI at a vault other than `~/.mentat`.

## 🔮 Obsidian Integration

Mentat is designed to be a first-class citizen in [Obsidian](https://obsidian.md/).

1. Open Obsidian.
2. Select **Open folder as vault**.
3. Choose `~/.mentat/`.

**Native benefits you get for free:**
- **Graph View:** Visualize the clustering of your bugs, features, and technologies. Entries are auto-colored by type via `type/` tags.
- **Backlinks:** See exactly what technologies or decisions caused specific issues.
- **Unresolved Links:** Discover knowledge gaps automatically.

> **Tag note:** frontmatter tags are written as bare paths (`type/bug`), never with a leading `#`. A `#` inside a YAML flow sequence is a comment indicator, which breaks the whole frontmatter block and drops the entry from every Obsidian tag query. The `#` form is only for inline tags and search queries like `tag:#type/bug`.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
