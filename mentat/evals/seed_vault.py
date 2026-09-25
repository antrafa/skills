#!/usr/bin/env python3
"""Build a throwaway Mentat vault for the evals, with entry ages relative to today.

Seeds cannot be checked in as fixed files. Half of what the evals assert is about
decay, and decay is measured in days since last access — a seed frozen at
2026-01-10 tests something different every day it sits in the repo, and the
"a note idle for 14 days lands near 75" assertion would silently start failing.
Generating them means the ages are whatever the eval says they are.

Indexing goes through vault.py's own helpers rather than being reimplemented
here: a seed vault whose MOCs were built differently from real ones would test
the seeder instead of the skill.

    ./seed_vault.py --scenario cors            # prints the vault path
    ./seed_vault.py --scenario mixed-age --into /tmp/v
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TODAY = dt.date.today()


def load_vault(vault_path: Path):
    """Import vault.py bound to `vault_path`.

    vault.py resolves MENTAT_VAULT at import time, so the environment has to be
    set first — which is also exactly how a test run should invoke the CLI.
    """
    os.environ["MENTAT_VAULT"] = str(vault_path)
    spec = importlib.util.spec_from_file_location("vault", SKILL_DIR / "scripts" / "vault.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed(
    mod,
    *,
    kind: str,
    slug: str,
    summary: str,
    body: str,
    age_days: int,
    idle_days: int | None = None,
    salience: int | None = None,
    usage_count: int = 0,
    tags: str = "",
    project: str = "",
    related: tuple[str, ...] = (),
    title: str | None = None,
    index: bool = True,
) -> str:
    created = TODAY - dt.timedelta(days=age_days)
    idle = age_days if idle_days is None else idle_days
    accessed = TODAY - dt.timedelta(days=idle)
    stem = f"{created.isoformat()}-{slug}"
    front = {
        "type": kind,
        "date": created.isoformat(),
        "tags": "[" + ", ".join(mod.normalize_tags(tags, kind)) + "]",
        "project": project,
        "summary": mod.yaml_str(summary),
        "salience": str(salience if salience is not None else (200 if kind == "schema" else 100)),
        "usage_count": str(usage_count),
        "last_accessed": accessed.isoformat(),
        "decayed_at": accessed.isoformat(),
        "status": "resolved" if kind in mod.RESOLVED_BY_DEFAULT else "open",
        "related": mod.render_related(list(related)),
    }
    mod.entries_dir().mkdir(parents=True, exist_ok=True)
    path = mod.entries_dir() / f"{stem}.md"
    mod.dump_entry(path, front, f"\n# {title or summary}\n\n{body.strip()}\n")

    if index:
        mod.insert_under(mod.moc_path(kind), "## Recent", f"- [[{stem}]] — {summary}")
        daily = mod.daily_path(created)
        if not daily.exists():
            daily.parent.mkdir(parents=True, exist_ok=True)
            daily.write_text(f"# {created.isoformat()}\n\n## Entries\n", encoding="utf-8")
        mod.insert_under(daily, "## Entries", f"- [[{stem}]] — {summary} ({kind})")
        mod.insert_under(mod.VAULT / "index.md", "## Recent Entries", f"- [[{stem}]] — {summary}")
    return stem


# --- scenarios ---------------------------------------------------------------


def scenario_cors(mod) -> None:
    """A vault that already knows about the CORS bug.

    Two of the entries are deliberate distractors: `browser-preflight-caching`
    matches "preflight" without answering how the bug was fixed, and
    `api-gateway-timeout` is a plausible neighbour. Recall is supposed to
    reconsolidate only what earned it, and with a single relevant entry there is
    nothing to get that wrong with.
    """
    seed(
        mod,
        kind="bug",
        slug="api-gateway-timeout",
        title="API gateway times out before upstream finishes",
        summary="Gateway 60s timeout cut long checkout writes",
        age_days=75,
        salience=110,
        usage_count=1,
        project="checkout-api",
        tags="infra/nginx, domain/orders",
        body="""
## Symptoms

- POST /api/orders returned 504 on large carts

## Root Cause

- Gateway `proxy_read_timeout` was 60s while the upstream write took up to 90s

## Fix

- Raised `proxy_read_timeout` to 120s for the orders location block
""",
    )
    seed(
        mod,
        kind="bug",
        slug="nginx-strips-cors-header",
        title="Nginx strips CORS header on 502",
        summary="Nginx dropped CORS headers on 502",
        age_days=60,
        salience=130,
        usage_count=3,
        project="checkout-api",
        tags="infra/nginx, domain/auth",
        related=("api-gateway-timeout",),
        body="""
## Symptoms

- The browser preflight for POST /api/orders failed only when the upstream
  answered 502 — the same request succeeded on 200
- No `Access-Control-Allow-Origin` on the error response

## Root Cause

- `add_header` in Nginx applies only to successful responses unless it is
  declared with `always`, so error responses went out bare

## Fix

- `add_header Access-Control-Allow-Origin $cors_origin always;`

## Changed Files

- `deploy/nginx/checkout.conf`

## Lessons Learned

- Error responses need the same headers as success responses, or the browser
  reports a CORS failure and hides the real status
""",
    )
    seed(
        mod,
        kind="learning",
        slug="browser-preflight-caching",
        title="Browsers cache preflight responses per Access-Control-Max-Age",
        summary="Preflight caching hides config changes for up to 2h",
        age_days=30,
        tags="domain/auth",
        body="""
## Insight

- Chrome caches a successful OPTIONS response for as long as
  `Access-Control-Max-Age` allows, capped at 2h

## Application

- Test CORS changes in a fresh profile, or the old preflight answers for you
""",
    )
    seed(
        mod,
        kind="note",
        slug="deploy-checklist",
        summary="Steps before a checkout-api deploy",
        age_days=5,
        project="checkout-api",
        body="## Details\n\n- Drain the queue before rolling pods",
    )


def scenario_mixed_age(mod) -> None:
    """Ages and types spread wide enough that groom has something to get wrong.

    Permanent types are seeded old and idle on purpose — they are the control
    group: if any of their salience moves, the permanence rule broke.
    """
    permanent = [
        ("bug", "flaky-retry-test", "Retry test failed under parallel runs", 90),
        ("decision", "postgres-over-mongo", "Stayed on Postgres for multi-table transactions", 200),
        ("feature", "order-export-csv", "CSV export for closed orders", 60),
        ("learning", "jitter-prevents-herd", "Backoff without jitter causes thundering herd", 45),
        ("snippet", "retry-with-backoff", "Retry helper with full jitter", 120),
        ("schema", "error-handling-pattern", "Errors belong to the domain, not the flow", 30),
    ]
    for kind, slug, summary, age in permanent:
        seed(
            mod, kind=kind, slug=slug, summary=summary, age_days=age,
            tags="pattern/retry" if "retry" in slug else "",
            body=f"## Details\n\n- {summary}",
        )

    # Fadeable, one per band: fresh, the 14-day reference point, mid-fade, and two
    # already spent enough that groom must archive them.
    fadeable = [
        ("note", "standup-notes-today", "What the team is on this week", 0, 100),
        ("note", "profiling-session", "Where the checkout latency actually goes", 14, 100),
        ("idea", "vault-web-ui", "A browser view over the vault", 40, 100),
        ("journal", "rough-oncall-week", "Notes from a bad on-call rotation", 250, 20),
        ("episodic", "migrated-staging-db", "Ran the staging migration by hand", 300, 12),
    ]
    for kind, slug, summary, idle, salience in fadeable:
        seed(
            mod, kind=kind, slug=slug, summary=summary,
            age_days=max(idle, 1), idle_days=idle, salience=salience,
            body=f"## Details\n\n- {summary}",
        )

    # Integrity damage for Status and Audit to find: an entry in no MOC, and a
    # MOC line pointing at an entry that never existed.
    seed(
        mod, kind="note", slug="never-indexed", summary="Written straight to disk",
        age_days=3, index=False, body="## Details\n\n- No MOC knows about this one",
    )
    mod.insert_under(
        mod.moc_path("bug"), "## Recent", "- [[2026-01-01-entry-that-was-deleted]] — gone"
    )
    seed(
        mod, kind="note", slug="points-at-nothing", summary="Links to a deleted entry",
        age_days=4, related=("2026-01-02-also-deleted",),
        body="## Details\n\n- See [[2026-01-03-vanished]] for the rest",
    )


SCENARIOS = {
    "cors": scenario_cors,
    "mixed-age": scenario_mixed_age,
    "empty": lambda mod: None,
    # `bare` leaves the path non-existent on purpose: the bootstrap eval is about
    # whether the agent notices a missing vault and runs init-vault.sh itself.
    "bare": lambda mod: None,
}


def build(scenario: str, into: Path | None = None) -> Path:
    vault = into or Path(tempfile.mkdtemp(prefix="mentat-eval-")) / "vault"
    mod = load_vault(vault)
    if scenario != "bare":
        subprocess.run(
            ["bash", str(SKILL_DIR / "scripts" / "init-vault.sh")],
            env={**os.environ, "MENTAT_VAULT": str(vault)},
            check=True, capture_output=True,
        )
    SCENARIOS[scenario](mod)
    return vault


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", required=True, choices=list(SCENARIOS))
    parser.add_argument("--into", type=Path, help="target directory (default: a temp dir)")
    args = parser.parse_args()
    print(build(args.scenario, args.into))


if __name__ == "__main__":
    main()
