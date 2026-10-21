#!/usr/bin/env python3
"""
run_dossier.py - Main orchestrator of the dossie-politico skill.
Runs the search on open APIs (Câmara/Senado/TSE), compiles the dossier JSON, generates the HTML and updates the index in ~/.dossie-politico/
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Import the local modules
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir))

from fetch_camara import fetch_deputado_por_nome
from fetch_senado import fetch_senador_por_nome
from fetch_governo import fetch_dados_governo
from fetch_tse_transparency import build_transparency_links
from generate_dossier_html import build_dossier_file, open_index_file, validate_coverage_record

def run_investigation(
    nome_politico: str,
    extra_data_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    open_index: bool = True,
    render_html: bool = True,
    check_links: bool = True,
    camara_id: Optional[int] = None,
    senado_codigo: Optional[str] = None,
    governo: Optional[str] = None,
) -> Dict[str, Any]:
    extra: Dict[str, Any] = {}
    if extra_data_file:
        if not os.path.exists(extra_data_file):
            raise FileNotFoundError(f"Supplementary data file not found: {extra_data_file}")
        with open(extra_data_file, 'r', encoding='utf-8') as f:
            extra = json.load(f)
    # Fail before the network calls: without cobertura_pesquisa the dossier would be refused at the end.
    if render_html:
        validate_coverage_record(extra)

    if governo:
        print(f"[*] Collecting macroeconomic indicators and government data for: '{governo}'...")
        gov_data = fetch_dados_governo(governo)
        mandato = gov_data.get('mandato_executivo') or {}
        pres_nome = mandato.get('presidente') or governo

        dossier: Dict[str, Any] = {
            'tipo_dossie': 'governo_presidencial',
            'nome': pres_nome,
            'nome_eleitoral': f"Governo {pres_nome}",
            'nome_civil': pres_nome,
            'cargo': f"Presidente da República ({mandato.get('periodo', 'Mandato')})",
            'partido': mandato.get('partido', 'S/ Partido'),
            'uf': 'BR',
            'data_corte': mandato.get('data_fim', 'Não informada'),
            'mandato_periodo': mandato.get('periodo', ''),
            'salario_oficial_base': 'R$ 30.934,70 (Subsídio fixado para a Presidência da República)',
            'salario_label': 'Subsídio Presidencial',
            'salario_contexto': 'Fixado para o Chefe do Poder Executivo Federal',
            'titulo_secao_remuneracao': '💰 Despesas do Executivo e Cartões Corporativos',
            'titulo_secao_atuacao': '📜 Reformas Estruturais e Marcos Legais Sancionados',
            'itens_label': 'Reformas / Atos',
            'titulo_secao_controversias': '🚨 Crises, CPIs, Investigações e Fatos Verificados',
            'resumo_cidadao_ia': {
                'sintese': 'Síntese cidadã ainda não produzida. Consulte as seções detalhadas e as fontes vinculadas.',
                'pontos_chave': [],
                'lacunas': ['Pesquisa complementar e síntese por IA ainda necessárias.'],
                'aviso': 'Conteúdo preliminar; confira todas as fontes antes de formar sua conclusão.'
            },
            'projetos_de_lei_e_reformas': [],
            'promessas_campanha': {
                'total': 0,
                'cumpridas': 0,
                'parciais': 0,
                'nao_cumpridas': 0,
                'itens': []
            },
            'controversias_e_noticias': [],
            'evolucao_patrimonial': [],
            'links_transparencia': {
                'portal_transparencia_federal': 'https://portaldatransparencia.gov.br',
                'bcb_sgs': 'https://www3.bcb.gov.br/sgspub',
                'tesouro_transparente': 'https://www.tesourotransparente.gov.br',
                'tse_divulgacand': 'https://divulgacandcontas.tse.jus.br',
                'stf_jurisprudencia': 'https://portal.stf.jus.br/jurisprudencia',
            }
        }
        dossier.update(gov_data)
    else:
        print(f"[*] Starting the investigation and public audit for: '{nome_politico}'...")
        dossier = {
            'nome': nome_politico,
            'nome_eleitoral': nome_politico,
            'nome_civil': nome_politico,
            'cargo': 'Agente Público',
            'partido': 'A apurar',
            'uf': 'BR',
            'data_corte': 'Não informada',
            'resumo_cidadao_ia': {
                'sintese': 'Síntese cidadã ainda não produzida. Consulte as seções detalhadas e as fontes vinculadas.',
                'pontos_chave': [],
                'lacunas': ['Pesquisa complementar e síntese por IA ainda necessárias.'],
                'aviso': 'Conteúdo preliminar; confira todas as fontes antes de formar sua conclusão.'
            },
            'proposicoes_principais': [],
            'controversias_e_noticias': [],
            'evolucao_patrimonial': [],
            'auxilios_previstos': [],
            'links_transparencia': build_transparency_links(nome_politico)
        }

        # 1. Try the Câmara dos Deputados
        print("[1/3] Querying the Câmara dos Deputados open data API...")
        camara_res = fetch_deputado_por_nome(nome_politico, camara_id)
        if camara_res and camara_res.get('cargo'):
            print(f" [+] Found in the Câmara: {camara_res.get('nome_eleitoral')} ({camara_res.get('partido')}-{camara_res.get('uf')})")
            dossier.update(camara_res)
        else:
            # 2. Try the Senado Federal
            print("[2/3] Querying the Senado Federal open data API...")
            senado_res = fetch_senador_por_nome(nome_politico, senado_codigo)
            if senado_res and senado_res.get('cargo'):
                print(f" [+] Found in the Senado: {senado_res.get('nome_eleitoral')} ({senado_res.get('partido')}-{senado_res.get('uf')})")
                dossier.update(senado_res)
            else:
                print("[!] Not found in the direct APIs for sitting federal legislators (may be a governor, mayor, state deputy or former officeholder).")

    # 3. Merge extra data (news, scandals, TSE, etc.) when provided
    if extra:
        print(f"[*] Merging additional investigation/news data from '{extra_data_file}'...")
        for k, v in extra.items():
            if isinstance(v, list) and k in dossier and isinstance(dossier[k], list):
                dossier[k] = v + dossier[k]
            else:
                dossier[k] = v

    if not render_html:
        return {'status': 'success', 'html_path': None, 'index_path': None,
                'index_opened': False, 'dossier_data': dossier}

    # 4. Generate the HTML file and update the index
    output_html_path = build_dossier_file(dossier, output_dir, check_links=check_links)
    target_folder = os.path.dirname(output_html_path)
    index_path = os.path.join(target_folder, "index.html")
    
    print(f"\n[✓] Dossier completed successfully!")
    print(f"    Report: {output_html_path}")
    print(f"    Main index: {index_path}")
    index_opened = False
    if open_index:
        index_opened = open_index_file(index_path)
        if index_opened:
            print("    Index opened in the default browser.")
        else:
            print("    [!] The index was generated, but the browser did not confirm it opened automatically.")
    
    return {
        'status': 'success',
        'html_path': output_html_path,
        'index_path': index_path,
        'index_opened': index_opened,
        'dossier_data': dossier
    }

def main():
    parser = argparse.ArgumentParser(description="Generates an HTML transparency dossier on a politician or a government term in ~/.dossie-politico/")
    parser.add_argument('nome', nargs='?', default=None, help="Name of the politician to investigate")
    parser.add_argument('--governo', dest='governo', default=None, help="Preset or name of a presidential government (e.g. bolsonaro, lula, fhc, dilma, temer)")
    parser.add_argument('--extra-json', help="Path to a JSON file with news and supplementary data", default=None)
    parser.add_argument('--output-dir', help="Output directory (default: ~/.dossie-politico)", default=None)
    parser.add_argument('--json-only', action='store_true', help="Only prints the JSON data: generates no HTML, leaves the index untouched and opens no browser")
    parser.add_argument('--id', dest='camara_id', type=int, default=None, help="Deputy's Câmara ID, when the name is ambiguous")
    parser.add_argument('--codigo', dest='senado_codigo', default=None, help="Senator's code, when the name is ambiguous")
    parser.add_argument('--no-check-links', action='store_true', help="Does not check whether the cited source URLs resolve")
    parser.add_argument('--no-open-index', action='store_true', help="Does not open the index (tests / headless environments only)")
    
    args = parser.parse_args()

    if not args.nome and not args.governo:
        parser.error("provide the politician's name or use --governo <preset/name>")

    nome_alvo = args.governo or args.nome
    
    try:
        result = run_investigation(
            nome_politico=nome_alvo,
            extra_data_file=args.extra_json,
            output_dir=args.output_dir,
            open_index=not args.no_open_index,
            render_html=not args.json_only,
            check_links=not args.no_check_links,
            camara_id=args.camara_id,
            senado_codigo=args.senado_codigo,
            governo=args.governo,
        )
    except LookupError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1
    if args.json_only:
        print(json.dumps(result['dossier_data'], indent=2, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
