#!/usr/bin/env python3
"""Grade the agent-run evals by inspecting the vault each run left behind.

Most of what these evals assert is a fact about files: whether an entry was
created, whether usage_count moved on exactly the right entry, whether the
bootstrap actually ran. Checking that against a freshly generated reference vault
is stricter than asking a grader to read the agent's own account of what it did —
an agent that says it amended and actually duplicated passes the prose check and
fails this one.

The assertions that genuinely need judgment (did the refusal explain itself? was
the query expanded thoughtfully?) are emitted as `needs_review` so they land in
the viewer for a human instead of being guessed at here.

    ./grade_agent_runs.py <workspace>/iteration-N
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_vault import build  # noqa: E402

TODAY = dt.date.today().isoformat()


def front(path: Path) -> dict[str, str]:
    block = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.DOTALL)
    if not block:
        return {}
    return {
        k.strip(): v.strip()
        for k, _, v in (line.partition(":") for line in block.group(1).splitlines())
        if k.strip()
    }


def entries(vault: Path) -> dict[str, Path]:
    directory = vault / "entries"
    return {p.stem: p for p in directory.glob("*.md")} if directory.exists() else {}


def find_one(vault: Path, needle: str) -> Path | None:
    return next((p for stem, p in entries(vault).items() if needle in stem), None)


def usage(vault: Path, needle: str) -> int | None:
    path = find_one(vault, needle)
    return int(front(path).get("usage_count", -1)) if path else None


# --- per-eval graders --------------------------------------------------------
# Each returns a list of (assertion, passed | None, evidence). None means the
# assertion needs a human — it is about the response, not the filesystem.


def grade_ambiguous(vault: Path, reference: Path, response: str) -> list:
    before, after = set(entries(reference)), set(entries(vault))
    return [
        ("No new file was created in entries/", after <= before, f"added: {sorted(after - before)}"),
        (
            "The response names the matching entry rather than staying vague",
            "nginx-strips-cors-header" in response,
            "found in response" if "nginx-strips-cors-header" in response else "not mentioned",
        ),
        ("The response reads as a search result, not a save confirmation", None, "needs review"),
    ]


def grade_recall_synonym(vault: Path, reference: Path, response: str) -> list:
    target, distractors = "nginx-strips-cors-header", ("browser-preflight-caching", "api-gateway-timeout")
    path = find_one(vault, target)
    moved = [d for d in distractors if usage(vault, d) != usage(reference, d)]
    return [
        (
            "The seeded CORS entry appears in the response",
            target in response, f"'{target}' in response: {target in response}",
        ),
        (
            "usage_count on it incremented by exactly 1",
            usage(vault, target) == (usage(reference, target) or 0) + 1,
            f"{usage(reference, target)} -> {usage(vault, target)}",
        ),
        (
            "last_accessed on it is today",
            bool(path) and front(path).get("last_accessed") == TODAY,
            front(path).get("last_accessed", "no entry") if path else "no entry",
        ),
        (
            "keyword-matching distractors were NOT reconsolidated",
            not moved, f"wrongly boosted: {moved}" if moved else "both left alone",
        ),
        ("The query was expanded into technical synonyms before searching", None, "needs review"),
    ]


def grade_amend(vault: Path, reference: Path, response: str) -> list:
    target = "nginx-strips-cors-header"
    path, ref_path = find_one(vault, target), find_one(reference, target)
    body = path.read_text(encoding="utf-8") if path else ""
    identity = (
        bool(path) and bool(ref_path)
        and all(front(path).get(k) == front(ref_path).get(k) for k in ("type", "date", "project"))
    )
    return [
        (
            "The number of entries did not increase",
            len(entries(vault)) <= len(entries(reference)),
            f"{len(entries(reference))} -> {len(entries(vault))}",
        ),
        ("The entry's body now mentions 504", "504" in body, "504 present" if "504" in body else "absent"),
        (
            "type, date and project are unchanged", identity,
            f"type={front(path).get('type')} date={front(path).get('date')}" if path else "no entry",
        ),
        (
            "usage_count incremented and last_accessed is today",
            usage(vault, target) == (usage(reference, target) or 0) + 1
            and bool(path) and front(path).get("last_accessed") == TODAY,
            f"usage {usage(reference, target)} -> {usage(vault, target)}, "
            f"last_accessed={front(path).get('last_accessed') if path else '-'}",
        ),
        (
            "Indexes agree with the entry's summary",
            indexes_consistent(vault, target),
            "no index still shows a stale summary" if indexes_consistent(vault, target) else "stale index line",
        ),
    ]


def indexes_consistent(vault: Path, needle: str) -> bool:
    path = find_one(vault, needle)
    if not path:
        return False
    summary = front(path).get("summary", "").strip("\"'")
    if not summary:
        return True
    candidates = [vault / "index.md", *(vault / "maps").glob("*.md"), *(vault / "daily").glob("*.md")]
    for candidate in candidates:
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            if f"[[{path.stem}]]" in line and summary not in line:
                return False
    return True


def grade_validity_gate(vault: Path, reference: Path, response: str) -> list:
    before, after = set(entries(reference)), set(entries(vault))
    return [
        (
            "No entry was created without the user insisting",
            after <= before, f"created: {sorted(after - before)}",
        ),
        ("The response explains specifically why the fact is trivial", None, "needs review"),
        ("The response makes clear the user can override", None, "needs review"),
    ]


def grade_bootstrap(vault: Path, reference: Path, response: str) -> list:
    required = ["entries", "maps", "daily", "archive", "index.md", ".obsidian"]
    missing = [name for name in required if not (vault / name).exists()]
    decisions = [p for p in entries(vault).values() if front(p).get("type") == "decision"]
    body = decisions[0].read_text(encoding="utf-8") if decisions else ""
    links = set(re.findall(r"\[\[([^\]|#]+)", body))
    graph = {t.lower() for t in links}
    return [
        ("The vault structure was created", not missing, f"missing: {missing}"),
        (
            "A decision entry exists with status: open",
            bool(decisions) and front(decisions[0]).get("status") == "open",
            front(decisions[0]).get("status", "-") if decisions else "no decision entry",
        ),
        (
            "The rationale is recorded under its own section",
            bool(re.search(r"^##+\s*(Rationale|Racional)", body, re.M | re.I)),
            "Rationale heading present" if "ationale" in body else "no Rationale heading",
        ),
        (
            "Postgres and Mongo are threaded as wiki-links",
            any("postgres" in t for t in graph) and any("mongo" in t for t in graph),
            f"links: {sorted(links)}",
        ),
    ]


GRADERS = {
    "ambiguous-input-routes-to-recall": ("cors", grade_ambiguous),
    "recall-by-synonym": ("cors", grade_recall_synonym),
    "duplicate-becomes-amend": ("cors", grade_amend),
    "validity-gate-pushes-back": ("empty", grade_validity_gate),
    "fresh-vault-bootstraps": ("bare", grade_bootstrap),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("iteration", type=Path)
    args = parser.parse_args()

    summary = []
    for name, (scenario, grader) in GRADERS.items():
        # A reference vault built now has the same relative ages as the seed the
        # run started from, so diffing against it isolates what the agent changed.
        reference = build(scenario)
        for arm in ("with_skill", "without_skill"):
            run = args.iteration / name / arm
            if not run.exists():
                continue
            response_file = run / "outputs" / "response.md"
            response = response_file.read_text(encoding="utf-8") if response_file.exists() else ""
            results = grader(run / "vault", reference, response)
            graded = [
                {"text": text, "passed": bool(passed), "evidence": evidence,
                 "needs_review": passed is None}
                for text, passed, evidence in results
            ]
            (run / "grading.json").write_text(
                json.dumps({"eval_name": name, "arm": arm, "expectations": graded}, indent=2),
                encoding="utf-8",
            )
            objective = [g for g in graded if not g["needs_review"]]
            passed = sum(1 for g in objective if g["passed"])
            summary.append((name, arm, passed, len(objective), len(graded) - len(objective)))

    width = max(len(n) for n, *_ in summary)
    print(f"{'eval'.ljust(width)}  arm             objective  needs review")
    for name, arm, passed, total, review in summary:
        print(f"{name.ljust(width)}  {arm.ljust(14)}  {passed}/{total}        {review}")


if __name__ == "__main__":
    main()
