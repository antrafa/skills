#!/usr/bin/env python3
"""Bookkeeping for the Mentat vault.

The agent owns judgment (what is worth remembering, how to phrase it, what to
link). This script owns arithmetic and cross-file consistency, because those are
deterministic and an LLM editing frontmatter by hand gets them wrong.

Every tunable number lives here and nowhere else — SKILL.md and OPERATIONS.md
reference this file instead of restating values, so they cannot drift apart.

Subcommands: write | search | touch | relate | reindex | groom | restore
             | stats | tags | audit
Run `python3 vault.py --selfcheck` to verify the decay model and index editing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import re
import shutil
import sys
from pathlib import Path

# --- Tunables (single source of truth) ---------------------------------------

PERMANENT_TYPES = {"bug", "decision", "learning", "schema", "snippet", "feature"}
FADEABLE_TYPES = {"note", "idea", "journal", "episodic"}
ALL_TYPES = sorted(PERMANENT_TYPES | FADEABLE_TYPES)

SALIENCE_NEW = 100
SALIENCE_NEW_SCHEMA = 200
SALIENCE_MAX = 500
SALIENCE_BOOST = 10
ARCHIVE_AT = 10  # fadeable entries at or below this are archived by groom
FADE_WARN_AT = 30  # "approaching archive" band reported by stats
GROOM_SUGGEST_AT = 10  # stats suggests groom above this many warn-band entries
DECAY_RATE = 0.98  # per idle day
INDEX_RECENT_MAX = 10

RESOLVED_BY_DEFAULT = {"bug", "feature", "episodic"}

VAULT = Path(os.environ.get("MENTAT_VAULT", Path.home() / ".mentat"))

# --- Frontmatter -------------------------------------------------------------

_FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
_DATED_SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
# An index bullet: `- [[slug]] — summary` with the daily note's optional `(type)`.
_LABEL_RE = re.compile(r"^(\s*- .*?\]\]\s+—\s+)(.*?)(\s+\([a-z]+\))?$")


def parse_entry(path: Path) -> tuple[dict[str, str] | None, str]:
    """Split a markdown file into (frontmatter, body).

    Values stay as raw strings and key order is preserved so that rewriting an
    entry only changes the fields we touched — no reformatting churn, no lost
    keys we do not know about.
    """
    text = path.read_text(encoding="utf-8")
    match = _FM_RE.match(text)
    if not match:
        return None, text
    front: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        front[key.strip()] = value.strip()
    return front, text[match.end():]


def dump_entry(path: Path, front: dict[str, str], body: str) -> None:
    rendered = "\n".join(
        f"{key}: {value}" if value else f"{key}:" for key, value in front.items()
    )
    path.write_text(f"---\n{rendered}\n---\n{body}", encoding="utf-8")


def read_int(front: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(str(front.get(key, default)).strip())
    except (TypeError, ValueError):
        return default


def read_str(front: dict[str, str], key: str) -> str:
    return (front.get(key) or "").strip().strip("\"'")


def yaml_str(value: str) -> str:
    """Quote a free-text scalar so a `:` or `#` inside it cannot break the block.

    `summary: fixed CORS: only on 502` is not valid YAML, and Obsidian drops an
    entry whose frontmatter fails to parse from every tag query — the same
    failure mode the `#`-in-tags rule exists to prevent.
    """
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read_date(front: dict[str, str], *keys: str) -> dt.date | None:
    for key in keys:
        raw = (front.get(key) or "").strip().strip("\"'")
        try:
            return dt.date.fromisoformat(raw)
        except ValueError:
            continue
    return None


# --- Markdown section editing ------------------------------------------------


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _write_lines(path: Path, lines: list[str]) -> None:
    """Write markdown back, keeping a blank line before every heading.

    Inserting or deleting bullets otherwise eats the separator between a list and
    the heading that follows it.
    """
    out: list[str] = []
    for line in lines:
        if line.startswith("#") and out and out[-1].strip():
            out.append("")
        out.append(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def insert_under(path: Path, heading: str, line: str, limit: int | None = None) -> None:
    """Insert `line` as the first bullet under `heading`, creating it if absent."""
    lines = _read_lines(path)
    try:
        at = next(i for i, l in enumerate(lines) if l.strip() == heading)
    except StopIteration:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(heading)
        at = len(lines) - 1
    cursor = at + 1
    while cursor < len(lines) and not lines[cursor].strip():
        cursor += 1
    # Replace the blank run after the heading with exactly one blank plus the new
    # bullet, so repeated inserts stay a tight list instead of double-spacing.
    lines[at + 1:cursor] = ["", line]
    _write_lines(path, lines)
    if limit is not None:
        trim_under(path, heading, limit)


def trim_under(path: Path, heading: str, limit: int) -> None:
    """Keep at most `limit` bullets under `heading` (oldest are last, so drop tail)."""
    lines = _read_lines(path)
    out, inside, kept = [], False, 0
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            inside, kept = True, 0
            out.append(line)
            continue
        if inside and stripped.startswith("#"):
            inside = False
        if inside and stripped.startswith("- "):
            kept += 1
            if kept > limit:
                continue
        out.append(line)
    _write_lines(path, out)


def links_to(line: str, slug: str) -> bool:
    """Does this line carry a wiki-link whose target is exactly `slug`?

    Comparing link targets rather than searching for the slug as a substring is
    what keeps archiving `2026-01-01-cors` from also deindexing
    `2026-01-01-cors-fix`: any slug that is a prefix of another used to delete
    its neighbour's line from the MOC, the daily note and the index — silently,
    since the surviving entry then looks like an orphan rather than a victim.
    """
    return any(target.strip() == slug for target in _WIKILINK_RE.findall(line))


def drop_lines_mentioning(path: Path, slug: str) -> int:
    """Remove every bullet linking to `slug`. Returns how many were removed."""
    if not path.exists():
        return 0
    lines = _read_lines(path)
    kept = [l for l in lines if not (l.strip().startswith("- ") and links_to(l, slug))]
    removed = len(lines) - len(kept)
    if removed:
        _write_lines(path, kept)
    return removed


def relabel_lines_linking(path: Path, slug: str, summary: str) -> int:
    """Rewrite the one-line summary on every bullet linking to `slug`.

    Position and any trailing annotation are preserved — the daily note's
    `(type)` marker and the ordering of `## Recent` carry meaning, so a summary
    change should not reorder the index or drop the type.
    """
    if not path.exists():
        return 0
    lines = _read_lines(path)
    changed = 0
    for index, line in enumerate(lines):
        if not (line.strip().startswith("- ") and links_to(line, slug)):
            continue
        match = _LABEL_RE.match(line)
        if not match:
            continue
        relabeled = f"{match.group(1)}{summary}{match.group(3) or ''}"
        if relabeled != line:
            lines[index] = relabeled
            changed += 1
    if changed:
        _write_lines(path, lines)
    return changed


# --- Vault paths -------------------------------------------------------------


def entries_dir() -> Path:
    return VAULT / "entries"


def archive_dir() -> Path:
    return VAULT / "archive"


def moc_path(entry_type: str) -> Path:
    return VAULT / "maps" / f"{entry_type}s.md"


def daily_path(day: dt.date) -> Path:
    return VAULT / "daily" / f"{day.isoformat()}.md"


def iter_entries(directory: Path | None = None):
    directory = directory or entries_dir()
    if not directory.exists():
        return
    for path in sorted(directory.glob("*.md")):
        front, body = parse_entry(path)
        yield path, front, body


def match_entries(query: str, directory: Path | None = None) -> list[Path]:
    """Candidates for a slug-ish query: exact path, then exact slug, then substring."""
    directory = directory or entries_dir()
    candidate = Path(query)
    if candidate.is_file():
        return [candidate]
    for name in (query, f"{query}.md"):
        direct = directory / name
        if direct.is_file():
            return [direct]
    return [p for p in directory.glob("*.md") if query.lower() in p.stem.lower()]


def resolve_entry(query: str) -> Path:
    """Find exactly one entry, or exit — for commands that must hit a single file."""
    hits = match_entries(query)
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"error: no entry matching {query!r}")
    sys.exit("error: ambiguous, matches:\n  " + "\n  ".join(p.stem for p in hits))


def entry_summary(front: dict[str, str], body: str, stem: str) -> str:
    """The entry's one-line summary, falling back for entries written by hand."""
    return read_str(front, "summary") or next(
        (l[2:].strip() for l in body.splitlines() if l.startswith("# ")), stem
    )


def render_related(targets: list[str]) -> str:
    return "[" + ", ".join(f'"[[{t.strip().strip("[]")}]]"' for t in targets) + "]"


# --- write -------------------------------------------------------------------


def normalize_tags(raw: str, entry_type: str) -> list[str]:
    """Strip `#` from frontmatter tags — a `#` there is invalid YAML.

    Obsidian's `tags` property takes bare paths (`type/bug`); the `#` prefix only
    belongs in inline tags and in search/graph queries.
    """
    tags = [t.strip().lstrip("#") for t in raw.split(",") if t.strip()]
    type_tag = f"type/{entry_type}"
    return [type_tag] + [t for t in tags if t != type_tag]


def read_body(value: str | None) -> str:
    """Resolve the entry body from the flag, or from stdin when something piped it.

    The old default of `-` meant a call without a heredoc blocked forever on an
    interactive stdin. Deciding by whether stdin is a terminal fails safe in both
    directions: piped input is read even if the flag was forgotten, and a bare
    invocation at a prompt writes an empty body instead of hanging the session.
    """
    if value == "-":
        return sys.stdin.read()
    if value is not None:
        return value
    return "" if sys.stdin.isatty() else sys.stdin.read()


def cmd_write(args: argparse.Namespace) -> None:
    if args.type not in ALL_TYPES:
        sys.exit(f"error: type must be one of {', '.join(ALL_TYPES)}")
    today = dt.date.today()
    slug = re.sub(r"[^a-z0-9-]+", "-", args.slug.lower()).strip("-")
    slug = _DATED_SLUG_RE.sub("", slug)
    stem = f"{today.isoformat()}-{slug}"
    path = entries_dir() / f"{stem}.md"
    if path.exists() and not args.force:
        sys.exit(f"error: {path} already exists (use --force to overwrite)")

    salience = SALIENCE_NEW_SCHEMA if args.type == "schema" else SALIENCE_NEW
    status = args.status or ("resolved" if args.type in RESOLVED_BY_DEFAULT else "open")
    related = [r.strip() for r in (args.related or "").split(",") if r.strip()]
    summary = args.summary or args.title or slug
    front = {
        "type": args.type,
        "date": today.isoformat(),
        "tags": "[" + ", ".join(normalize_tags(args.tags or "", args.type)) + "]",
        "project": args.project or "",
        # The summary lives with the entry so `reindex` has one source of truth to
        # push out to the MOC, the daily note and the index — three copies with no
        # original is how a summary ends up describing an entry that changed.
        "summary": yaml_str(summary),
        "salience": str(salience),
        "usage_count": "0",
        "last_accessed": today.isoformat(),
        "decayed_at": today.isoformat(),
        "status": status,
        "related": render_related(related),
    }
    body = read_body(args.body).strip("\n")
    if args.title and not body.lstrip().startswith("# "):
        body = f"# {args.title}\n\n{body}"
    body = f"\n{body}\n"
    entries_dir().mkdir(parents=True, exist_ok=True)
    dump_entry(path, front, body)

    insert_under(moc_path(args.type), "## Recent", f"- [[{stem}]] — {summary}")
    daily = daily_path(today)
    if not daily.exists():
        daily.parent.mkdir(parents=True, exist_ok=True)
        daily.write_text(f"# {today.isoformat()}\n\n## Entries\n", encoding="utf-8")
    insert_under(daily, "## Entries", f"- [[{stem}]] — {summary} ({args.type})")
    insert_under(
        VAULT / "index.md", "## Recent Entries", f"- [[{stem}]] — {summary}",
        limit=INDEX_RECENT_MAX,
    )
    print(path)
    for target, linked in thread_backlinks(stem, related):
        print(f"backlink: {target} <- {stem}" if linked else f"backlink: {target} (no such entry yet)")


def add_related(path: Path, stem: str) -> bool:
    """Append `stem` to an entry's `related` list, unless it is already there."""
    front, body = parse_entry(path)
    if front is None:
        return False
    existing = re.findall(r"\[\[([^\]|#]+)", front.get("related", "") or "")
    if any(t.strip() == stem for t in existing):
        return False
    front["related"] = render_related([t.strip() for t in existing] + [stem])
    dump_entry(path, front, body)
    return True


def thread_backlinks(stem: str, related: list[str]) -> list[tuple[str, bool]]:
    """Add the reverse link on every related entry that exists.

    A one-way link is invisible in Obsidian from the other side, so the graph
    quietly stops connecting. Which entries to relate is judgment and stays with
    the agent; writing the mirror of that choice is frontmatter arithmetic.

    A target with no file yet is reported, not an error — an unresolved link is
    Obsidian showing a knowledge gap.
    """
    results = []
    for target in related:
        hits = match_entries(target)
        results.append((target, len(hits) == 1 and add_related(hits[0], stem)))
    return results


# --- relate ------------------------------------------------------------------


def cmd_relate(args: argparse.Namespace) -> None:
    """Thread an existing entry to siblings, both directions.

    `write` already mirrors `--related` onto its targets; amending an entry used
    to mean doing that by hand on two files and remembering which side was
    missing. A link only one side can see is a link the graph does not have.
    """
    path = resolve_entry(args.slug)
    targets: list[str] = []
    for raw in (t.strip() for t in args.related.split(",")):
        if not raw:
            continue
        hits = match_entries(raw)
        stem = hits[0].stem if len(hits) == 1 else raw
        if stem != path.stem and stem not in targets:
            targets.append(stem)
    if not targets:
        sys.exit("error: --related listed nothing to link")
    for stem in targets:
        added = add_related(path, stem)
        print(f"{path.stem} -> {stem}" + ("" if added else " (already linked)"))
    for target, linked in thread_backlinks(path.stem, targets):
        print(
            f"backlink: {target} <- {path.stem}" if linked
            else f"backlink: {target} (no such entry yet)"
        )


# --- touch (reconsolidate) ---------------------------------------------------


def reconsolidate(path: Path) -> tuple[int, int]:
    front, body = parse_entry(path)
    if front is None:
        sys.exit(f"error: {path} has no frontmatter")
    before = read_int(front, "salience")
    after = min(before + SALIENCE_BOOST, SALIENCE_MAX)
    front["salience"] = str(after)
    front["usage_count"] = str(read_int(front, "usage_count") + 1)
    front["last_accessed"] = dt.date.today().isoformat()
    dump_entry(path, front, body)
    return before, after


def cmd_touch(args: argparse.Namespace) -> None:
    for query in args.entries:
        path = resolve_entry(query)
        before, after = reconsolidate(path)
        print(f"{path.stem}: salience {before} -> {after}")


# --- search ------------------------------------------------------------------

# Where a term matches says how much it means. A slug hit is what past-you chose
# to call the entry; a frontmatter hit is a deliberate classification; a body hit
# might be an aside. Terms are OR-ed because the caller is expected to pass
# synonyms — the user's wording rarely matches what past-you wrote — so entries
# matching more of them rank first.
MATCH_WEIGHTS = {"slug": 4, "meta": 2, "body": 1}


def search_entries(
    terms: list[str],
    *,
    project: str | None = None,
    entry_type: str | None = None,
    include_archived: bool = False,
) -> list[dict]:
    needles = [t.lower() for t in terms if t.strip()]
    candidates = [(path, front, body, False) for path, front, body in iter_entries()]
    if include_archived:
        candidates += [(p, f, b, True) for p, f, b in iter_entries(archive_dir())]
    hits = []
    for path, front, body, archived in candidates:
        if front is None:
            continue
        # Scoping is opt-in so an unfiltered search keeps ranking the whole
        # vault — a filter that silently hides the one matching entry is worse
        # than the noise it removes.
        if project and read_str(front, "project").lower() != project.lower():
            continue
        if entry_type and front.get("type") != entry_type:
            continue
        haystacks = {
            "slug": path.stem.lower(),
            "meta": " ".join(
                front.get(k, "") for k in ("tags", "project", "related", "summary", "status")
            ).lower(),
            "body": body.lower(),
        }
        score = matched = 0
        for needle in needles:
            weight = max(
                (w for field, w in MATCH_WEIGHTS.items() if needle in haystacks[field]),
                default=0,
            )
            if weight:
                matched += 1
                score += weight
        if matched:
            hits.append({
                "slug": path.stem,
                "type": front.get("type", "?"),
                "salience": read_int(front, "salience"),
                "summary": entry_summary(front, body, path.stem),
                "path": str(path),
                "status": read_str(front, "status"),
                "archived": archived,
                "terms_matched": matched,
                "score": score,
            })
    hits.sort(key=lambda h: (-h["terms_matched"], -h["score"], -h["salience"]))
    return hits


def search_flags(hit: dict) -> str:
    """Mark what a caller must not read past the summary.

    A superseded entry ranks like any other — it matched the same terms — so
    presenting it unmarked is how last year's decision gets quoted as current.
    Same for an archived hit: it is real knowledge, but it is not in the vault's
    working set until `restore` puts it back.
    """
    marks = []
    if hit.get("archived"):
        marks.append("archived")
    if hit.get("status") and hit["status"] not in ("open", "resolved"):
        marks.append(hit["status"])
    return "".join(f"  [{m}]" for m in marks)


def cmd_search(args: argparse.Namespace) -> None:
    hits = search_entries(
        args.terms,
        project=args.project,
        entry_type=args.type,
        include_archived=args.include_archived,
    )[: args.limit]
    if args.json:
        import json

        print(json.dumps(hits, indent=2))
        return
    if not hits:
        print("no matches — the vault has nothing on these terms")
        return
    width = max(len(h["type"]) for h in hits)
    for hit in hits:
        print(
            f"{hit['salience']:>4}  {hit['type'].ljust(width)}  "
            f"{hit['slug']} — {hit['summary']}{search_flags(hit)}"
        )


# --- reindex -----------------------------------------------------------------


def cmd_reindex(args: argparse.Namespace) -> None:
    path = resolve_entry(args.slug)
    front, body = parse_entry(path)
    if front is None:
        sys.exit(f"error: {path} has no frontmatter")
    if args.summary:
        front["summary"] = yaml_str(args.summary)
        dump_entry(path, front, body)
    summary = entry_summary(front, body, path.stem)
    targets = [moc_path(front.get("type", "")), VAULT / "index.md"]
    targets += sorted((VAULT / "daily").glob("*.md"))
    changed = sum(relabel_lines_linking(p, path.stem, summary) for p in targets)
    print(f"{path.stem}: {changed} index lines relabeled")
    if not changed:
        print("nothing pointed at it — run audit --fix to re-index an orphan")


# --- groom -------------------------------------------------------------------


def decayed_salience(salience: int, idle_days: int) -> int:
    if idle_days <= 0:
        return salience
    return max(0, math.floor(salience * DECAY_RATE**idle_days))


def cmd_groom(args: argparse.Namespace) -> None:
    today = dt.date.today()
    archive = VAULT / "archive"
    faded = archived = 0
    for path, front, body in iter_entries():
        if front is None or front.get("type") not in FADEABLE_TYPES:
            continue
        # Decay accrues only over days the entry sat unused, measured from
        # whichever happened later: the last decay pass or the last access.
        # Anchoring on decayed_at is what makes groom cadence-insensitive —
        # decaying from last_accessed alone re-applies the same idle window on
        # every run and destroys the vault when groom is run often.
        created = read_date(front, "date") or today
        floor_date = read_date(front, "decayed_at") or created
        accessed = read_date(front, "last_accessed") or created
        idle_days = (today - max(floor_date, accessed)).days
        before = read_int(front, "salience")
        after = decayed_salience(before, idle_days)
        if after == before and "decayed_at" in front:
            continue
        if args.dry_run:
            print(f"{path.stem}: {before} -> {after} ({idle_days}d idle)")
            continue
        front["salience"] = str(after)
        front["decayed_at"] = today.isoformat()
        dump_entry(path, front, body)
        faded += 1
        if after <= ARCHIVE_AT:
            archive.mkdir(parents=True, exist_ok=True)
            drop_lines_mentioning(moc_path(front["type"]), path.stem)
            for daily in sorted((VAULT / "daily").glob("*.md")):
                drop_lines_mentioning(daily, path.stem)
            drop_lines_mentioning(VAULT / "index.md", path.stem)
            shutil.move(str(path), str(archive / path.name))
            archived += 1
            print(f"archived {path.stem} (salience {after})")
    if not args.dry_run:
        print(f"groom: {faded} entries faded, {archived} archived")


# --- restore -----------------------------------------------------------------


def cmd_restore(args: argparse.Namespace) -> None:
    """Bring an archived entry back into the working set and re-index it.

    Groom archives rather than deletes precisely so this is possible, but until
    now the way back was `mv` plus three index edits by hand. Restoring at the
    salience it faded to would also be pointless — the next groom would archive
    it again the same day — so the idle clock is reset with it.
    """
    hits = match_entries(args.slug, archive_dir())
    if not hits:
        sys.exit(f"error: no archived entry matching {args.slug!r}")
    if len(hits) > 1:
        sys.exit("error: ambiguous, matches:\n  " + "\n  ".join(p.stem for p in hits))
    path = hits[0]
    front, body = parse_entry(path)
    if front is None or front.get("type") not in ALL_TYPES:
        sys.exit(f"error: {path} has no usable frontmatter — restore it by hand")
    target = entries_dir() / path.name
    if target.exists():
        sys.exit(f"error: {target} already exists — merge the two by hand")

    today = dt.date.today()
    entry_type = front["type"]
    front["salience"] = str(SALIENCE_NEW_SCHEMA if entry_type == "schema" else SALIENCE_NEW)
    front["last_accessed"] = today.isoformat()
    front["decayed_at"] = today.isoformat()
    entries_dir().mkdir(parents=True, exist_ok=True)
    dump_entry(target, front, body)
    path.unlink()

    summary = entry_summary(front, body, target.stem)
    insert_under(moc_path(entry_type), "## Recent", f"- [[{target.stem}]] — {summary}")
    insert_under(
        VAULT / "index.md", "## Recent Entries", f"- [[{target.stem}]] — {summary}",
        limit=INDEX_RECENT_MAX,
    )
    created = read_date(front, "date")
    daily = daily_path(created) if created else None
    if daily is not None and daily.exists():
        insert_under(daily, "## Entries", f"- [[{target.stem}]] — {summary} ({entry_type})")
    print(target)
    print(f"restored at salience {front['salience']}, re-indexed into {moc_path(entry_type).name}")


# --- stats -------------------------------------------------------------------


def collect_stats() -> dict:
    by_type: dict[str, int] = {}
    links: set[str] = set()
    unresolved: set[str] = set()
    warn: list[str] = []
    invalid: list[str] = []
    slugs = {p.stem for p in entries_dir().glob("*.md")} if entries_dir().exists() else set()
    archived_slugs = (
        {p.stem for p in (VAULT / "archive").glob("*.md")}
        if (VAULT / "archive").exists()
        else set()
    )
    moc_text = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted((VAULT / "maps").glob("*.md"))
    ) if (VAULT / "maps").exists() else ""
    # Indexed-ness is decided on link targets, never on substrings: `...-cors`
    # appears inside `...-cors-fix`, so a substring test declared a genuinely
    # un-indexed entry healthy whenever a longer sibling was indexed. Same
    # failure `links_to` exists to prevent, one layer up.
    moc_links = {t.strip() for t in _WIKILINK_RE.findall(moc_text)}

    orphans: list[str] = []
    for path, front, body in iter_entries():
        if front is None or "type" not in front:
            invalid.append(path.stem)
            continue
        entry_type = front["type"]
        by_type[entry_type] = by_type.get(entry_type, 0) + 1
        for target in _WIKILINK_RE.findall(body + " " + front.get("related", "")):
            target = target.strip()
            links.add(target)
            if _DATED_SLUG_RE.match(target) and target not in slugs | archived_slugs:
                unresolved.add(target)
        if entry_type in FADEABLE_TYPES and read_int(front, "salience") <= FADE_WARN_AT:
            warn.append(path.stem)
        if path.stem not in moc_links:
            orphans.append(path.stem)

    size = sum(f.stat().st_size for f in VAULT.rglob("*") if f.is_file()) if VAULT.exists() else 0
    return {
        "vault": str(VAULT),
        "total_entries": len(slugs),
        # An entry whose frontmatter no longer parses has no type to count, so
        # by_type cannot sum to the total on its own. Reporting `classified`
        # alongside it keeps the arithmetic checkable — classified + invalid is
        # the total, always — instead of leaving a silent gap between two numbers
        # that look like they should agree.
        "classified": sum(by_type.values()),
        "by_type": dict(sorted(by_type.items())),
        "archived": len(archived_slugs),
        "unique_link_targets": len(links),
        "unresolved_links": sorted(unresolved),
        "fade_warning": sorted(warn),
        "orphans": sorted(orphans),
        "invalid_frontmatter": sorted(invalid),
        "disk_bytes": size,
        "suggest_groom": len(warn) > GROOM_SUGGEST_AT,
        "suggest_audit": bool(orphans or unresolved or invalid),
    }


def cmd_stats(args: argparse.Namespace) -> None:
    data = collect_stats()
    if args.json:
        import json

        print(json.dumps(data, indent=2))
        return
    mib = data["disk_bytes"] / 1048576
    rows = [
        ("vault", data["vault"]),
        ("total entries", str(data["total_entries"])),
        ("archived", str(data["archived"])),
        ("unique link targets", str(data["unique_link_targets"])),
        ("disk size", f"{mib:.1f} MiB"),
    ]
    for entry_type, count in data["by_type"].items():
        rows.append((f"  {entry_type}", str(count)))
    unclassified = data["total_entries"] - data["classified"]
    if unclassified:
        rows.append(("  (unclassified) ⚠️", str(unclassified)))
    if data["fade_warning"]:
        mark = " ⚠️" if data["suggest_groom"] else ""
        rows.append((f"fading (≤{FADE_WARN_AT}){mark}", str(len(data["fade_warning"]))))
    if data["orphans"]:
        rows.append(("orphans ⚠️", str(len(data["orphans"]))))
    if data["unresolved_links"]:
        rows.append(("unresolved links", str(len(data["unresolved_links"]))))
    if data["invalid_frontmatter"]:
        rows.append(("invalid frontmatter ⚠️", str(len(data["invalid_frontmatter"]))))
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        print(f"{label.ljust(width)}  {value}")
    if data["suggest_groom"]:
        print(f"\n⚠️  {len(data['fade_warning'])} entries near the archive threshold — run groom.")
    if data["suggest_audit"]:
        print("⚠️  Integrity issues found — run audit.")


# --- tags --------------------------------------------------------------------


def collect_tags() -> dict[str, int]:
    counts: dict[str, int] = {}
    for _, front, _ in iter_entries():
        if front is None:
            continue
        for tag in (t.strip().lstrip("#") for t in front.get("tags", "").strip("[]").split(",")):
            if tag:
                counts[tag] = counts.get(tag, 0) + 1
    return counts


def cmd_tags(args: argparse.Namespace) -> None:
    """List the vocabulary already in use, so a new entry can join it.

    A category used two ways is worse than no category — `infra/nginx` and
    `tool/nginx` split the same knowledge into two tag queries that each look
    complete. Reading the existing counts before writing is what keeps that from
    happening, and it is cheaper than noticing it a hundred entries later.
    """
    counts = collect_tags()
    if args.json:
        import json

        print(json.dumps(dict(sorted(counts.items())), indent=2))
        return
    if not counts:
        print("no tags yet — the vocabulary starts with this entry")
        return
    width = max(len(tag) for tag in counts)
    for tag, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{tag.ljust(width)}  {count}")


# --- audit -------------------------------------------------------------------


def cmd_audit(args: argparse.Namespace) -> None:
    slugs = {p.stem for p in entries_dir().glob("*.md")} if entries_dir().exists() else set()
    archived = (
        {p.stem for p in (VAULT / "archive").glob("*.md")}
        if (VAULT / "archive").exists()
        else set()
    )
    known = slugs | archived
    data = collect_stats()

    broken_moc: list[tuple[Path, str]] = []
    for path in sorted((VAULT / "maps").glob("*.md")):
        for target in _WIKILINK_RE.findall(path.read_text(encoding="utf-8")):
            target = target.strip()
            if _DATED_SLUG_RE.match(target) and target not in known:
                broken_moc.append((path, target))

    stale_daily: list[tuple[Path, str]] = []
    for path in sorted((VAULT / "daily").glob("*.md")):
        for target in _WIKILINK_RE.findall(path.read_text(encoding="utf-8")):
            target = target.strip()
            if _DATED_SLUG_RE.match(target) and target not in known:
                stale_daily.append((path, target))

    # Only bookkeeping damage is mechanically fixable. A body wiki-link pointing
    # at a deleted entry, or frontmatter that no longer parses, needs a decision
    # about what the text meant — that stays with the agent.
    findings = [
        ("orphan entries (in no MOC)", data["orphans"], True),
        ("broken MOC references", [f"{p.name}: {t}" for p, t in broken_moc], True),
        ("stale daily references", [f"{p.name}: {t}" for p, t in stale_daily], True),
        ("broken wiki-links in entries", data["unresolved_links"], False),
        ("invalid frontmatter", data["invalid_frontmatter"], False),
    ]
    print(f"{'check'.ljust(30)}  count")
    for label, items, _ in findings:
        print(f"{label.ljust(30)}  {len(items)}")
    for label, items, _ in findings:
        if items:
            print(f"\n{label}:")
            for item in items:
                print(f"  - {item}")

    manual = [label for label, items, fixable in findings if items and not fixable]
    if not args.fix:
        if any(items for _, items, fixable in findings if fixable):
            print("\nRe-run with --fix to remove broken references and re-index orphans.")
        if manual:
            print(f"\nNeeds a judgment call, not --fix: {', '.join(manual)}.")
        return

    for path, target in broken_moc + stale_daily:
        drop_lines_mentioning(path, target)
    for stem in data["orphans"]:
        front, body = parse_entry(entries_dir() / f"{stem}.md")
        if front and front.get("type") in ALL_TYPES:
            # Re-index under the entry's own summary rather than a placeholder: the
            # MOC line is what recall reads, so a re-indexed orphan should be as
            # findable as one that was never lost.
            summary = entry_summary(front, body, stem)
            insert_under(moc_path(front["type"]), "## Recent", f"- [[{stem}]] — {summary}")
    print(f"\nfixed: {len(broken_moc) + len(stale_daily)} broken references removed, "
          f"{len(data['orphans'])} orphans re-indexed")
    if manual:
        print(f"still needs a judgment call: {', '.join(manual)}.")


# --- self-check --------------------------------------------------------------


def selfcheck() -> None:
    """Guard the decay model: how often groom runs must barely affect the result.

    The original formula decayed from last_accessed without recording that it had
    run, so every pass re-applied the whole idle window. Fourteen daily grooms
    took a fresh entry from 100 down to ~12 — past the archive threshold — while
    a single pass on day 14 left it at 75. Cadence, not time, decided what the
    vault forgot.

    Anchoring on decayed_at bounds that spread to the rounding error alone.
    """
    single = decayed_salience(SALIENCE_NEW, 14)
    assert single == 75, single

    daily = SALIENCE_NEW
    for _ in range(14):
        daily = decayed_salience(daily, 1)
    weekly = decayed_salience(decayed_salience(SALIENCE_NEW, 7), 7)

    # Salience is a strength heuristic, not a ledger, so bounded agreement is the
    # invariant worth holding — floor() truncates on every pass, which costs up
    # to 1 point per run.
    # ponytail: drift ceiling ~1/run; store salience as a float if it matters.
    for label, value, runs in (("weekly", weekly, 2), ("daily", daily, 14)):
        assert value <= single, (label, value, single)
        assert single - value <= runs, f"{label} cadence drifted {single - value} (max {runs})"
        assert value > ARCHIVE_AT, f"{label} groom archived a 14-day-old entry: {value}"

    assert decayed_salience(SALIENCE_NEW, 0) == SALIENCE_NEW, "no idle days must not decay"
    assert decayed_salience(SALIENCE_NEW, -3) == SALIENCE_NEW, "clock skew must not decay"
    assert decayed_salience(5, 999) == 0, "decay must bottom out at 0"

    assert normalize_tags("#lang/python, infra/docker", "bug") == [
        "type/bug", "lang/python", "infra/docker",
    ], "frontmatter tags must not carry '#' — it is invalid YAML"
    assert normalize_tags("type/bug", "bug") == ["type/bug"], "type tag must not duplicate"

    assert PERMANENT_TYPES.isdisjoint(FADEABLE_TYPES), "a type cannot be both permanent and fadeable"

    check_index_editing()
    check_orphan_detection()
    check_stats_accounting()
    print(f"selfcheck ok (100 salience, 14 idle days: 1 run={single}, 2 runs={weekly}, 14 runs={daily})")


def check_index_editing() -> None:
    """Guard the index editors against prefix collisions and label churn.

    Matching a slug as a substring meant archiving `...-cors` also deleted the
    bullet for `...-cors-fix` from the MOC, the daily note and the index. The
    victim then read as an orphan, so audit --fix would re-index it under a
    placeholder summary — losing the original wording too.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        moc = Path(tmp) / "notes.md"
        moc.write_text(
            "# Notes\n\n## Recent\n\n"
            "- [[2026-01-01-cors-fix]] — the sibling\n"
            "- [[2026-01-01-cors]] — the victim\n"
            "- [[2026-01-01-cors|aliased]] — alias form\n",
            encoding="utf-8",
        )
        assert drop_lines_mentioning(moc, "2026-01-01-cors") == 2, "alias form must also be dropped"
        assert "cors-fix" in moc.read_text(), "prefix collision deindexed a sibling entry"

        daily = Path(tmp) / "2026-01-01.md"
        daily.write_text(
            "# 2026-01-01\n\n## Entries\n\n- [[2026-01-01-cors]] — old wording (bug)\n",
            encoding="utf-8",
        )
        assert relabel_lines_linking(daily, "2026-01-01-cors", "new wording") == 1
        assert daily.read_text().rstrip().endswith("— new wording (bug)"), (
            "relabel must keep the daily note's type marker"
        )

        entry = Path(tmp) / "2026-01-01-target.md"
        entry.write_text('---\ntype: bug\nrelated: []\n---\n\n# T\n', encoding="utf-8")
        assert add_related(entry, "2026-01-02-source") is True
        assert add_related(entry, "2026-01-02-source") is False, "backlink must not duplicate"
        assert 'related: ["[[2026-01-02-source]]"]' in entry.read_text()

    assert yaml_str('fixed CORS: only on "502"') == '"fixed CORS: only on \\"502\\""'


def check_orphan_detection() -> None:
    """An entry is indexed only if a MOC links to it — not if its slug appears.

    Deciding that by substring meant `...-cors` counted as indexed because
    `...-cors-fix` had a line: stats reported zero orphans, audit had nothing to
    re-index, and the entry stayed unreachable from every MOC with no signal at
    all. The same prefix collision `links_to` already guards against, one layer
    up, and the quieter of the two failures.
    """
    global VAULT
    import tempfile

    original = VAULT
    with tempfile.TemporaryDirectory() as tmp:
        VAULT = Path(tmp)
        try:
            entries_dir().mkdir(parents=True)
            (VAULT / "maps").mkdir(parents=True)
            for stem in ("2026-01-01-cors", "2026-01-01-cors-fix"):
                (entries_dir() / f"{stem}.md").write_text(
                    '---\ntype: note\nsalience: 100\nsummary: "s"\n---\n\n# S\n',
                    encoding="utf-8",
                )
            moc_path("note").write_text(
                "# Notes\n\n## Recent\n\n- [[2026-01-01-cors-fix]] — the indexed one\n",
                encoding="utf-8",
            )
            orphans = collect_stats()["orphans"]
            assert orphans == ["2026-01-01-cors"], f"prefix collision hid an orphan: {orphans}"
        finally:
            VAULT = original


def check_stats_accounting() -> None:
    """Every file in entries/ is either classified by type or reported as invalid.

    `total_entries` counts files on disk while `by_type` can only count entries
    whose frontmatter parses, so the two are not meant to match. Holding
    classified + invalid == total is what makes the gap a reported number rather
    than a discrepancy the reader has to explain.
    """
    global VAULT
    import tempfile

    original = VAULT
    with tempfile.TemporaryDirectory() as tmp:
        VAULT = Path(tmp)
        try:
            entries_dir().mkdir(parents=True)
            (entries_dir() / "2026-01-01-ok.md").write_text(
                "---\ntype: bug\nsalience: 100\n---\n\n# Ok\n", encoding="utf-8"
            )
            (entries_dir() / "2026-01-02-typo.md").write_text(
                "---\ntpye: bug\n---\n\n# Typo in the key\n", encoding="utf-8"
            )
            (entries_dir() / "2026-01-03-none.md").write_text("no frontmatter\n", encoding="utf-8")
            data = collect_stats()
            assert data["total_entries"] == 3, data["total_entries"]
            assert data["classified"] == 1, data["classified"]
            assert len(data["invalid_frontmatter"]) == 2, data["invalid_frontmatter"]
            assert data["classified"] + len(data["invalid_frontmatter"]) == data["total_entries"]
        finally:
            VAULT = original

    assert read_body("inline") == "inline"
    # Substituting stdin rather than reading the real one: under CI or a
    # background shell the process inherits an open pipe nobody ever closes, and
    # asserting against it hung the whole selfcheck instead of checking anything.
    import io

    real_stdin, sys.stdin = sys.stdin, io.StringIO("piped body\n")
    try:
        assert read_body(None) == "piped body\n", "piped stdin must be read without --body"
    finally:
        sys.stdin = real_stdin


# --- CLI ---------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selfcheck", action="store_true", help="verify the decay model and exit")
    sub = parser.add_subparsers(dest="command")

    write = sub.add_parser("write", help="create an entry and index it everywhere")
    write.add_argument("--type", required=True, choices=ALL_TYPES)
    write.add_argument("--slug", required=True, help="kebab-case, max 6 words, no date prefix")
    write.add_argument("--title")
    write.add_argument("--summary", help="one line for the MOC, daily note and index")
    write.add_argument("--project", default="")
    write.add_argument("--tags", default="", help="comma-separated, no '#'")
    write.add_argument("--related", default="", help="comma-separated entry slugs")
    write.add_argument("--status")
    write.add_argument("--body", help="entry body; '-' forces stdin, piped stdin is read anyway")
    write.add_argument("--force", action="store_true")
    write.set_defaults(func=cmd_write)

    touch = sub.add_parser("touch", help="reconsolidate entries that proved useful")
    touch.add_argument("entries", nargs="+")
    touch.set_defaults(func=cmd_touch)

    search = sub.add_parser("search", help="rank entries matching any of the given terms")
    search.add_argument("terms", nargs="+", help="key terms plus likely synonyms")
    search.add_argument("--project", help="restrict to one project slug")
    search.add_argument("--type", choices=ALL_TYPES, help="restrict to one entry type")
    search.add_argument(
        "--include-archived", action="store_true",
        help="also rank entries groom has archived (marked [archived])",
    )
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    relate = sub.add_parser("relate", help="link an entry to siblings, both directions")
    relate.add_argument("--slug", required=True)
    relate.add_argument("--related", required=True, help="comma-separated entry slugs")
    relate.set_defaults(func=cmd_relate)

    reindex = sub.add_parser("reindex", help="push an entry's summary back out to every index")
    reindex.add_argument("--slug", required=True)
    reindex.add_argument("--summary", help="new one-line summary; omit to re-push the current one")
    reindex.set_defaults(func=cmd_reindex)

    groom = sub.add_parser("groom", help="fade idle transient entries, archive the spent ones")
    groom.add_argument("--dry-run", action="store_true")
    groom.set_defaults(func=cmd_groom)

    restore = sub.add_parser("restore", help="bring an archived entry back and re-index it")
    restore.add_argument("slug")
    restore.set_defaults(func=cmd_restore)

    stats = sub.add_parser("stats", help="counts and health signals")
    stats.add_argument("--json", action="store_true")
    stats.set_defaults(func=cmd_stats)

    tags = sub.add_parser("tags", help="the tag vocabulary already in use, with counts")
    tags.add_argument("--json", action="store_true")
    tags.set_defaults(func=cmd_tags)

    audit = sub.add_parser("audit", help="integrity checks across entries, MOCs and daily notes")
    audit.add_argument("--fix", action="store_true")
    audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    if args.selfcheck:
        selfcheck()
        return
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
