#!/usr/bin/env python3
"""
fetch_senado.py - Consulta e estruturação de dados da API do Senado Federal.
Fonte oficial: https://legis.senado.leg.br/dadosabertos/
"""

import sys
import json
import time
import urllib.error
import urllib.request
import unicodedata
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.resolve()))
from remuneracao_oficial import (  # noqa: E402
    AUXILIOS_SENADOR, CEAPS_CONFERIR_EM, contexto_remuneracao, subsidio,
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

def find_senadores(nome: str) -> List[Dict[str, Any]]:
    """Todos os senadores em exercicio compativeis com o nome, sem escolher sozinho."""
    norm_query = normalize(nome)
    url_lista = "https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json"
    data = http_get(url_lista)
    if not data or 'ListaParlamentarEmExercicio' not in data:
        return []

    parlamentares = data['ListaParlamentarEmExercicio']['Parlamentares'].get('Parlamentar', [])
    hits = []
    for p in parlamentares:
        ident = p.get('IdentificacaoParlamentar', {})
        nome_p = normalize(ident.get('NomeParlamentar', ''))
        nome_c = normalize(ident.get('NomeCompletoParlamentar', ''))
        if norm_query in nome_p or norm_query in nome_c or all(part in nome_p or part in nome_c for part in norm_query.split()):
            hits.append(p)
    return hits


def describe_candidates(hits: List[Dict[str, Any]]) -> str:
    linhas = "\n".join(
        "  --codigo {c}  {n} ({p}-{u})".format(
            c=h.get('IdentificacaoParlamentar', {}).get('CodigoParlamentar'),
            n=h.get('IdentificacaoParlamentar', {}).get('NomeParlamentar'),
            p=h.get('IdentificacaoParlamentar', {}).get('SiglaPartidoParlamentar'),
            u=h.get('IdentificacaoParlamentar', {}).get('UfParlamentar'),
        )
        for h in hits
    )
    return (
        f"Nome ambiguo no Senado: {len(hits)} correspondencias. "
        f"Escolha explicitamente para nao gerar o dossie da pessoa errada:\n{linhas}"
    )


def fetch_senador_por_nome(nome: str, codigo_parlamentar: Optional[str] = None) -> Optional[Dict[str, Any]]:
    hits = find_senadores(nome)
    if codigo_parlamentar is not None:
        hits = [
            h for h in hits
            if str(h.get('IdentificacaoParlamentar', {}).get('CodigoParlamentar')) == str(codigo_parlamentar)
        ] or [{'IdentificacaoParlamentar': {'CodigoParlamentar': str(codigo_parlamentar)}}]
    if not hits:
        return None
    if len(hits) > 1:
        raise LookupError(describe_candidates(hits))
    matched = hits[0]

    ident = matched.get('IdentificacaoParlamentar', {})
    mandato = matched.get('Mandato', {})
    codigo = ident.get('CodigoParlamentar')
    
    # Detalhes completos (tambem cobrem quem foi pedido por --codigo e nao esta na lista atual)
    det_data = http_get(f"https://legis.senado.leg.br/dadosabertos/senador/{codigo}.json")
    det_parlamentar = (det_data or {}).get('DetalheParlamentar', {}).get('Parlamentar', {}) or {}
    if not ident.get('NomeParlamentar'):
        ident = det_parlamentar.get('IdentificacaoParlamentar', ident)
    if not mandato:
        mandato = det_parlamentar.get('MandatoAtual', {}) or {}
    
    # Matérias / Propostas
    materias_lista = []
    try:
        mat_data = http_get(f"https://legis.senado.leg.br/dadosabertos/senador/{codigo}/autorias.json")
        if mat_data and 'MateriasAutoriaParlamentar' in mat_data:
            raw_mat = mat_data['MateriasAutoriaParlamentar']['Parlamentar'].get('Autorias', {}).get('Autoria', [])
            if isinstance(raw_mat, dict):
                raw_mat = [raw_mat]
            materias_lista = raw_mat
    except Exception as e:
        sys.stderr.write(f"[WARN] Erro ao buscar materias do senador: {e}\n")

    # Suplentes
    suplentes = mandato.get('Suplentes', {}).get('Suplente', [])
    if isinstance(suplentes, dict):
        suplentes = [suplentes]

    primeira_leg = mandato.get('PrimeiraLegislaturaDoMandato', {})
    segunda_leg = mandato.get('SegundaLegislaturaDoMandato', {})

    telefones = ident.get('Telefones', {}).get('Telefone', [])
    if isinstance(telefones, dict):
        telefones = [telefones]
    tel_str = ", ".join([f"({t.get('NumeroTelefone')})" for t in telefones if t.get('NumeroTelefone')])

    return {
        'fonte': 'Senado Federal (API Dados Abertos)',
        'id_origem': codigo,
        'cargo': 'Senador(a) da República',
        'nome_eleitoral': ident.get('NomeParlamentar'),
        'nome_civil': ident.get('NomeCompletoParlamentar'),
        'partido': ident.get('SiglaPartidoParlamentar'),
        'uf': ident.get('UfParlamentar'),
        'foto_url': ident.get('UrlFotoParlamentar'),
        'email': ident.get('EmailParlamentar'),
        'telefone_gabinete': tel_str or 'Gabinete Senado',
        'bloco_parlamentar': ident.get('Bloco', {}).get('NomeBloco'),
        'membro_mesa': ident.get('MembroMesa') == 'Sim',
        'membro_lideranca': ident.get('MembroLideranca') == 'Sim',
        'mandato_periodo': f"{primeira_leg.get('DataInicio', '2023-02-01')} a {segunda_leg.get('DataFim', '2031-01-31')}",
        'suplentes': [
            {
                'participacao': s.get('DescricaoParticipacao'),
                'nome': s.get('NomeParlamentar')
            } for s in suplentes
        ],
        'salario_oficial_base': subsidio('Senador(a) da República'),
        'salario_contexto': contexto_remuneracao(CEAPS_CONFERIR_EM),
        'auxilios_previstos': list(AUXILIOS_SENADOR),
        'proposicoes_principais': [
            {
                'id': m.get('Materia', {}).get('Codigo') or m.get('Materia', {}).get('CodigoMateria'),
                'tipo': m.get('Materia', {}).get('Sigla') or m.get('Materia', {}).get('SiglaSubtipoMateria', 'PL'),
                'numero': m.get('Materia', {}).get('Numero') or m.get('Materia', {}).get('NumeroMateria'),
                'ano': m.get('Materia', {}).get('Ano') or m.get('Materia', {}).get('AnoMateria'),
                'ementa': m.get('Materia', {}).get('Ementa') or m.get('Materia', {}).get('EmentaMateria'),
                'data': m.get('Materia', {}).get('Data') or m.get('Materia', {}).get('DataApresentacao'),
                'link': f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{m.get('Materia', {}).get('Codigo') or m.get('Materia', {}).get('CodigoMateria')}"
            } for m in materias_lista[:25] if m.get('Materia')
        ],
        'link_perfil_oficial': ident.get('UrlPaginaParlamentar') or f"https://www25.senado.leg.br/web/senadores/senador/-/perfil/{codigo}",
        'link_transparencia_gastos': f"https://www.senado.leg.br/transparencia/sen/{codigo}/",
        'link_votacoes': f"https://www25.senado.leg.br/web/senadores/senador/-/perfil/{codigo}#votacoes"
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Informe o nome do senador: python3 fetch_senado.py "<Nome>"'}))
        sys.exit(1)
    
    argv = sys.argv[1:]
    codigo = None
    if '--codigo' in argv:
        i = argv.index('--codigo')
        codigo = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    nome_arg = " ".join(argv)
    try:
        resultado = fetch_senador_por_nome(nome_arg, codigo)
    except LookupError as exc:
        print(json.dumps({'status': 'ambiguous', 'message': str(exc)}, ensure_ascii=False))
        sys.exit(2)
    if resultado:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({'status': 'not_found', 'message': f'Senador não encontrado na API do Senado para: {nome_arg}'}))
