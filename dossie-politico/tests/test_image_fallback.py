#!/usr/bin/env python3
"""Regressões do HTML gerado para imagens ausentes ou quebradas."""

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from generate_dossier_html import generate_dossier_html, generate_index_html  # noqa: E402


class ImageFallbackTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dossier = {
            "nome_eleitoral": "Pessoa sem foto",
            "nome_civil": "Pessoa sem foto",
            "cargo": "Candidatura de teste",
            "partido": "TESTE",
            "uf": "BR",
            "data_corte": "2026-08-22",
            "resumo_cidadao_ia": {
                "sintese": "Fixture mínima para testar a imagem de perfil.",
                "pontos_chave": ["Um", "Dois", "Três"],
                "lacunas": [],
                "aviso": "Fixture de teste.",
            },
            "cobertura_pesquisa": {
                "data_execucao": "2026-08-22",
                "periodo": "fixture",
                "nomes_consultados": ["Pessoa sem foto"],
                "eixos_verificados": ["fixture"],
                "fontes_consultadas": ["fixture"],
                "limitacoes": [],
            },
        }

    def assert_local_fallback(self, document: str) -> None:
        self.assertNotIn("via.placeholder.com", document)
        self.assertIn("data:image/svg+xml", document)
        self.assertIn("this.onerror=null", document)

    def test_dossier_without_photo_uses_non_recursive_local_fallback(self) -> None:
        self.assert_local_fallback(generate_dossier_html(self.dossier))

    def test_index_without_photo_uses_non_recursive_local_fallback(self) -> None:
        entries = [{
            "nome_eleitoral": "Pessoa sem foto",
            "nome_civil": "Pessoa sem foto",
            "cargo": "Candidatura de teste",
            "partido": "TESTE",
            "uf": "BR",
            "filename": "Pessoa_sem_foto.html",
        }]
        self.assert_local_fallback(generate_index_html(entries))


if __name__ == "__main__":
    unittest.main()
