#!/usr/bin/env python3
"""Generates several individual dossiers and opens the index only at the end."""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from generate_dossier_html import build_dossier_file, open_index_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generates one HTML file per item of a JSON list."
    )
    parser.add_argument("json_path", help="JSON file holding a list of payloads")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument(
        "--no-open-index",
        action="store_true",
        help="Does not open the index (tests / headless environments only)",
    )
    parser.add_argument(
        "--no-check-links",
        action="store_true",
        help="Does not check whether the cited source URLs resolve",
    )
    args = parser.parse_args()

    with open(args.json_path, "r", encoding="utf-8") as handle:
        dossiers = json.load(handle)

    if not isinstance(dossiers, list) or not dossiers:
        raise ValueError("The file must hold a non-empty JSON list.")

    generated = []
    for position, dossier in enumerate(dossiers, start=1):
        if not isinstance(dossier, dict):
            raise ValueError(f"Item {position} is not a JSON object.")
        name = dossier.get("nome_eleitoral") or dossier.get("nome")
        if not name:
            raise ValueError(f"Item {position} has no electoral name (nome_eleitoral).")
        path = build_dossier_file(dossier, args.output_dir, check_links=not args.no_check_links)
        generated.append(path)
        print(f"[{position}/{len(dossiers)}] {name}: {path}")

    index_path = os.path.join(os.path.dirname(generated[-1]), "index.html")
    print(f"Index updated: {index_path}")
    if not args.no_open_index:
        if open_index_file(index_path):
            print("Index opened in the default browser.")
        else:
            print("[!] The browser did not confirm it opened automatically.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
