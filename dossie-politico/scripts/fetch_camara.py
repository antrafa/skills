#!/usr/bin/env python3
"""
fetch_camara.py - Consulta e estruturação de dados da API da Câmara dos Deputados.
Fonte oficial: https://dadosabertos.camara.leg.br/api/v2/
"""

import sys
import json
import time
import urllib.error
import urllib.request
import urllib.parse
import unicodedata
from typing import Dict, Any, Optional, List

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.resolve()))
from remuneracao_oficial import (  # noqa: E402
    AUXILIOS_DEPUTADO, CEAP_CONFERIR_EM, contexto_remuneracao, subsidio,
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PoliticoDossie/1.0',
    'Accept': 'application/json'
}

def normalize(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def http_get(url: str, timeout: int = 15, tentativas: int = 3) -> Optional[Dict[str, Any]]:
    """As APIs da Camara e do Senado derrubam handshake com frequencia; uma falha unica nao e resposta."""
    for tentativa in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode('utf-8'))
                return None
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"[WARN] {e.code} ao consultar {url}\n")
            return None
        except Exception as e:
            if tentativa == tentativas:
                sys.stderr.write(f"[WARN] Falha ao consultar {url} apos {tentativas} tentativas: {e}\n")
            else:
                time.sleep(0.6 * tentativa)
    return None

LEGISLATURAS_ANTERIORES = (56, 55, 54)


def _dedupe(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """A mesma pessoa aparece uma vez por legislatura; id repetido não é homônimo."""
    vistos = {}
    for h in hits:
        vistos.setdefault(h.get('id'), h)
    return list(vistos.values())


def find_deputados(nome: str) -> List[Dict[str, Any]]:
    """Todos os deputados compatíveis com o nome, sem escolher por conta própria."""
    norm_query = normalize(nome)
    query_encoded = urllib.parse.quote(nome.strip())
    url_search = f"https://dadosabertos.camara.leg.br/api/v2/deputados?nome={query_encoded}&ordem=ASC&ordenarPor=nome"

    data = http_get(url_search)
    hits = _dedupe((data or {}).get('dados') or [])
    if hits:
        return hits

    url_all = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome&itens=600"
    data_all = http_get(url_all)
    hits = _dedupe([
        d for d in (data_all or {}).get('dados', [])
        if norm_query in normalize(d['nome']) or all(part in normalize(d['nome']) for part in norm_query.split())
    ])
    if hits:
        return hits

    # Ex-deputado: a busca padrão cobre apenas a legislatura corrente.
    for legislatura in LEGISLATURAS_ANTERIORES:
        data_leg = http_get(f"{url_search}&idLegislatura={legislatura}")
        hits = _dedupe((data_leg or {}).get('dados') or [])
        if hits:
            sys.stderr.write(
                f"[INFO] Encontrado apenas na {legislatura}a legislatura: trate como ex-deputado "
                "e confirme mandato e situacao atual.\n"
            )
            return hits
    return []


def describe_candidates(hits: List[Dict[str, Any]]) -> str:
    linhas = "\n".join(
        f"  --id {d.get('id')}  {d.get('nome')} ({d.get('siglaPartido')}-{d.get('siglaUf')})"
        for d in hits
    )
    return (
        f"Nome ambiguo na Camara: {len(hits)} correspondencias. "
        f"Escolha explicitamente para nao gerar o dossie da pessoa errada:\n{linhas}"
    )


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fetch_despesas(dep_id: int, id_legislatura: int = 57, max_paginas: int = 30) -> Dict[str, Any]:
    """Agrega a CEAP por ano, categoria e fornecedor.

    O filtro `?ano=` da API retorna vazio: só `idLegislatura` traz registros.
    Nota fiscal solta não informa nada; o que fiscaliza é o agregado.
    """
    base = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    url: Optional[str] = f"{base}/{dep_id}/despesas?idLegislatura={id_legislatura}&itens=100"
    registros: List[Dict[str, Any]] = []
    paginas = 0
    while url and paginas < max_paginas:
        data = http_get(url)
        if not data:
            break
        registros.extend(data.get('dados') or [])
        url = next((l.get('href') for l in data.get('links', []) if l.get('rel') == 'next'), None)
        paginas += 1

    if not registros:
        return {}

    por_ano: Dict[Any, float] = {}
    por_categoria: Dict[str, Dict[str, Any]] = {}
    por_fornecedor: Dict[str, Dict[str, Any]] = {}
    total = 0.0
    for r in registros:
        valor = float(r.get('valorLiquido') or 0)
        total += valor
        por_ano[r.get('ano')] = por_ano.get(r.get('ano'), 0.0) + valor
        cat = por_categoria.setdefault(r.get('tipoDespesa') or 'Não classificada', {'valor': 0.0, 'notas': 0})
        cat['valor'] += valor
        cat['notas'] += 1
        chave = r.get('cnpjCpfFornecedor') or r.get('nomeFornecedor') or 'Não informado'
        forn = por_fornecedor.setdefault(chave, {'nome': r.get('nomeFornecedor'), 'cnpj_cpf': r.get('cnpjCpfFornecedor'), 'valor': 0.0, 'notas': 0})
        forn['valor'] += valor
        forn['notas'] += 1

    anos = sorted(a for a in por_ano if a)
    return {
        'periodo': f"{anos[0]} a {anos[-1]}" if anos else 'Não informado',
        'total': total,
        'total_formatado': _brl(total),
        'registros_analisados': len(registros),
        'truncado': paginas >= max_paginas,
        'por_ano': [{'ano': a, 'valor': por_ano[a], 'valor_formatado': _brl(por_ano[a])} for a in anos],
        'por_categoria': sorted(
            ({'categoria': k, 'valor': v['valor'], 'valor_formatado': _brl(v['valor']), 'notas': v['notas']}
             for k, v in por_categoria.items()),
            key=lambda c: c['valor'], reverse=True,
        ),
        'principais_fornecedores': sorted(
            ({'nome': v['nome'], 'cnpj_cpf': v['cnpj_cpf'], 'valor': v['valor'],
              'valor_formatado': _brl(v['valor']), 'notas': v['notas']} for v in por_fornecedor.values()),
            key=lambda f: f['valor'], reverse=True,
        )[:10],
    }


def fetch_deputado_por_nome(nome: str, dep_id: Optional[int] = None,
                            com_despesas: bool = True) -> Optional[Dict[str, Any]]:
    dep_summary: Dict[str, Any] = {}
    if dep_id is None:
        hits = find_deputados(nome)
        if not hits:
            return None
        if len(hits) > 1:
            raise LookupError(describe_candidates(hits))
        dep_summary = hits[0]
        dep_id = dep_summary['id']
    
    # Detalhes completos
    det_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}")
    det = det_data.get('dados', {}) if det_data else {}
    
    # Proposições de autoria recente
    props_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor={dep_id}&ordem=DESC&ordenarPor=ano&itens=25")
    props = props_data.get('dados', []) if props_data else []
    
    # Frentes parlamentares
    frentes_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/frentes")
    frentes = frentes_data.get('dados', []) if frentes_data else []
    
    # Órgãos / Comissões
    orgaos_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/orgaos")
    orgaos = orgaos_data.get('dados', []) if orgaos_data else []
    
    # Discursos recentes
    discursos_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/discursos?ordenarPor=dataHoraInicio&ordem=DESC&itens=10")
    discursos = discursos_data.get('dados', []) if discursos_data else []

    ultimo_status = det.get('ultimoStatus', {})
    gabinete = ultimo_status.get('gabinete', {})
    legislatura = ultimo_status.get('idLegislatura', 57)

    despesas = fetch_despesas(dep_id, legislatura) if com_despesas else {}
    despesas_discriminadas = [
        {
            'categoria': c['categoria'].title(),
            'valor': c['valor'],
            'valor_formatado': c['valor_formatado'],
            'detalhe': f"{c['notas']} documento(s) na legislatura {legislatura} ({despesas.get('periodo')}).",
        }
        for c in despesas.get('por_categoria', [])[:8]
    ]

    return {
        'despesas_discriminadas': despesas_discriminadas,
        'despesas_resumo': despesas,
        'fonte': 'Câmara dos Deputados (API Dados Abertos)',
        'id_origem': dep_id,
        'cargo': 'Deputado(a) Federal',
        'nome_eleitoral': ultimo_status.get('nomeEleitoral', dep_summary.get('nome')),
        'nome_civil': det.get('nomeCivil', dep_summary.get('nome')),
        'partido': ultimo_status.get('siglaPartido', dep_summary.get('siglaPartido')),
        'uf': ultimo_status.get('siglaUf', dep_summary.get('siglaUf')),
        'legislatura': legislatura,
        'situacao': ultimo_status.get('situacao', 'Exercício'),
        'condicao_eleitoral': ultimo_status.get('condicaoEleitoral', 'Titular'),
        'foto_url': ultimo_status.get('urlFoto', dep_summary.get('urlFoto')),
        'email': gabinete.get('email') or ultimo_status.get('email'),
        'telefone_gabinete': gabinete.get('telefone'),
        'sala_gabinete': f"Gabinete {gabinete.get('nome')}, Prédio {gabinete.get('predio')}, Sala {gabinete.get('sala')}, Andar {gabinete.get('andar')}" if gabinete else None,
        'data_nascimento': det.get('dataNascimento'),
        'municipio_nascimento': f"{det.get('municipioNascimento', '')} - {det.get('ufNascimento', '')}".strip(" -"),
        'escolaridade': det.get('escolaridade'),
        'redes_sociais': det.get('redeSocial', []),
        'salario_oficial_base': subsidio('Deputado(a) Federal'),
        'salario_contexto': contexto_remuneracao(CEAP_CONFERIR_EM),
        'auxilios_previstos': list(AUXILIOS_DEPUTADO),
        'proposicoes_principais': [
            {
                'id': p.get('id'),
                'tipo': p.get('siglaTipo'),
                'numero': p.get('numero'),
                'ano': p.get('ano'),
                'ementa': p.get('ementa'),
                'data': p.get('dataApresentacao', '')[:10],
                'link': f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={p.get('id')}"
            } for p in props
        ],
        'frentes_parlamentares_count': len(frentes),
        'frentes_destaque': [f.get('titulo') for f in frentes[:8]],
        'comissoes_orgaos': [
            {
                'nome': o.get('nomeOrgao'),
                'sigla': o.get('siglaOrgao'),
                'cargo': o.get('titulo', 'Membro'),
                'data_inicio': o.get('dataInicio')
            } for o in orgaos[:10]
        ],
        'discursos_recentes': [
            {
                'data_hora': d.get('dataHoraInicio'),
                'fase': d.get('faseEvento'),
                'sumario': d.get('sumario')
            } for d in discursos
        ],
        'link_perfil_oficial': f"https://www.camara.leg.br/deputados/{dep_id}",
        'link_transparencia_gastos': f"https://www.camara.leg.br/deputados/{dep_id}/gastos",
        'link_presenca': f"https://www.camara.leg.br/deputados/{dep_id}/presenca-plenario"
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Informe o nome do deputado: python3 fetch_camara.py "<Nome>"'}))
        sys.exit(1)
    
    args = [a for a in sys.argv[1:] if a != '--id']
    dep_id = None
    if '--id' in sys.argv:
        dep_id = int(sys.argv[sys.argv.index('--id') + 1])
        args = [a for a in args if a != str(dep_id)]
    nome_arg = " ".join(args)
    com_despesas = '--sem-despesas' not in sys.argv
    args = [a for a in args if a != '--sem-despesas']
    nome_arg = " ".join(args)
    try:
        resultado = fetch_deputado_por_nome(nome_arg, dep_id, com_despesas)
    except LookupError as exc:
        print(json.dumps({'status': 'ambiguous', 'message': str(exc)}, ensure_ascii=False))
        sys.exit(2)
    if resultado:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({'status': 'not_found', 'message': f'Deputado não encontrado na API da Câmara para: {nome_arg}'}))
