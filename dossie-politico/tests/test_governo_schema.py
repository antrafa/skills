#!/usr/bin/env python3
"""
test_governo_schema.py - Validação do esquema de dados, geração HTML e persistência JSON
para dossiês de governos presidenciais.
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).parents[1]
SCRIPT_DIR = REPO_ROOT / "scripts"
EXAMPLES_DIR = REPO_ROOT / "examples"
sys.path.insert(0, str(SCRIPT_DIR))

from generate_dossier_html import (  # noqa: E402
    generate_dossier_html,
    build_dossier_file,
    update_index_catalog,
)
from run_dossier import run_investigation  # noqa: E402


class TestGovernoSchema(unittest.TestCase):
    def setUp(self):
        self.exemplo_path = EXAMPLES_DIR / "exemplo_governo_presidencial.json"

    def test_exemplo_governo_presidencial_exists_and_is_valid(self):
        self.assertTrue(
            self.exemplo_path.is_file(),
            f"Arquivo {self.exemplo_path} não encontrado.",
        )
        with open(self.exemplo_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validação do tipo de dossiê
        self.assertEqual(data.get("tipo_dossie"), "governo_presidencial")

        # Campos gerais obrigatórios
        for campo in [
            "nome_eleitoral",
            "cargo",
            "partido",
            "uf",
            "data_corte",
            "resumo_cidadao_ia",
            "cobertura_pesquisa",
        ]:
            self.assertIn(campo, data, f"Campo obrigatório '{campo}' ausente.")

        # Validação do bloco mandato_executivo
        mandato = data.get("mandato_executivo")
        self.assertIsInstance(mandato, dict, "mandato_executivo deve ser dict")
        for k in ["id", "presidente", "partido", "periodo", "ano_inicio", "ano_fim", "ministros_notaveis"]:
            self.assertIn(k, mandato, f"Campo '{k}' ausente em mandato_executivo")
        self.assertIsInstance(mandato["ministros_notaveis"], list)
        self.assertGreater(len(mandato["ministros_notaveis"]), 0)

        # Validação do bloco indicadores_economicos
        indicadores = data.get("indicadores_economicos")
        self.assertIsInstance(indicadores, dict, "indicadores_economicos deve ser dict")
        self.assertIn("resumo_macro", indicadores)
        self.assertIn("grafico_anual", indicadores)
        resumo = indicadores["resumo_macro"]
        for k in ["ipca_acumulado", "selic_inicial", "selic_final", "dolar_inicial", "dolar_final", "divida_bruta_inicial", "divida_bruta_final"]:
            self.assertIn(k, resumo, f"Chave '{k}' ausente em resumo_macro")
        self.assertIsInstance(indicadores["grafico_anual"], list)
        self.assertGreater(len(indicadores["grafico_anual"]), 0)

        # Validação de cofres_publicos
        cofres = data.get("cofres_publicos")
        self.assertIsInstance(cofres, dict, "cofres_publicos deve ser dict")
        self.assertIn("fontes", cofres)

        # Validação de promessas_campanha
        promessas = data.get("promessas_campanha")
        self.assertIsInstance(promessas, dict, "promessas_campanha deve ser dict")
        for k in ["total", "cumpridas", "nao_cumpridas", "itens"]:
            self.assertIn(k, promessas, f"Chave '{k}' ausente em promessas_campanha")
        self.assertIsInstance(promessas["itens"], list)
        self.assertGreater(len(promessas["itens"]), 0)

        # Validação de projetos_de_lei_e_reformas
        reformas = data.get("projetos_de_lei_e_reformas")
        self.assertIsInstance(reformas, list, "projetos_de_lei_e_reformas deve ser list")
        self.assertGreater(len(reformas), 0)
        for ref in reformas:
            self.assertIn("titulo", ref)
            self.assertIn("norma", ref)
            self.assertIn("ano", ref)
            self.assertIn("impacto", ref)

        # Validação de controversias_e_noticias com contraditório e evidência
        controversias = data.get("controversias_e_noticias")
        self.assertIsInstance(controversias, list)
        self.assertGreater(len(controversias), 0)
        for c in controversias:
            for k in ["titulo", "status", "grau_veracidade", "o_que_esta_comprovado", "o_que_nao_esta_comprovado", "posicao_defesa", "fontes"]:
                self.assertIn(k, c, f"Campo '{k}' ausente na controvérsia '{c.get('titulo')}'")

        # Validação da auditoria de cobertura
        cov = data.get("cobertura_pesquisa")
        self.assertIsInstance(cov, dict)
        for k in ["data_execucao", "periodo", "nomes_consultados", "eixos_verificados", "fontes_consultadas", "limitacoes"]:
            self.assertIn(k, cov)

    def test_html_rendering_presidential_sections(self):
        if not self.exemplo_path.is_file():
            self.skipTest("exemplo_governo_presidencial.json ainda não criado")
        with open(self.exemplo_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        html_content = generate_dossier_html(data)

        # Garante presença dos blocos específicos de mandato presidencial
        self.assertIn("Indicadores Macroeconômicos", html_content)
        self.assertIn("Promessas de Campanha", html_content)
        self.assertIn("Reformas", html_content)
        self.assertIn("IPCA", html_content)
        self.assertIn("Selic", html_content)
        self.assertIn("Dólar", html_content)
        self.assertIn("Dívida Bruta", html_content)
        # Garante menção a ministros notáveis
        self.assertIn("Equipe Ministerial", html_content)

    def test_build_dossier_file_saves_both_html_and_json(self):
        if not self.exemplo_path.is_file():
            self.skipTest("exemplo_governo_presidencial.json ainda não criado")
        with open(self.exemplo_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        with tempfile.TemporaryDirectory() as tmpdir:
            generated_html = build_dossier_file(data, output_dir=tmpdir, check_links=False)
            self.assertTrue(os.path.isfile(generated_html))
            self.assertTrue(generated_html.endswith(".html"))

            # Verifica se o arquivo .json correspondente foi gravado lado a lado
            expected_json = str(Path(generated_html).with_suffix(".json"))
            self.assertTrue(
                os.path.isfile(expected_json),
                f"Arquivo JSON correspondente {expected_json} não foi salvo.",
            )

            with open(expected_json, "r", encoding="utf-8") as f:
                saved_json = json.load(f)
            self.assertEqual(saved_json.get("tipo_dossie"), "governo_presidencial")
            self.assertEqual(saved_json.get("nome_eleitoral"), data.get("nome_eleitoral"))

            # Verifica se index.json foi atualizado com campos de governo
            index_json_path = os.path.join(tmpdir, "index.json")
            self.assertTrue(os.path.isfile(index_json_path))
            with open(index_json_path, "r", encoding="utf-8") as f:
                index_entries = json.load(f)
            self.assertEqual(len(index_entries), 1)
            entry = index_entries[0]
            self.assertEqual(entry.get("tipo_dossie"), "governo_presidencial")
            self.assertIn("periodo_mandato", entry)
            self.assertIn("resumo_indicadores", entry)
            self.assertIsNotNone(entry.get("resumo_indicadores"))

    def test_run_dossier_with_governo_flag(self):
        fake_gov = {
            "tipo_dossie": "governo_presidencial",
            "mandato_executivo": {
                "id": "bolsonaro",
                "presidente": "Jair Bolsonaro",
                "partido": "PL",
                "vice": "Hamilton Mourão",
                "periodo": "2019–2022",
                "ano_inicio": 2019,
                "ano_fim": 2022,
                "ministros_notaveis": [{"pasta": "Economia", "nome": "Paulo Guedes"}],
            },
            "indicadores_economicos": {
                "resumo_macro": {"ipca_acumulado": 26.89},
                "series": {},
                "grafico_anual": [],
            },
            "cofres_publicos": {"fontes": ["BCB SGS"]},
        }

        with patch("run_dossier.fetch_dados_governo", return_value=fake_gov):
            res = run_investigation(
                nome_politico="bolsonaro",
                governo="bolsonaro",
                render_html=False,
            )
            dossier = res["dossier_data"]
            self.assertEqual(dossier.get("tipo_dossie"), "governo_presidencial")
            self.assertEqual(dossier.get("mandato_executivo", {}).get("presidente"), "Jair Bolsonaro")
            self.assertIn("indicadores_economicos", dossier)

    def test_remove_dossier_entry_deletes_both_html_and_json(self):
        with open(self.exemplo_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        with tempfile.TemporaryDirectory() as tmpdir:
            generated_html = build_dossier_file(data, output_dir=tmpdir, check_links=False)
            filename = os.path.basename(generated_html)
            expected_json = str(Path(generated_html).with_suffix(".json"))

            self.assertTrue(os.path.isfile(generated_html))
            self.assertTrue(os.path.isfile(expected_json))

            from generate_dossier_html import remove_dossier_entry
            removed = remove_dossier_entry(tmpdir, filename, delete_html=True)
            self.assertTrue(removed)
            self.assertFalse(os.path.isfile(generated_html))
            self.assertFalse(os.path.isfile(expected_json))

    def test_parliamentary_dossier_also_persists_json(self):
        deputado_path = EXAMPLES_DIR / "exemplo_deputado.json"
        self.assertTrue(deputado_path.is_file())
        with open(deputado_path, "r", encoding="utf-8") as f:
            dep_data = json.load(f)

        with tempfile.TemporaryDirectory() as tmpdir:
            generated_html = build_dossier_file(dep_data, output_dir=tmpdir, check_links=False)
            expected_json = str(Path(generated_html).with_suffix(".json"))

            self.assertTrue(os.path.isfile(generated_html))
            self.assertTrue(os.path.isfile(expected_json))

            # Verifica catalog
            with open(os.path.join(tmpdir, "index.json"), "r", encoding="utf-8") as f:
                entries = json.load(f)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].get("tipo_dossie"), "perfil_politico")


if __name__ == "__main__":
    unittest.main()
