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


# --- sync-two-machines -------------------------------------------------------


def eval_sync_two_machines() -> None:
    """Two clones of one remote write and touch concurrently, then both sync.

    The bookkeeping must merge on its own; only a prose edit on both sides may
    stop the sync, and a vault with no repository must be left alone.
    """
    import tempfile

    name = "sync-two-machines"
    root = Path(tempfile.mkdtemp(prefix="mentat-sync-"))
    sh = lambda *a, cwd=root: subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=True)

    plain = build("empty")
    out = vault_py(plain, "sync")
    check(name, "a vault without git is left alone", out.startswith("sync off:") and not (plain / ".git").exists(), out.strip())

    sh("git", "init", "-q", "--bare", "-b", "main", "remote.git")
    first = build("cors")
    sh("git", "init", "-q", "-b", "main", cwd=first)
    sh("git", "remote", "add", "origin", str(root / "remote.git"), cwd=first)
    for repo in (first,):
        sh("git", "config", "user.email", "t@t", cwd=repo)
        sh("git", "config", "user.name", "t", cwd=repo)
    vault_py(first, "sync")  # no upstream yet: must refuse, not push
    sh("git", "add", "-A", cwd=first)
    sh("git", "commit", "-q", "-m", "seed", cwd=first)
    sh("git", "push", "-q", "-u", "origin", "main", cwd=first)
    vault_py(first, "sync")  # installs .gitattributes and the driver
    second = root / "second"
    sh("git", "clone", "-q", str(root / "remote.git"), str(second))
    sh("git", "config", "user.email", "t@t", cwd=second)
    sh("git", "config", "user.name", "t", cwd=second)

    slug = next(p.stem for p in (first / "entries").glob("*.md") if "cors" in p.stem)
    before = frontmatter(first / "entries" / f"{slug}.md")
    vault_py(first, "touch", slug)
    vault_py(second, "touch", slug)
    vault_py(second, "touch", slug)
    vault_py(first, "write", "--type", "note", "--slug", "from-first", "--summary", "first", stdin="- a\n")
    vault_py(second, "write", "--type", "note", "--slug", "from-second", "--summary", "second", stdin="- b\n")

    vault_py(first, "sync")
    out = vault_py(second, "sync")
    vault_py(first, "sync")
    check(name, "concurrent touches and writes merge without stopping", "sync ok" in out, out.strip())

    for label, repo in (("first", first), ("second", second)):
        front = frontmatter(repo / "entries" / f"{slug}.md")
        check(
            name, f"{label}: usage_count counts all three touches",
            int(front.get("usage_count", 0)) == int(before.get("usage_count", 0)) + 3,
            f"before={before.get('usage_count')} after={front.get('usage_count')}",
        )
        notes = (repo / "maps" / "notes.md").read_text()
        check(name, f"{label}: both new notes indexed once", notes.count("from-first]]") == 1 and notes.count("from-second]]") == 1, notes)
        check(name, f"{label}: no conflict markers left", "<<<<<<<" not in "".join(p.read_text() for p in repo.rglob("*.md")))

    (first / "profile.md").write_text("# Profile\n\n- first machine\n", encoding="utf-8")
    (second / "profile.md").write_text("# Profile\n\n- second machine\n", encoding="utf-8")
    vault_py(first, "sync")
    stopped = subprocess.run(
        [sys.executable, str(VAULT_PY), "sync"], env={**os.environ, "MENTAT_VAULT": str(second)},
        capture_output=True, text=True,
    )
    check(name, "prose edited on both machines stops the sync", stopped.returncode != 0 and "profile.md" in stopped.stdout, stopped.stdout + stopped.stderr)


# --- sync-topics --------------------------------------------------------------


def eval_sync_topics() -> None:
    """Only allowed topics leave the machine; the local ones stay whole at home.

    Nothing about a local entry may reach the remote — not its file, its index
    bullets, its slug in a link — while this machine keeps all of it, across a
    merge that rewrites the files it was stripped from.
    """
    import tempfile

    name = "sync-topics"
    root = Path(tempfile.mkdtemp(prefix="mentat-topics-"))
    sh = lambda *a, cwd=root: subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=True)
    sh("git", "init", "-q", "--bare", "-b", "main", "remote.git")
    first = build("empty")
    sh("git", "init", "-q", "-b", "main", cwd=first)
    sh("git", "remote", "add", "origin", str(root / "remote.git"), cwd=first)
    for key, value in (("user.email", "t@t"), ("user.name", "t")):
        sh("git", "config", key, value, cwd=first)

    vault_py(first, "write", "--type", "learning", "--slug", "java-records", "--summary", "records are final",
             "--project", "estudos", "--tags", "lang/java", stdin="- shared\n")
    vault_py(first, "write", "--type", "bug", "--slug", "waf-cliente-x", "--summary", "WAF do cliente X bloqueia",
             "--project", "cliente-x", "--tags", "lang/java", stdin="- private\n")
    vault_py(first, "write", "--type", "learning", "--slug", "cliente-x-usa-java", "--summary", "cliente X usa Java",
             "--project", "estudos", "--tags", "lang/java, cliente/x", stdin="- denied by tag\n")
    shared = next(p.stem for p in (first / "entries").glob("*java-records.md"))
    private = next(p.stem for p in (first / "entries").glob("*waf-cliente-x.md"))
    denied = next(p.stem for p in (first / "entries").glob("*cliente-x-usa-java.md"))
    vault_py(first, "relate", "--slug", shared, "--related", private)
    entry = first / "entries" / f"{shared}.md"
    entry.write_text(entry.read_text() + f"\nSee [[{private}]].\n", encoding="utf-8")
    (first / "sync-topics").write_text("estudos\n!cliente/*\n", encoding="utf-8")

    sh("git", "add", "sync-topics", cwd=first)
    sh("git", "commit", "-q", "-m", "seed", cwd=first)
    sh("git", "push", "-q", "-u", "origin", "main", cwd=first)
    out = vault_py(first, "sync")
    check(name, "sync reports the entries kept local", "2 entries kept on this machine" in out, out.strip())

    tree = sh("git", "ls-tree", "-r", "--name-only", "origin/main", cwd=first).stdout
    leaked = subprocess.run(["git", "grep", "-l", "-e", "waf-cliente-x", "-e", "cliente-x-usa-java",
                             "-e", "WAF do cliente", "origin/main", "--", "."], cwd=first, capture_output=True, text=True)
    check(name, "the shared entry reaches the remote", f"entries/{shared}.md" in tree, tree)
    check(name, "no local entry file reaches the remote", private not in tree and denied not in tree, tree)
    check(name, "no slug or summary of a local entry reaches the remote", not leaked.stdout.strip(), leaked.stdout)

    def whole(repo: Path) -> bool:
        text = "".join((repo / f).read_text() for f in ("maps/bugs.md", "index.md", f"entries/{shared}.md"))
        return (repo / "entries" / f"{private}.md").exists() and text.count(private) == 4

    check(name, "this machine keeps the local entry, its bullets and links", whole(first),
          (first / "maps/bugs.md").read_text())

    second = root / "second"
    sh("git", "clone", "-q", str(root / "remote.git"), str(second))
    for key, value in (("user.email", "t@t"), ("user.name", "t")):
        sh("git", "config", key, value, cwd=second)
    # Two touches, not one: identical files on both sides never reach the merge
    # driver, so a single same-day touch on each machine counts once — git's limit.
    vault_py(second, "touch", shared)
    vault_py(second, "touch", shared)
    vault_py(second, "write", "--type", "learning", "--slug", "from-second", "--summary", "second",
             "--project", "estudos", stdin="- b\n")
    vault_py(second, "sync")
    vault_py(first, "touch", shared)
    out = vault_py(first, "sync")
    check(name, "a merge over stripped files still syncs", "sync ok" in out, out.strip())
    check(name, "the local lines survive a merge that rewrote their files", whole(first),
          (first / f"entries/{shared}.md").read_text())
    usage = int(frontmatter(entry).get("usage_count", 0))
    check(name, "the other machine's change arrives", usage == 3 and "from-second" in (first / "index.md").read_text(),
          f"usage_count={usage}")
    check(name, "the second machine never sees the local entry", private not in
          "".join(p.read_text() for p in second.rglob("*.md") if ".git" not in p.parts))

    sh("git", "add", "-A", cwd=first)
    manual = subprocess.run(["git", "commit", "-q", "-m", "by hand"], cwd=first, capture_output=True, text=True)
    check(name, "a commit by hand that carries a local entry is refused",
          manual.returncode != 0 and "refusing to commit" in manual.stderr, manual.stderr.strip())
    sh("git", "reset", "-q", cwd=first)

    (first / "sync-topics").write_text("estudos\n!cliente/*\n!lang/*\n", encoding="utf-8")
    vault_py(first, "sync")
    out = vault_py(second, "sync")
    gone = sh("git", "ls-tree", "-r", "--name-only", "origin/main", cwd=first).stdout
    check(name, "a topic withdrawn from sync leaves the remote", f"entries/{shared}.md" not in gone, gone)
    check(name, "the other machine keeps a withdrawn entry on disk", (second / "entries" / f"{shared}.md").exists(), out)


# --- setup-opt-in -------------------------------------------------------------


def eval_setup_opt_in() -> None:
    """Mentat becomes the main memory only where chosen, and uninstall undoes it.

    The person's own instructions and the vault must survive both directions.
    """
    import tempfile

    name = "setup-opt-in"
    home = Path(tempfile.mkdtemp(prefix="mentat-home-"))
    for d in (".claude/projects/p/memory", ".codex"):
        (home / d).mkdir(parents=True)
    own = "# my rules\n\n- keep this\n"
    (home / ".codex/AGENTS.md").write_text(own, encoding="utf-8")
    (home / ".claude/CLAUDE.md").write_text(own, encoding="utf-8")
    memory = home / ".claude/projects/p/memory/MEMORY.md"
    memory.write_text("- original index\n", encoding="utf-8")

    def setup(*args: str) -> str:
        done = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts/setup.py"), "--no-timer", *args],
            env={**os.environ, "HOME": str(home), "MENTAT_VAULT": str(home / ".mentat")},
            capture_output=True, text=True,
        )
        if done.returncode:
            raise RuntimeError(f"setup.py {' '.join(args)} failed: {done.stderr.strip()}")
        return done.stdout

    setup("--agents", "codex")
    codex, claude = (home / ".codex/AGENTS.md").read_text(), (home / ".claude/CLAUDE.md").read_text()
    check(name, "chosen agent gets the pointer block", "mentat:start" in codex, codex)
    check(name, "agent left out keeps its file untouched", claude == own, claude)
    check(name, "agent left out still gets the skill to consult", (home / ".claude/skills/mentat").exists())

    setup("--agents", "none")
    check(name, "--agents none adds nothing", (home / ".claude/CLAUDE.md").read_text() == own)

    setup()
    memory.rename(memory.with_name("MEMORY.md.pre-mentat"))  # what Absorb leaves behind
    memory.write_text("memory lives in the Mentat vault\n", encoding="utf-8")
    setup("--uninstall")
    check(name, "uninstall restores each file to exactly what it was",
          all((home / f).read_text() == own for f in (".codex/AGENTS.md", ".claude/CLAUDE.md")),
          (home / ".codex/AGENTS.md").read_text())
    check(name, "uninstall restores the pre-Mentat MEMORY.md", memory.read_text() == "- original index\n", memory.read_text())
    check(name, "uninstall keeps the vault", (home / ".mentat/entries").is_dir())

    remote = home / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    env = {**os.environ, "HOME": str(home), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    vault_py(home / ".mentat", "write", "--type", "bug", "--slug", "segredo-cliente", "--project", "cliente-x",
             "--summary", "segredo do cliente", stdin="- x\n")
    (home / ".mentat/sync-topics").write_text("estudos\n", encoding="utf-8")
    published = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts/setup.py"), "--no-timer", "--agents", "none", "--remote", str(remote)],
        env={**env, "MENTAT_VAULT": str(home / ".mentat")}, capture_output=True, text=True,
    )
    leaked = subprocess.run(["git", f"--git-dir={remote}", "grep", "-l", "segredo", "main", "--", "."],
                            capture_output=True, text=True).stdout
    check(name, "the first publish leaves local topics out", published.returncode == 0 and not leaked,
          published.stderr + leaked)
    check(name, "the first publish keeps local topics on this machine",
          "segredo" in (home / ".mentat/maps/bugs.md").read_text(), (home / ".mentat/maps/bugs.md").read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-v", "--verbose", action="store_true", help="show evidence for passes too")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    for runner in (
        eval_remember_a_bug, eval_groom, eval_groom_cadence,
        eval_amend_preserves_identity, eval_stats, eval_orphan_prefix,
        eval_archive_round_trip, eval_prefix_collision, eval_sync_two_machines, eval_sync_topics,
        eval_setup_opt_in,
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
