#!/usr/bin/env python3
"""
test_fetch_governo.py - Testes unitários para o coletor macroeconômico do BCB SGS.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adiciona scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fetch_governo import (
    get_preset_governo,
    calcular_variacao_acumulada,
    consultar_serie_bcb,
    fetch_dados_governo,
    PRESETS_GOVERNO,
)


class TestFetchGoverno(unittest.TestCase):
    def test_presets_exist(self):
        preset = get_preset_governo("bolsonaro")
        self.assertIsNotNone(preset)
        self.assertEqual(preset["presidente"], "Jair Bolsonaro")
        self.assertEqual(preset["ano_inicio"], 2019)
        self.assertEqual(preset["ano_fim"], 2022)

        # Checa todos os 5 presets requeridos
        for key in ("fhc", "lula", "dilma", "temer", "bolsonaro"):
            p = get_preset_governo(key)
            self.assertIsNotNone(p, f"Preset '{key}' deve existir")
            self.assertIn("presidente", p)
            self.assertIn("ano_inicio", p)
            self.assertIn("ano_fim", p)
            self.assertIn("data_inicio", p)
            self.assertIn("data_fim", p)

        # Case-insensitive e whitespace
        self.assertEqual(get_preset_governo(" Bolsonaro ")["ano_inicio"], 2019)
        self.assertEqual(get_preset_governo("LULA")["ano_inicio"], 2003)

        # Preset inexistente ou strings curtas que não devem dar falso positivo
        self.assertIsNone(get_preset_governo("inexistente_xyz"))
        self.assertIsNone(get_preset_governo("a"))
        self.assertIsNone(get_preset_governo("fh"))
        self.assertIsNone(get_preset_governo("te"))
        self.assertIsNone(get_preset_governo("lu"))
        self.assertIsNotNone(get_preset_governo("fhc"))

    def test_calculo_variacao(self):
        # Teste do cálculo composto
        taxas = [4.31, 4.52, 10.06, 5.79]  # IPCA aproximado 2019-2022
        acumulado = calcular_variacao_acumulada(taxas)
        # O valor composto exato é (1.0431*1.0452*1.1006*1.0579 - 1)*100 = 26.94%
        self.assertAlmostEqual(acumulado, 26.94, places=1)
        self.assertAlmostEqual(acumulado, 26.89, delta=0.1)

        # Lista vazia retorna 0.0
        self.assertEqual(calcular_variacao_acumulada([]), 0.0)

        # Valor único
        self.assertEqual(calcular_variacao_acumulada([5.5]), 5.5)

        # Variação negativa (deflação)
        # 1.10 * 0.90 = 0.99 -> -1.0%
        self.assertAlmostEqual(calcular_variacao_acumulada([10.0, -10.0]), -1.0, places=2)

    @patch("fetch_governo.http_get_json")
    def test_consultar_serie_bcb_mock(self, mock_http):
        mock_http.return_value = [
            {"data": "01/01/2021", "valor": "0.25"},
            {"data": "01/02/2021", "valor": "0.86"},
        ]
        dados = consultar_serie_bcb(433, "01/01/2021", "01/02/2021")
        self.assertEqual(len(dados), 2)
        self.assertEqual(dados[0]["data"], "01/01/2021")
        self.assertEqual(dados[0]["valor"], 0.25)
        self.assertEqual(dados[1]["valor"], 0.86)

    @patch("fetch_governo.http_get_json")
    def test_consultar_serie_bcb_error_handling(self, mock_http):
        mock_http.return_value = None
        dados = consultar_serie_bcb(99999, "01/01/2021", "01/02/2021")
        self.assertEqual(dados, [])

    @patch("fetch_governo.http_get_json")
    def test_consultar_serie_bcb_brazilian_number_cleaning(self, mock_http):
        mock_http.return_value = [
            {"data": "01/01/2021", "valor": "1.234,56"},
            {"data": "01/02/2021", "valor": "5.678.901,23"},
            {"data": "01/03/2021", "valor": "42,5"},
            {"data": "01/04/2021", "valor": "10.75"},
        ]
        dados = consultar_serie_bcb(433, "01/01/2021", "01/04/2021")
        self.assertEqual(len(dados), 4)
        self.assertEqual(dados[0]["valor"], 1234.56)
        self.assertEqual(dados[1]["valor"], 5678901.23)
        self.assertEqual(dados[2]["valor"], 42.5)
        self.assertEqual(dados[3]["valor"], 10.75)

    @patch("fetch_governo.consultar_serie_bcb")
    def test_fetch_dados_governo_structure(self, mock_consultar):
        # Mock das séries do SGS
        def mock_serie(codigo, dt_ini, dt_fim):
            if codigo == 433:  # IPCA mensal
                return [
                    {"data": "01/01/2019", "valor": 0.32},
                    {"data": "01/06/2019", "valor": 0.01},
                    {"data": "01/12/2019", "valor": 1.15},
                    {"data": "01/12/2022", "valor": 0.62},
                ]
            elif codigo == 432:  # Selic meta
                return [
                    {"data": "01/01/2019", "valor": 6.50},
                    {"data": "31/12/2022", "valor": 13.75},
                ]
            elif codigo == 1:  # Dólar PTAX
                return [
                    {"data": "02/01/2019", "valor": 3.87},
                    {"data": "30/12/2022", "valor": 5.21},
                ]
            elif codigo == 13762:  # Dívida Bruta % PIB
                return [
                    {"data": "01/01/2019", "valor": 75.3},
                    {"data": "01/12/2022", "valor": 73.5},
                ]
            elif codigo == 7326:  # PIB real
                return [
                    {"data": "01/01/2019", "valor": 1.2},
                    {"data": "01/01/2020", "valor": -3.3},
                    {"data": "01/01/2021", "valor": 5.0},
                    {"data": "01/01/2022", "valor": 2.9},
                ]
            return []

        mock_consultar.side_effect = mock_serie

        res = fetch_dados_governo("bolsonaro")
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("tipo_dossie"), "governo_presidencial")

        # Seções obrigatórias
        self.assertIn("mandato_executivo", res)
        self.assertIn("indicadores_economicos", res)
        self.assertIn("cofres_publicos", res)

        # Campos de mandato_executivo
        mandato = res["mandato_executivo"]
        self.assertEqual(mandato["presidente"], "Jair Bolsonaro")
        self.assertEqual(mandato["ano_inicio"], 2019)
        self.assertEqual(mandato["ano_fim"], 2022)

        # Campos de indicadores_economicos
        ind = res["indicadores_economicos"]
        self.assertIn("resumo_macro", ind)
        self.assertIn("series", ind)
        self.assertIn("grafico_anual", ind)

        resumo = ind["resumo_macro"]
        self.assertIn("ipca_acumulado", resumo)
        self.assertIn("selic_inicial", resumo)
        self.assertIn("selic_final", resumo)
        self.assertIn("dolar_inicial", resumo)
        self.assertIn("dolar_final", resumo)
        self.assertIn("dolar_variacao_pct", resumo)

        # Cofres públicos
        cofres = res["cofres_publicos"]
        self.assertIn("fontes", cofres)

    @patch("fetch_governo.consultar_serie_bcb")
    def test_fetch_dados_governo_custom_dates(self, mock_consultar):
        mock_consultar.return_value = []
        res = fetch_dados_governo(
            "Governo Teste", data_inicio="01/01/2021", data_fim="31/12/2022"
        )
        mandato = res["mandato_executivo"]
        self.assertEqual(mandato["presidente"], "Governo Teste")
        self.assertEqual(mandato["ano_inicio"], 2021)
        self.assertEqual(mandato["ano_fim"], 2022)
        self.assertEqual(len(res["indicadores_economicos"]["grafico_anual"]), 2)

    @patch("fetch_governo.consultar_serie_bcb")
    def test_fetch_dados_governo_selic_pre_1999(self, mock_consultar):
        def mock_serie(codigo, dt_ini, dt_fim):
            if codigo == 432:
                # Série 432 inicia apenas em 05/03/1999
                return [
                    {"data": "05/03/1999", "valor": 45.00},
                    {"data": "31/12/2002", "valor": 25.00},
                ]
            elif codigo == 1178:
                # Série 1178 cobre desde 1995
                return [
                    {"data": "02/01/1995", "valor": 47.37},
                    {"data": "31/12/1998", "valor": 29.00},
                    {"data": "31/12/1999", "valor": 19.00},
                ]
            return []

        mock_consultar.side_effect = mock_serie
        res = fetch_dados_governo("fhc")

        # Verifica que o ponto inicial de Selic vem de 1995 (série 1178)
        resumo = res["indicadores_economicos"]["resumo_macro"]
        self.assertEqual(resumo["selic_inicial"], 47.37)
        self.assertEqual(resumo["selic_final"], 25.00)

        # Gráfico anual deve conter valor de Selic para 1995 e 1998
        grafico = {g["ano"]: g for g in res["indicadores_economicos"]["grafico_anual"]}
        self.assertEqual(grafico[1995]["selic_fim"], 47.37)
        self.assertEqual(grafico[1998]["selic_fim"], 29.00)
        self.assertEqual(grafico[2002]["selic_fim"], 25.00)

    @patch("fetch_governo.fetch_dados_governo")
    def test_cli_main(self, mock_fetch):
        mock_fetch.return_value = {"tipo_dossie": "governo_presidencial"}
        from io import StringIO
        from fetch_governo import main

        test_args = ["fetch_governo.py", "bolsonaro"]
        with patch("sys.argv", test_args), patch("sys.stdout", new_callable=StringIO) as mock_out:
            main()
            output = mock_out.getvalue()
            self.assertIn('"tipo_dossie": "governo_presidencial"', output)


if __name__ == "__main__":
    unittest.main()
