#!/usr/bin/env python3
"""Regressões dos pontos que fazem o dossiê apontar para a pessoa ou a fonte errada."""

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import fetch_camara  # noqa: E402
import fetch_senado  # noqa: E402
import generate_dossier_html as gen  # noqa: E402

HOMONIMOS = [
    {"id": 1, "nome": "Benedita da Silva", "siglaPartido": "PT", "siglaUf": "RJ"},
    {"id": 2, "nome": "Marina Silva", "siglaPartido": "REDE", "siglaUf": "SP"},
]


class DisambiguationTest(unittest.TestCase):
    def test_camara_recusa_escolher_entre_homonimos(self) -> None:
        original = fetch_camara.find_deputados
        fetch_camara.find_deputados = lambda nome: HOMONIMOS
        try:
            with self.assertRaises(LookupError) as ctx:
                fetch_camara.fetch_deputado_por_nome("Silva")
        finally:
            fetch_camara.find_deputados = original
        self.assertIn("--id 1", str(ctx.exception))
        self.assertIn("--id 2", str(ctx.exception))

    def test_senado_recusa_escolher_entre_homonimos(self) -> None:
        hits = [
            {"IdentificacaoParlamentar": {"CodigoParlamentar": "10", "NomeParlamentar": "A Silva"}},
            {"IdentificacaoParlamentar": {"CodigoParlamentar": "20", "NomeParlamentar": "B Silva"}},
        ]
        original = fetch_senado.find_senadores
        fetch_senado.find_senadores = lambda nome: hits
        try:
            with self.assertRaises(LookupError) as ctx:
                fetch_senado.fetch_senador_por_nome("Silva")
        finally:
            fetch_senado.find_senadores = original
        self.assertIn("--codigo 10", str(ctx.exception))


class SourceVerificationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {
            "controversias_e_noticias": [{
                "titulo": "Caso de teste",
                "fontes": [
                    {"veiculo": "Veículo Vivo", "url": "https://exemplo.test/vivo"},
                    {"veiculo": "Veículo Morto", "url": "https://exemplo.test/morto"},
                ],
            }],
        }
        self.original = gen.check_url
        gen.check_url = lambda url, timeout=10: "ok" if url.endswith("vivo") else "quebrado (404)"

    def tearDown(self) -> None:
        gen.check_url = self.original

    def test_marca_link_quebrado_e_conta_no_resumo(self) -> None:
        tally = gen.verify_sources(self.data)
        self.assertEqual(tally, {"ok": 1, "quebrado": 1})

    def test_link_quebrado_aparece_riscado_no_html(self) -> None:
        gen.verify_sources(self.data)
        self.data.update({
            "nome_eleitoral": "Alvo de teste",
            "cargo": "Cargo de teste",
            "partido": "TESTE",
            "uf": "BR",
            "data_corte": "2026-09-08",
            "resumo_cidadao_ia": {"sintese": "x", "pontos_chave": ["a"], "lacunas": [], "aviso": "y"},
        })
        document = gen.generate_dossier_html(self.data)
        self.assertIn("source-dead", document)
        self.assertIn("Veículo Morto", document)
        # A fonte que resolveu não pode ser marcada como quebrada.
        self.assertNotIn("source-dead' title='Link não resolveu na verificação: ok", document)


class ScopeGuardTest(unittest.TestCase):
    def test_gerador_recusa_dossie_sem_registro_de_cobertura(self) -> None:
        with self.assertRaises(ValueError):
            gen.validate_coverage_record({"nome_eleitoral": "Sem cobertura"})


if __name__ == "__main__":
    unittest.main()


class DespesasTest(unittest.TestCase):
    """A CEAP só faz sentido agregada; nota solta não fiscaliza nada."""

    PAGINA = {
        "dados": [
            {"ano": 2023, "tipoDespesa": "COMBUSTÍVEIS", "valorLiquido": 100.0,
             "nomeFornecedor": "Posto X", "cnpjCpfFornecedor": "1"},
            {"ano": 2023, "tipoDespesa": "COMBUSTÍVEIS", "valorLiquido": 50.0,
             "nomeFornecedor": "Posto X", "cnpjCpfFornecedor": "1"},
            {"ano": 2024, "tipoDespesa": "PASSAGEM AÉREA", "valorLiquido": 900.0,
             "nomeFornecedor": "Cia Y", "cnpjCpfFornecedor": "2"},
        ],
        "links": [{"rel": "self", "href": "x"}],
    }

    def test_agrega_por_ano_categoria_e_fornecedor(self) -> None:
        original = fetch_camara.http_get
        fetch_camara.http_get = lambda url, **kw: self.PAGINA
        try:
            resumo = fetch_camara.fetch_despesas(1)
        finally:
            fetch_camara.http_get = original
        self.assertEqual(resumo["total"], 1050.0)
        self.assertEqual(resumo["periodo"], "2023 a 2024")
        self.assertEqual(resumo["por_categoria"][0]["categoria"], "PASSAGEM AÉREA")
        self.assertEqual(resumo["principais_fornecedores"][0]["nome"], "Cia Y")
        self.assertEqual(
            [c for c in resumo["por_categoria"] if c["categoria"] == "COMBUSTÍVEIS"][0]["notas"], 2
        )

    def test_para_no_limite_de_paginas_e_avisa(self) -> None:
        pagina_infinita = dict(self.PAGINA, links=[{"rel": "next", "href": "proxima"}])
        original = fetch_camara.http_get
        fetch_camara.http_get = lambda url, **kw: pagina_infinita
        try:
            resumo = fetch_camara.fetch_despesas(1, max_paginas=3)
        finally:
            fetch_camara.http_get = original
        self.assertTrue(resumo["truncado"])
        self.assertEqual(resumo["registros_analisados"], 9)


class RenderingGuardsTest(unittest.TestCase):
    BASE = {
        "nome_eleitoral": "Alvo de teste",
        "cargo": "Cargo",
        "partido": "TESTE",
        "uf": "BR",
        "data_corte": "2026-09-08",
        "resumo_cidadao_ia": {"sintese": "x", "pontos_chave": ["a"], "lacunas": [], "aviso": "y"},
    }

    def test_fonte_sem_url_nao_vira_link_falso(self) -> None:
        data = dict(self.BASE, controversias_e_noticias=[{
            "titulo": "Caso", "fontes": [{"veiculo": "Jornal", "data": "12/05/2024"}]}])
        document = gen.generate_dossier_html(data)
        self.assertIn("URL não localizada", document)
        self.assertNotIn("href='#'", document)

    def test_avisa_quando_o_dossie_so_tem_controversias(self) -> None:
        data = dict(self.BASE, controversias_e_noticias=[{"titulo": f"Caso {i}"} for i in range(3)])
        self.assertIn('<p class="proportion-warning">', gen.generate_dossier_html(data))

    def test_sem_desproporcao_nao_ha_aviso(self) -> None:
        data = dict(
            self.BASE,
            controversias_e_noticias=[{"titulo": "Caso"}],
            proposicoes_principais=[{"tipo": "PL", "numero": 1, "ano": 2024}],
        )
        self.assertNotIn('<p class="proportion-warning">', gen.generate_dossier_html(data))
