#!/usr/bin/env python3
"""
fetch_tse_transparency.py - Queries and supports extraction of electoral and asset data from the TSE (Superior Electoral Court) DivulgaCandContas system
Official source: https://divulgacandcontas.tse.jus.br/
"""

import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PoliticoDossie/1.0',
    'Accept': 'application/json'
}

def get_tse_endpoints(ano: int, uf: str) -> Dict[str, str]:
    """Official DivulgaCandContas and Dados Abertos (open data) sources for manual lookup."""
    base = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1"
    return {
        'eleicao_consulta': f"{base}/eleicao/eleicoes",
        'portal_busca': "https://divulgacandcontas.tse.jus.br/divulga/#/",
        'catalogo_dados_abertos': f"https://dadosabertos.tse.jus.br/dataset/candidatos-{ano}",
        'candidatos_csv_zip': f"https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{ano}.zip",
        'candidatos_complementar_csv_zip': (
            "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand_complementar/"
            f"consulta_cand_complementar_{ano}.zip"
        ),
        'bens_csv_zip': f"https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/bem_candidato_{ano}.zip",
        'filtro_uf': uf.upper(),
    }


def build_transparency_links(nome: str, cargo: str = "", uf: str = "") -> Dict[str, Any]:
    """Open searches on official portals.

    Only links whose search parameter is documented and works belong here. Single-page-app
    portals (TSE, TCU, STJ) do not take the term through the URL: for them the search
    screen goes in, and the dossier shows the name to type. A link that does not open
    destroys exactly the auditability this block exists to offer.
    """
    nome_encoded = urllib.parse.quote(nome)

    return {
        # Verified: they answer 200 with the term applied server-side.
        'portal_transparencia_federal': f"https://portaldatransparencia.gov.br/busca?termo={nome_encoded}",
        'portal_transparencia_servidores': f"https://portaldatransparencia.gov.br/servidores/busca?termo={nome_encoded}",
        'cgu_ceis_sancoes': f"https://portaldatransparencia.gov.br/sancoes/ceis?termo={nome_encoded}",
        'cnj_noticias_e_atos': f"https://www.cnj.jus.br/?s={nome_encoded}",
        'stf_jurisprudencia': (
            "https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&sinonimo=true"
            f"&plural=true&queryString={nome_encoded}"
        ),
        'stj_jurisprudencia': f"https://scon.stj.jus.br/SCON/pesquisar.jsp?b=ACOR&livre={nome_encoded}",
        # Search screens: the name is typed manually.
        'tse_divulgacand': "https://divulgacandcontas.tse.jus.br/divulga/#/",
        'tcu_jurisprudencia_e_inabilitados': "https://pesquisa.apps.tcu.gov.br/#/pesquisa/acordao-completo",
        'diario_oficial_uniao': "https://www.in.gov.br/consulta/",
    }


if __name__ == '__main__':
    nome = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Arthur Lira"
    links = build_transparency_links(nome)
    print(json.dumps({'politico': nome, 'links_transparencia': links}, indent=2, ensure_ascii=False))
