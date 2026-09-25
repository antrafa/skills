#!/usr/bin/env python3
"""Gera vários dossiês individuais e abre o índice apenas ao final."""

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
        description="Gera um HTML individual para cada item de uma lista JSON."
    )
    parser.add_argument("json_path", help="Arquivo JSON contendo uma lista de payloads")
    parser.add_argument("--output-dir", default=None, help="Diretório de saída")
    parser.add_argument(
        "--no-open-index",
        action="store_true",
        help="Não abre o índice (somente testes/ambientes sem interface)",
    )
    parser.add_argument(
        "--no-check-links",
        action="store_true",
        help="Não verifica se as URLs das fontes citadas resolvem",
    )
    args = parser.parse_args()

    with open(args.json_path, "r", encoding="utf-8") as handle:
        dossiers = json.load(handle)

    if not isinstance(dossiers, list) or not dossiers:
        raise ValueError("O arquivo deve conter uma lista JSON não vazia.")

    generated = []
    for position, dossier in enumerate(dossiers, start=1):
        if not isinstance(dossier, dict):
            raise ValueError(f"Item {position} não é um objeto JSON.")
        name = dossier.get("nome_eleitoral") or dossier.get("nome")
        if not name:
            raise ValueError(f"Item {position} não possui nome eleitoral.")
        path = build_dossier_file(dossier, args.output_dir, check_links=not args.no_check_links)
        generated.append(path)
        print(f"[{position}/{len(dossiers)}] {name}: {path}")

    index_path = os.path.join(os.path.dirname(generated[-1]), "index.html")
    print(f"Índice atualizado: {index_path}")
    if not args.no_open_index:
        if open_index_file(index_path):
            print("Índice aberto no navegador padrão.")
        else:
            print("[!] O navegador não confirmou a abertura automática.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
