#!/usr/bin/env python3
"""Checks the consistency of the skill's documents.

Three invariants, the ones that have already broken in this repo:

1. Every subcommand in the SKILL.md Intent map appears in README.md and in
   COMMANDS.md. The map is the source; the human guides must cover it. This is
   the one that left the tables stuck at 8 commands while the skill had 14.
2. Every relative link between the documents resolves, file and anchor.
3. The SKILL.md frontmatter follows the Agent Skills spec (agentskills.io):
   kebab-case name up to 64 characters, description up to 1024.

Usage: python3 scripts/check-docs.py     (exit 0 = ok, 1 = inconsistent)
"""

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ["README.md", "COMMANDS.md"]

# Targets that look like broken links but are examples inside a template block.
ILLUSTRATIVE_LINKS = {
    "decisions/2026-09-11-queue-notifications/",
    "references/playbook-<name>.md",
}


def documents():
    return [ROOT / "SKILL.md", *(ROOT / g for g in GUIDES), *sorted((ROOT / "references").rglob("*.md"))]


def map_subcommands(skill_md):
    """Extracts the subcommands from column 2 of the Intent map.

    A row with '—' in that column is a free-form intent, not a command.
    """
    text = skill_md.read_text(encoding="utf-8")
    start = text.index("### Intent map")
    body = text[start:]
    end = body.find("\n### ", 1)
    if end != -1:
        body = body[:end]

    found = []
    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        columns = [c.strip() for c in line.strip("|").split("|")]
        if len(columns) < 2 or columns[1] in ("—", "Subcommand"):
            continue
        for token in re.findall(r"`([^`]+)`", columns[1]):
            name = token.split()[0].strip()  # drop the argument: `dev [<step>]` -> dev
            if name and not name.startswith("<"):
                found.append(name)
    return found


def slug(title):
    s = re.sub(r"[`*_\[\]()]", "", title.strip().lower())
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s.strip())


def anchors(path):
    return {
        slug(m.group(1))
        for m in re.finditer(r"^#{1,6}\s+(.*)$", path.read_text(encoding="utf-8"), re.M)
    }


def check_command_coverage():
    commands = map_subcommands(ROOT / "SKILL.md")
    if not commands:
        return ["SKILL.md: could not read any subcommand from the Intent map"]

    failures = []
    for guide in GUIDES:
        # Only table rows count: describing the command in prose and forgetting the
        # quick-reference table has happened before, and the table is what readers use.
        tables = "\n".join(
            l for l in (ROOT / guide).read_text(encoding="utf-8").splitlines() if l.startswith("|")
        )
        missing = [c for c in commands if f"`{c}" not in tables and f"alterego {c}" not in tables]
        if missing:
            failures.append(f"{guide}: missing from the tables -> {', '.join(sorted(set(missing)))}")
    return failures


def check_links():
    failures = []
    for doc in documents():
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            target = m.group(1)
            if target.startswith(("http://", "https://", "file://", "mailto:")) or target in ILLUSTRATIVE_LINKS:
                continue
            file, _, anchor = target.partition("#")
            dest = (doc.parent / file).resolve() if file else doc
            rel = doc.relative_to(ROOT)
            if file and not dest.exists():
                failures.append(f"{rel}: missing file -> {target}")
                continue
            if anchor and dest.suffix == ".md":
                wanted = unicodedata.normalize("NFC", anchor)
                if wanted not in {unicodedata.normalize("NFC", a) for a in anchors(dest)}:
                    failures.append(f"{rel}: missing anchor -> {target}")
    return failures


def check_frontmatter():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return ["SKILL.md: no YAML frontmatter at the top"]
    fm = m.group(1)
    failures = []
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    if not name or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name.group(1).strip()) or len(name.group(1).strip()) > 64:
        failures.append("SKILL.md: name must be kebab-case, no double hyphen, up to 64 characters")
    desc = re.search(r"^description:\s*>-?\n((?:[ \t]+.*\n?)+)|^description:\s*(.+)$", fm, re.M)
    desc_text = " ".join(l.strip() for l in (desc.group(1) or desc.group(2)).splitlines()) if desc else ""
    if not desc_text or len(desc_text) > 1024:
        failures.append(f"SKILL.md: description must have 1 to 1024 characters (has {len(desc_text)})")
    return failures


def main():
    failures = check_command_coverage() + check_links() + check_frontmatter()
    if failures:
        print("Documentation inconsistent:\n")
        for f in failures:
            print(f"  - {f}")
        print(f"\n{len(failures)} problem(s). The SKILL.md Intent map is the source of the command list.")
        return 1
    print("Documentation consistent: commands covered in the guides, links resolving and frontmatter within spec.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
