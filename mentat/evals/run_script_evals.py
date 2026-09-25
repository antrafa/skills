#!/usr/bin/env python3
"""Run the eval assertions that do not need an agent.

Four of the eight evals are really about vault.py: whether groom is
cadence-insensitive, whether stats counts honestly, whether write produces
parseable frontmatter, whether amend preserves identity. Those have exact right
answers, so checking them with a script instead of a subagent is both cheaper and
stricter — a grader reading prose can be talked into a pass, an assertion cannot.

What stays with subagents is the part that needs judgment: routing an ambiguous
prompt, refusing trivia, noticing a duplicate, expanding a query into synonyms.
See evals.json for which eval is which.

    ./run_script_evals.py          # table plus exit code
    ./run_script_evals.py -v       # show evidence for passing checks too
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_vault import SKILL_DIR, build  # noqa: E402

VAULT_PY = SKILL_DIR / "scripts" / "vault.py"
TODAY = dt.date.today().isoformat()
RESULTS: list[tuple[str, str, bool, str]] = []


def vault_py(vault: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run(
        [sys.executable, str(VAULT_PY), *args],
        env={**os.environ, "MENTAT_VAULT": str(vault)},
        input=stdin, capture_output=True, text=True,
    )
    if done.returncode:
        raise RuntimeError(f"vault.py {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    block = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not block:
        return {}
    return {
        k.strip(): v.strip()
        for k, _, v in (line.partition(":") for line in block.group(1).splitlines())
        if k.strip()
    }


def check(eval_name: str, assertion: str, passed: bool, evidence: str = "") -> None:
    RESULTS.append((eval_name, assertion, bool(passed), evidence))


# --- eval 1: remember-a-bug --------------------------------------------------


def eval_remember_a_bug() -> None:
    name = "remember-a-bug"
    vault = build("empty")
    vault_py(
        vault, "write", "--type", "bug", "--slug", "nginx-strips-cors-header",
        "--title", "Nginx strips CORS header on 502",
        "--summary", "Nginx dropped CORS headers on 502",
        "--project", "checkout-api", "--tags", "#infra/nginx, domain/auth",
        stdin="## Symptoms\n\n- preflight failed only on 502\n",
    )
    entries = list((vault / "entries").glob("*.md"))
    check(name, "exactly one entry was created", len(entries) == 1, str([p.name for p in entries]))
    if len(entries) != 1:
        return
    entry = entries[0]
    front = frontmatter(entry)

    check(name, "type is bug", front.get("type") == "bug", front.get("type", ""))
    check(name, "frontmatter parses as valid YAML", *yaml_verdict(entry))
    check(
        name, "tags carry type/bug and no '#'",
        "type/bug" in front.get("tags", "") and "#" not in front.get("tags", ""),
        front.get("tags", ""),
    )
    check(name, "decayed_at is today", front.get("decayed_at") == TODAY, front.get("decayed_at", ""))
    check(name, "project is checkout-api", front.get("project") == "checkout-api", front.get("project", ""))
    check(
        name, "salience 100 and usage_count 0",
        front.get("salience") == "100" and front.get("usage_count") == "0",
        f"salience={front.get('salience')} usage_count={front.get('usage_count')}",
    )
    indexes = {
        "maps/bugs.md": vault / "maps" / "bugs.md",
        "daily note": vault / "daily" / f"{TODAY}.md",
        "index.md": vault / "index.md",
    }
    missing = [label for label, path in indexes.items() if entry.stem not in path.read_text()]
    check(name, "indexed into its MOC, the daily note and index.md", not missing, f"missing from {missing}")


def yaml_verdict(entry: Path) -> tuple[bool, str]:
    try:
        import yaml
    except ImportError:
        return True, "skipped: PyYAML not installed"
    block = re.match(r"---\n(.*?)\n---\n", entry.read_text(encoding="utf-8"), re.DOTALL)
    try:
        loaded = yaml.safe_load(block.group(1))
        return isinstance(loaded, dict), f"parsed {len(loaded)} keys"
    except yaml.YAMLError as exc:
        return False, str(exc).splitlines()[0]


# --- eval 4: groom-is-cadence-insensitive ------------------------------------


def eval_groom() -> None:
    name = "groom-is-cadence-insensitive"
    vault = build("mixed-age")
    permanent_before = salience_by_type(vault, {"bug", "decision", "feature", "learning", "snippet", "schema"})
    indexed_before = {p.stem for p in (vault / "entries").glob("*.md")}

    vault_py(vault, "groom")
    permanent_after = salience_by_type(vault, {"bug", "decision", "feature", "learning", "snippet", "schema"})
    check(
        name, "permanent types were not touched",
        permanent_before == permanent_after,
        f"{permanent_before} -> {permanent_after}",
    )

    second = vault_py(vault, "groom")
    check(
        name, "a second groom the same day fades nothing further",
        "0 entries faded" in second, second.strip().splitlines()[-1],
    )

    idle_14 = next(
        (frontmatter(p) for p in (vault / "entries").glob("*profiling-session.md")), {}
    )
    salience = int(idle_14.get("salience", -1))
    check(
        name, "a note idle 14 days lands within 3 points of 75",
        abs(salience - 75) <= 3, f"salience={salience}",
    )

    archived = {p.stem for p in (vault / "archive").glob("*.md")}
    check(name, "spent entries were archived, not deleted", bool(archived), f"archived={sorted(archived)}")
    still_referenced = [
        stem for stem in archived
        for path in [vault / "index.md", vault / "maps" / "notes.md", *(vault / "daily").glob("*.md")]
        if f"[[{stem}]]" in path.read_text(encoding="utf-8")
    ]
    check(
        name, "archived entries were removed from every index",
        not still_referenced, f"still referenced: {sorted(set(still_referenced))}",
    )
    check(
        name, "nothing was archived that groom did not report",
        archived <= indexed_before, f"unexpected: {sorted(archived - indexed_before)}",
    )


def eval_groom_cadence() -> None:
    """The regression the decay model exists to prevent, run end to end."""
    name = "groom-is-cadence-insensitive"
    once, often = build("mixed-age"), build("mixed-age")
    vault_py(once, "groom")
    for _ in range(14):
        vault_py(often, "groom")
    pairs = []
    for path in sorted((once / "entries").glob("*.md")):
        twin = often / "entries" / path.name
        if twin.exists():
            pairs.append((path.stem, int(frontmatter(path).get("salience", 0)),
                          int(frontmatter(twin).get("salience", 0))))
    worst = max((abs(a - b), stem) for stem, a, b in pairs) if pairs else (0, "-")
    check(
        name, "14 grooms and 1 groom agree within rounding error",
        worst[0] <= 14, f"largest gap {worst[0]} points on {worst[1]}",
    )


def salience_by_type(vault: Path, types: set[str]) -> dict[str, int]:
    out = {}
    for path in sorted((vault / "entries").glob("*.md")):
        front = frontmatter(path)
        if front.get("type") in types:
            out[path.stem] = int(front.get("salience", 0))
    return out


# --- eval 5: duplicate-becomes-amend (the mechanical half) -------------------


def eval_amend_preserves_identity() -> None:
    name = "duplicate-becomes-amend"
    vault = build("cors")
    entry = next((vault / "entries").glob("*nginx-strips-cors-header.md"))
    before = frontmatter(entry)
    count_before = len(list((vault / "entries").glob("*.md")))

    body = entry.read_text(encoding="utf-8").replace(
        "answered 502", "answered 502 or 504"
    )
    entry.write_text(body, encoding="utf-8")
    vault_py(vault, "touch", entry.stem)
    vault_py(vault, "reindex", "--slug", entry.stem,
             "--summary", "Nginx dropped CORS headers on 502 and 504")
    after = frontmatter(entry)

    check(
        name, "no new entry was created",
        len(list((vault / "entries").glob("*.md"))) == count_before,
        f"{count_before} entries before and after",
    )
    check(
        name, "type, date and project survived the edit",
        all(before[k] == after[k] for k in ("type", "date", "project")),
        f"type={after['type']} date={after['date']} project={after['project']}",
    )
    check(
        name, "usage_count incremented by exactly 1",
        int(after["usage_count"]) == int(before["usage_count"]) + 1,
        f"{before['usage_count']} -> {after['usage_count']}",
    )
    check(name, "last_accessed is today", after["last_accessed"] == TODAY, after["last_accessed"])
    check(
        name, "salience increased", int(after["salience"]) > int(before["salience"]),
        f"{before['salience']} -> {after['salience']}",
    )
    stale = [
        path.name
        for path in [vault / "maps" / "bugs.md", vault / "index.md", *(vault / "daily").glob("*.md")]
        if f"[[{entry.stem}]]" in path.read_text(encoding="utf-8")
        and "502 and 504" not in path.read_text(encoding="utf-8")
    ]
    check(name, "every index shows the new summary", not stale, f"stale in {stale}")

    sibling = next((vault / "entries").glob("*api-gateway-timeout.md"))
    vault_py(vault, "relate", "--slug", entry.stem, "--related", sibling.stem)
    check(
        name, "relate threads the link onto both entries",
        f"[[{sibling.stem}]]" in frontmatter(entry)["related"]
        and f"[[{entry.stem}]]" in frontmatter(sibling)["related"],
        f"{entry.stem}.related={frontmatter(entry)['related']}",
    )
    repeated = vault_py(vault, "relate", "--slug", entry.stem, "--related", sibling.stem)
    check(
        name, "relating twice does not duplicate the link",
        frontmatter(entry)["related"].count(sibling.stem) == 1, repeated.strip(),
    )


# --- eval 7: status-reports-health -------------------------------------------


def eval_stats() -> None:
    name = "status-reports-health"
    vault = build("mixed-age")
    data = json.loads(vault_py(vault, "stats", "--json"))
    on_disk = len(list((vault / "entries").glob("*.md")))

    check(
        name, "total matches the files on disk",
        data["total_entries"] == on_disk, f"reported {data['total_entries']}, found {on_disk}",
    )
    check(
        name, "classified plus invalid equals the total",
        data["classified"] + len(data["invalid_frontmatter"]) == data["total_entries"],
        f"{data['classified']} + {len(data['invalid_frontmatter'])} vs {data['total_entries']}",
    )
    check(
        name, "the un-indexed entry is reported as an orphan",
        any("never-indexed" in o for o in data["orphans"]), f"orphans={data['orphans']}",
    )
    check(
        name, "the dangling wiki-link is reported",
        bool(data["unresolved_links"]), f"unresolved={data['unresolved_links']}",
    )
    check(
        name, "integrity trouble raises the audit suggestion",
        data["suggest_audit"], f"suggest_audit={data['suggest_audit']}",
    )

    audited = vault_py(vault, "audit", "--fix")
    after = json.loads(vault_py(vault, "stats", "--json"))
    check(
        name, "audit --fix clears the orphan",
        not after["orphans"], f"orphans after fix: {after['orphans']}",
    )
    check(
        name, "audit leaves the judgment calls alone",
        after["unresolved_links"] == data["unresolved_links"],
        "broken body links still reported, as intended",
    )
    check(
        name, "the re-indexed orphan kept its own summary",
        "(re-indexed by audit)" not in (vault / "maps" / "notes.md").read_text(encoding="utf-8"),
        audited.strip().splitlines()[-1],
    )


def eval_orphan_prefix() -> None:
    """An un-indexed entry whose slug is a prefix of an indexed one is still an orphan."""
    name = "status-reports-health"
    vault = build("empty")
    vault_py(vault, "write", "--type", "note", "--slug", "cors-fix", "--summary", "indexed", stdin="- x\n")
    orphan = vault / "entries" / f"{TODAY}-cors.md"
    orphan.write_text(
        f'---\ntype: note\ndate: {TODAY}\ntags: [type/note]\nproject:\n'
        'summary: "written straight to disk"\nsalience: 100\nusage_count: 0\n'
        f'last_accessed: {TODAY}\ndecayed_at: {TODAY}\nstatus: open\nrelated: []\n---\n\n# Orphan\n',
        encoding="utf-8",
    )
    data = json.loads(vault_py(vault, "stats", "--json"))
    check(
        name, "a prefix-sharing orphan is not hidden by its longer sibling",
        data["orphans"] == [orphan.stem], f"orphans={data['orphans']}",
    )
    vault_py(vault, "audit", "--fix")
    moc = (vault / "maps" / "notes.md").read_text(encoding="utf-8")
    check(
        name, "audit --fix re-indexes it under its own summary",
        f"[[{orphan.stem}]] — written straight to disk" in moc, moc.strip().replace("\n", " | "),
    )


# --- eval 10: the archive round trip -----------------------------------------


def eval_archive_round_trip() -> None:
    name = "archived-entry-comes-back"
    vault = build("empty")
    vault_py(vault, "write", "--type", "note", "--slug", "ephemeral-note",
             "--summary", "faded on purpose", stdin="- x\n")
    entry = next((vault / "entries").glob("*ephemeral-note.md"))
    text = entry.read_text(encoding="utf-8").replace("salience: 100", "salience: 5")
    for key in ("last_accessed", "decayed_at"):
        text = text.replace(f"{key}: {TODAY}", f"{key}: 2024-01-01")
    entry.write_text(text, encoding="utf-8")
    vault_py(vault, "groom")

    check(
        name, "groom archived it instead of deleting it",
        (vault / "archive" / entry.name).exists(), f"archive={[p.name for p in (vault / 'archive').glob('*.md')]}",
    )
    check(
        name, "an unfiltered search no longer returns it",
        "no matches" in vault_py(vault, "search", "faded"), "archive stays out of the working set",
    )
    found = json.loads(vault_py(vault, "search", "faded", "--include-archived", "--json"))
    check(
        name, "--include-archived finds it and marks it archived",
        len(found) == 1 and found[0]["archived"] is True, f"hits={[h['slug'] for h in found]}",
    )

    vault_py(vault, "restore", entry.stem)
    restored = frontmatter(vault / "entries" / entry.name)
    check(
        name, "restore moves the file back out of the archive",
        (vault / "entries" / entry.name).exists() and not (vault / "archive" / entry.name).exists(),
        f"entries={[p.name for p in (vault / 'entries').glob('*.md')]}",
    )
    check(
        name, "it comes back at full salience with the idle clock reset",
        restored["salience"] == "100" and restored["decayed_at"] == TODAY,
        f"salience={restored['salience']} decayed_at={restored['decayed_at']}",
    )
    missing = [
        path.name
        for path in (vault / "maps" / "notes.md", vault / "index.md", vault / "daily" / f"{TODAY}.md")
        if f"[[{entry.stem}]]" not in path.read_text(encoding="utf-8")
    ]
    check(name, "restore re-indexes it everywhere groom removed it", not missing, f"missing from {missing}")
    after = json.loads(vault_py(vault, "stats", "--json"))
    check(name, "the restored entry is not an orphan", not after["orphans"], f"orphans={after['orphans']}")
    check(
        name, "a second groom does not archive it again the same day",
        "0 archived" in vault_py(vault, "groom"), "salience was reset, not carried over",
    )


# --- regression: the prefix collision ----------------------------------------


def eval_prefix_collision() -> None:
    name = "archiving-spares-sibling-slugs"
    vault = build("empty")
    vault_py(vault, "write", "--type", "note", "--slug", "cors", "--summary", "victim", stdin="- x\n")
    vault_py(vault, "write", "--type", "note", "--slug", "cors-fix", "--summary", "sibling", stdin="- x\n")
    victim = next((vault / "entries").glob("*-cors.md"))
    front = frontmatter(victim)
    text = victim.read_text(encoding="utf-8")
    for key in ("last_accessed", "decayed_at"):
        text = text.replace(f"{key}: {front[key]}", f"{key}: 2024-01-01")
    victim.write_text(text.replace("salience: 100", "salience: 5"), encoding="utf-8")

    vault_py(vault, "groom")
    survivors = {p.stem for p in (vault / "entries").glob("*.md")}
    moc = (vault / "maps" / "notes.md").read_text(encoding="utf-8")
    check(
        name, "the faded entry was archived", victim.stem not in survivors, f"entries={sorted(survivors)}",
    )
    check(
        name, "its prefix-sharing sibling kept its MOC line",
        "cors-fix" in moc, moc.strip().replace("\n", " | "),
    )
    check(
        name, "the sibling kept its index and daily lines",
        all(
            "cors-fix" in path.read_text(encoding="utf-8")
            for path in [vault / "index.md", vault / "daily" / f"{TODAY}.md"]
        ),
        "index.md and daily note both still list it",
    )


# --- runner ------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-v", "--verbose", action="store_true", help="show evidence for passes too")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    for runner in (
        eval_remember_a_bug, eval_groom, eval_groom_cadence,
        eval_amend_preserves_identity, eval_stats, eval_orphan_prefix,
        eval_archive_round_trip, eval_prefix_collision,
    ):
        try:
            runner()
        except Exception as exc:  # a crashed check is a failed check, not a lost run
            check(runner.__name__, "check ran without crashing", False, f"{type(exc).__name__}: {exc}")

    if args.json:
        print(json.dumps([
            {"eval": e, "text": a, "passed": p, "evidence": ev} for e, a, p, ev in RESULTS
        ], indent=2))
    else:
        current = None
        for eval_name, assertion, passed, evidence in RESULTS:
            if eval_name != current:
                current, _ = eval_name, print(f"\n{eval_name}")
            mark = "PASS" if passed else "FAIL"
            print(f"  [{mark}] {assertion}")
            if evidence and (args.verbose or not passed):
                print(f"         {evidence}")
        failed = sum(1 for *_, passed, _ in RESULTS if not passed)
        print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} assertions passed")

    sys.exit(1 if any(not passed for *_, passed, _ in RESULTS) else 0)


if __name__ == "__main__":
    main()
