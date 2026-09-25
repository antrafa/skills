#!/usr/bin/env python3
"""Garante que o consolidado por IA não omita polêmicas catalogadas."""

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from generate_dossier_html import build_summary_cases  # noqa: E402


class SummaryRayXTest(unittest.TestCase):
    def test_every_catalogued_case_appears_in_consolidated_summary(self) -> None:
        cases = [
            {
                "titulo": "Caso documental",
                "status": "Arquivado",
                "grau_veracidade": "Confirmado por documento/decisão",
                "resumo": "O procedimento foi encerrado.",
                "o_que_esta_comprovado": "O arquivamento.",
                "o_que_nao_esta_comprovado": "A acusação original.",
                "posicao_defesa": "A defesa negou os fatos.",
            },
            {
                "titulo": "Caso em apuração",
                "status": "Em investigação",
                "grau_veracidade": "Alegação oficial em apuração",
                "resumo": "A autoridade abriu inquérito.",
                "o_que_esta_comprovado": "A existência do inquérito.",
                "o_que_nao_esta_comprovado": "Autoria ou culpa.",
                "posicao_defesa": "A defesa afirmou não haver irregularidade.",
            },
        ]

        result = build_summary_cases(cases)

        self.assertEqual(result.count('class="summary-case"'), 2)
        for item in cases:
            self.assertIn(item["titulo"], result)
            self.assertIn(item["status"], result)
            self.assertIn(item["grau_veracidade"], result)
            self.assertIn(item["o_que_esta_comprovado"], result)
            self.assertIn(item["o_que_nao_esta_comprovado"], result)
            self.assertIn(item["posicao_defesa"], result)

    def test_empty_case_list_states_the_research_scope(self) -> None:
        result = build_summary_cases([])
        self.assertIn("Nenhum caso foi catalogado", result)
        self.assertIn("não prova inexistência", result)


if __name__ == "__main__":
    unittest.main()
