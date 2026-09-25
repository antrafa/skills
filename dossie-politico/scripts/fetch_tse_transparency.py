#!/usr/bin/env python3
"""
fetch_tse_transparency.py - Consulta e suporte à extração de dados eleitorais e patrimônio do TSE (DivulgaCandContas)
Fonte oficial: https://divulgacandcontas.tse.jus.br/
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
    """Fontes oficiais do DivulgaCandContas e dos Dados Abertos para consulta manual."""
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
    """Buscas abertas em portais oficiais.

    Só entra aqui link cujo parâmetro de busca é documentado e funciona. Portais em
    single-page app (TSE, TCU, STJ) não aceitam termo pela URL: para eles vai a tela de
    busca, e o dossiê exibe o nome a ser digitado. Link que não abre destrói justamente
    a auditabilidade que este bloco existe para oferecer.
    """
    nome_encoded = urllib.parse.quote(nome)

    return {
        # Verificados: respondem 200 com o termo aplicado no servidor.
        'portal_transparencia_federal': f"https://portaldatransparencia.gov.br/busca?termo={nome_encoded}",
        'portal_transparencia_servidores': f"https://portaldatransparencia.gov.br/servidores/busca?termo={nome_encoded}",
        'cgu_ceis_sancoes': f"https://portaldatransparencia.gov.br/sancoes/ceis?termo={nome_encoded}",
        'cnj_noticias_e_atos': f"https://www.cnj.jus.br/?s={nome_encoded}",
        'stf_jurisprudencia': (
            "https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&sinonimo=true"
            f"&plural=true&queryString={nome_encoded}"
        ),
        'stj_jurisprudencia': f"https://scon.stj.jus.br/SCON/pesquisar.jsp?b=ACOR&livre={nome_encoded}",
        # Telas de busca: digitar o nome manualmente.
        'tse_divulgacand': "https://divulgacandcontas.tse.jus.br/divulga/#/",
        'tcu_jurisprudencia_e_inabilitados': "https://pesquisa.apps.tcu.gov.br/#/pesquisa/acordao-completo",
        'diario_oficial_uniao': "https://www.in.gov.br/consulta/",
    }


if __name__ == '__main__':
    nome = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Arthur Lira"
    links = build_transparency_links(nome)
    print(json.dumps({'politico': nome, 'links_transparencia': links}, indent=2, ensure_ascii=False))
