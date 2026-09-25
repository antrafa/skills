#!/usr/bin/env python3
"""
generate_dossier_html.py - Gera um dossiê político interativo, completo e autossuficiente em formato HTML.
Salva o relatório em ~/.dossie-politico/<nome_politico>.html e atualiza o ~/.dossie-politico/index.html
"""

import sys
import os
import json
import html
import re
import datetime
import webbrowser
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional


DEFAULT_PROFILE_IMAGE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 380'%3E"
    "%3Crect width='300' height='380' fill='%231e293b'/%3E"
    "%3Ccircle cx='150' cy='128' r='62' fill='%2364748b'/%3E"
    "%3Cpath d='M48 338c8-78 50-120 102-120s94 42 102 120' fill='%2364748b'/%3E"
    "%3C/svg%3E"
)


def safe_image_url(value: Any) -> str:
    """Retorna a foto informada ou um fallback local sem dependência de rede."""
    candidate = str(value or '').strip()
    return candidate if candidate else DEFAULT_PROFILE_IMAGE


def image_error_handler() -> str:
    """Fallback de uma única execução, evitando laços de erro no navegador."""
    return f"this.onerror=null;this.src='{DEFAULT_PROFILE_IMAGE}'"

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', name).strip()
    return re.sub(r'[-\s]+', '_', cleaned)

def format_currency(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(value) if value else "Não informado"

def get_badge_class(status: str) -> str:
    s = (status or "").lower()
    if any(k in s for k in ['condenad', 'reu', 'denunciad', 'crime', 'cassad', 'inconstitucional', 'não cumprid', 'nao cumprid']):
        return "badge-danger"
    elif any(k in s for k in ['investiga', 'inquerito', 'apuracao', 'suspeita', 'operacao', 'tramita', 'parte', 'parcial', 'em andamento']):
        return "badge-warning"
    elif any(k in s for k in ['arquivad', 'absolvid', 'sem irregularidade', 'rejeitad', 'inocent', 'anulad', 'trancad', 'cumprid']):
        return "badge-success"
    else:
        return "badge-info"


def get_evidence_class(level: str) -> str:
    """Mapeia a força da evidência sem converter a classificação em nota de caráter."""
    normalized = (level or "").lower()
    if any(term in normalized for term in ("confirmado", "documento", "decisão")):
        return "evidence-confirmed"
    if any(term in normalized for term in ("fortemente", "sustentado")):
        return "evidence-supported"
    if any(term in normalized for term in ("apuração", "investigação", "alegação oficial")):
        return "evidence-pending"
    if any(term in normalized for term in ("falso", "enganoso")):
        return "evidence-false"
    return "evidence-unproven"

TRANSPARENCY_LABELS = {
    'portal_transparencia_federal': '🔎 Portal da Transparência — busca geral',
    'portal_transparencia_servidores': '👤 Transparência — remuneração de servidores',
    'cgu_ceis_sancoes': '🚫 CGU/CEIS — empresas sancionadas',
    'cnj_noticias_e_atos': '⚖️ CNJ — atos e notícias',
    'stf_jurisprudencia': '🏛️ STF — jurisprudência',
    'stj_jurisprudencia': '🏛️ STJ — jurisprudência',
    'tse_divulgacand': '🗳️ TSE DivulgaCandContas',
    'tcu_jurisprudencia_e_inabilitados': '📋 TCU — acórdãos e inabilitados',
    'diario_oficial_uniao': '📰 Diário Oficial da União',
}

# Portais em single-page app não aceitam o termo pela URL: o leitor digita o nome.
TRANSPARENCY_MANUAL = {'tse_divulgacand', 'tcu_jurisprudencia_e_inabilitados', 'diario_oficial_uniao'}


def check_url(url: str, timeout: int = 10) -> str:
    """Classifica um link de fonte sem afirmar mais do que a resposta HTTP permite."""
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 DossiePolitico/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 'ok' if resp.status < 400 else f'indisponivel ({resp.status})'
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 429):
            return f'nao verificavel ({exc.code})'
        return f'quebrado ({exc.code})'
    except Exception:
        return 'nao verificado'


def verify_sources(data: Dict[str, Any], workers: int = 8) -> Dict[str, int]:
    """Marca cada fonte citada com o resultado da verificação. Link morto não é auditável."""
    from concurrent.futures import ThreadPoolExecutor

    fontes = [
        f
        for caso in (data.get('controversias_e_noticias') or [])
        if isinstance(caso, dict)
        for f in (caso.get('fontes') or [])
        if isinstance(f, dict) and str(f.get('url', '')).startswith('http')
    ]
    if not fontes:
        return {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for fonte, status in zip(fontes, pool.map(lambda f: check_url(f['url']), fontes)):
            fonte['status_link'] = status
    tally: Dict[str, int] = {}
    for fonte in fontes:
        chave = fonte['status_link'].split(' (')[0]
        tally[chave] = tally.get(chave, 0) + 1
    return tally


def open_index_file(index_path: str) -> bool:
    """Abre o índice local no navegador padrão."""
    try:
        return bool(webbrowser.open(Path(index_path).resolve().as_uri(), new=2))
    except Exception as exc:
        print(f"[!] Não foi possível abrir o índice automaticamente: {exc}", file=sys.stderr)
        return False

def build_citizen_summary(data: Dict[str, Any]) -> Dict[str, str]:
    """Normaliza o resumo cidadão e escapa todo conteúdo antes da renderização."""
    raw = data.get('resumo_cidadao_ia') or {}
    if isinstance(raw, str):
        raw = {'sintese': raw}
    if not isinstance(raw, dict):
        raw = {}

    sintese = str(raw.get('sintese') or '').strip()
    if not sintese:
        sintese = (
            "Este relatório ainda não contém uma síntese cidadã produzida por IA. "
            "Consulte as seções detalhadas e as fontes oficiais vinculadas abaixo."
        )
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', sintese) if p.strip()]
    summary_html = "".join(f"<p>{html.escape(p)}</p>" for p in paragraphs)

    points_html = ""
    for point in raw.get('pontos_chave') or []:
        if isinstance(point, dict):
            title = html.escape(str(point.get('titulo') or 'Ponto-chave'))
            body = html.escape(str(point.get('texto') or ''))
            points_html += f"<li><strong>{title}:</strong> {body}</li>"
        else:
            points_html += f"<li>{html.escape(str(point))}</li>"
    if not points_html:
        points_html = "<li>Consulte as seções detalhadas para formar sua própria conclusão.</li>"

    gaps_html = "".join(
        f"<li>{html.escape(str(gap))}</li>" for gap in (raw.get('lacunas') or [])
    )
    if not gaps_html:
        gaps_html = "<li>Nenhuma lacuna material foi declarada no payload; isso não significa ausência de dados indisponíveis.</li>"

    notice = html.escape(str(raw.get('aviso') or (
        "Síntese gerada por IA a partir dos dados e fontes deste dossiê; "
        "confira os links antes de formar sua conclusão."
    )))
    excerpt = re.sub(r'\s+', ' ', sintese).strip()
    if len(excerpt) > 280:
        excerpt = excerpt[:277].rstrip() + "..."

    return {
        'summary_html': summary_html,
        'points_html': points_html,
        'gaps_html': gaps_html,
        'notice': notice,
        'excerpt': excerpt,
    }


def build_summary_cases(cases: List[Dict[str, Any]]) -> str:
    """Condensa todos os casos catalogados sem omitir estágio, limites ou defesa."""
    if not cases:
        return (
            '<div class="summary-case-empty">Nenhum caso foi catalogado no recorte e nas fontes '
            'consultadas; isso não prova inexistência de outros fatos.</div>'
        )

    rendered = []
    for case in cases:
        title = html.escape(str(case.get('titulo') or 'Fato catalogado'))
        status = html.escape(str(case.get('status') or 'Status não informado'))
        evidence = html.escape(str(case.get('grau_veracidade') or 'Não classificado'))
        summary = html.escape(str(case.get('resumo') or 'Resumo não informado.'))
        proven = html.escape(str(case.get('o_que_esta_comprovado') or 'Não informado.'))
        unproven = html.escape(str(case.get('o_que_nao_esta_comprovado') or 'Não informado.'))
        defense = html.escape(str(case.get('posicao_defesa') or (
            'Manifestação da defesa não localizada no recorte pesquisado.'
        )))
        rendered.append(f"""
            <details class="summary-case">
                <summary>
                    <span>{title}</span>
                    <span class="summary-case-status">{status} • {evidence}</span>
                </summary>
                <p>{summary}</p>
                <ul>
                    <li><strong>Comprovado:</strong> {proven}</li>
                    <li><strong>Não comprovado:</strong> {unproven}</li>
                </ul>
                <p class="summary-case-defense"><strong>Defesa / desfecho:</strong> {defense}</p>
            </details>
        """)
    return ''.join(rendered)

def generate_dossier_html(data: Dict[str, Any]) -> str:
    nome_eleitoral = html.escape(data.get('nome_eleitoral') or data.get('nome') or 'Político')
    nome_civil = html.escape(data.get('nome_civil') or nome_eleitoral)
    cargo = html.escape(data.get('cargo') or 'Agente Público')
    partido = html.escape(data.get('partido') or 'S/ Partido')
    uf = html.escape(data.get('uf') or 'BR')
    foto_url = safe_image_url(data.get('foto_url'))
    salario_base = html.escape(str(data.get('salario_oficial_base') or 'Não informado'))
    data_geracao = data.get('data_geracao') or datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    data_corte = html.escape(str(data.get('data_corte') or 'Não informada'))
    status_eleitoral = html.escape(str(data.get('status_eleitoral') or 'Não se aplica / não informado'))
    situacao = html.escape(str(data.get('situacao') or 'Não informada'))
    mandato_periodo = html.escape(str(data.get('mandato_periodo') or data.get('legislatura') or 'Não informado'))
    municipio_nascimento = html.escape(str(data.get('municipio_nascimento') or 'Não informado'))
    escolaridade = html.escape(str(data.get('escolaridade') or 'Não informada'))
    telefone_gabinete = html.escape(str(data.get('telefone_gabinete') or 'Não informado'))
    salario_contexto = html.escape(str(data.get('salario_contexto') or 'Consulte a fonte oficial do cargo e do período analisado'))
    salario_label = html.escape(str(data.get('salario_label') or 'Salário Base Mensal'))
    assiduidade_label = html.escape(str(data.get('assiduidade_label') or 'Assiduidade Parlamentar'))
    assiduidade_contexto = html.escape(str(data.get('assiduidade_contexto') or 'Presença em sessões deliberativas'))
    remuneration_section_title = html.escape(str(data.get('titulo_secao_remuneracao') or '💰 Remuneração, Cotas e Verbas Públicas'))
    remuneration_description = html.escape(str(data.get('remuneracao_descricao') or (
        'Além do subsídio mensal bruto, o mandato pode dispor de verbas operacionais e '
        'indenizatórias regulamentadas pelo órgão competente.'
    )))
    activity_section_title = html.escape(str(data.get('titulo_secao_atuacao') or '📜 Atuação Legislativa e Principais Projetos'))
    empty_controversies_note = html.escape(str(data.get('controversias_nota') or (
        'Nenhuma investigação, processo ou controvérsia foi registrada no payload até a data de corte. '
        'Isso descreve o conteúdo pesquisado e não prova a inexistência de outros fatos.'
    )))
    controversies_section_title = html.escape(str(data.get('titulo_secao_controversias') or (
        '🚨 Escândalos, polêmicas e fatos verificados'
    )))
    citizen_summary = build_citizen_summary(data)
    # Peso proporcional é exigência da ética da skill, mas nada avisava quando o dossiê pendia.
    n_casos = len(data.get('controversias_e_noticias') or [])
    n_atuacao = len(data.get('proposicoes_principais') or [])
    proporcao_aviso = ""
    if n_casos >= 3 and n_atuacao == 0:
        proporcao_aviso = (
            f"Este relatório reúne {n_casos} caso(s) de controvérsia e nenhum registro de atuação ou "
            "proposição. A desproporção pode indicar lacuna da pesquisa, e não o retrato da pessoa: "
            "complete a coleta de atividade pública antes de tratar o dossiê como equilibrado."
        )
    elif n_atuacao >= 5 and n_casos == 0:
        proporcao_aviso = (
            f"Este relatório reúne {n_atuacao} registro(s) de atuação e nenhum caso de controvérsia "
            "no recorte pesquisado. Isso descreve o que foi encontrado, não comprova ausência de fatos."
        )
    proporcao_aviso_html = (
        f'<p class="proportion-warning">⚖️ {html.escape(proporcao_aviso)}</p>' if proporcao_aviso else ''
    )
    coverage = data.get('cobertura_pesquisa') or {}

    coverage_html = ""
    if isinstance(coverage, dict) and coverage:
        coverage_date = html.escape(str(coverage.get('data_execucao') or data.get('data_corte') or 'Não informada'))
        coverage_period = html.escape(str(coverage.get('periodo') or 'Não informado'))

        def coverage_list(label: str, key: str) -> str:
            values = coverage.get(key) or []
            if not isinstance(values, list):
                values = [values]
            clean_values = [html.escape(str(value)) for value in values if str(value).strip()]
            if not clean_values:
                return ""
            return f"<li><strong>{label}:</strong> {'; '.join(clean_values)}</li>"

        coverage_html = f"""
            <details class="coverage-audit card">
                <summary>Como esta busca foi feita</summary>
                <p>Registro de cobertura para que o leitor conheça o alcance e os limites deste levantamento.</p>
                <ul>
                    <li><strong>Executada em:</strong> {coverage_date}</li>
                    <li><strong>Período:</strong> {coverage_period}</li>
                    {coverage_list('Nomes e vínculos consultados', 'nomes_consultados')}
                    {coverage_list('Eixos verificados', 'eixos_verificados')}
                    {coverage_list('Fontes e portais', 'fontes_consultadas')}
                    {coverage_list('Limitações', 'limitacoes')}
                </ul>
            </details>
        """
    
    # KPIs
    assiduidade = html.escape(str(data.get('assiduidade_percentual') or 'Não informada'))
    props_total = len(data.get('proposicoes_principais', []))
    controversias = data.get('controversias_e_noticias', [])
    controversias_total = len(controversias)
    summary_cases_html = build_summary_cases(controversias)
    patrimonio_recente = html.escape(str(data.get('patrimonio_declarado_recente') or 'Consultar TSE'))
    if patrimonio_recente == 'Consultar TSE' and data.get('evolucao_patrimonial'):
        patrimonio_recente = html.escape(str(data['evolucao_patrimonial'][0].get('valor_formatado') or 'Consultar TSE'))
    
    # Auxílios
    auxilios = data.get('auxilios_previstos', [])
    auxilios_html = "".join([f"<li><span class='bullet'>•</span> <div>{html.escape(str(a))}</div></li>" for a in auxilios]) if auxilios else "<li>Sem auxílios adicionais cadastrados.</li>"
    
    # Despesas discriminadas
    gastos_detalhados = data.get('despesas_discriminadas', [])
    gastos_html = ""
    if gastos_detalhados:
        for g in gastos_detalhados:
            categoria = html.escape(str(g.get('categoria', 'Despesa')))
            valor = html.escape(str(g.get('valor_formatado') or format_currency(g.get('valor', 0))))
            detalhe = html.escape(str(g.get('detalhe', '')))
            gastos_html += f"""
            <div class="expense-card">
                <div class="expense-header">
                    <span class="expense-category">{categoria}</span>
                    <span class="expense-value">{valor}</span>
                </div>
                <div class="expense-detail">{detalhe}</div>
            </div>
            """

    # Resumo agregado da cota parlamentar
    despesas_resumo = data.get('despesas_resumo') or {}
    despesas_resumo_html = ""
    if isinstance(despesas_resumo, dict) and despesas_resumo.get('por_ano'):
        anos_html = "".join(
            f"<tr class='table-row'><td class='td-year'><strong>{html.escape(str(a.get('ano')))}</strong></td>"
            f"<td class='td-value'>{html.escape(str(a.get('valor_formatado') or format_currency(a.get('valor'))))}</td></tr>"
            for a in despesas_resumo['por_ano']
        )
        fornecedores_html = "".join(
            "<li><strong>{nome}</strong> — {valor} em {notas} documento(s){doc}</li>".format(
                nome=html.escape(str(f.get('nome') or 'Fornecedor não informado')),
                valor=html.escape(str(f.get('valor_formatado') or format_currency(f.get('valor')))),
                notas=html.escape(str(f.get('notas') or 0)),
                doc=f" <span class='text-muted'>(CNPJ/CPF {html.escape(str(f.get('cnpj_cpf')))})</span>" if f.get('cnpj_cpf') else "",
            )
            for f in despesas_resumo.get('principais_fornecedores', [])
        )
        truncado = (
            "<p class='text-muted'>Leitura interrompida no limite de páginas da API: o total mostrado é parcial.</p>"
            if despesas_resumo.get('truncado') else ""
        )
        despesas_resumo_html = f"""
            <div class="card">
                <h3 class="card-title">🧾 Uso da cota parlamentar (CEAP)</h3>
                <p style="margin-bottom: 14px; font-size: 0.92rem;">
                    <strong>{html.escape(str(despesas_resumo.get('total_formatado') or format_currency(despesas_resumo.get('total'))))}</strong>
                    reembolsados em {html.escape(str(despesas_resumo.get('registros_analisados') or 0))} documentos no período
                    {html.escape(str(despesas_resumo.get('periodo') or 'não informado'))}, somados a partir das notas publicadas na
                    API de Dados Abertos da Câmara. Valores reembolsados não indicam irregularidade por si.
                </p>
                {truncado}
                <table class="data-table">
                    <thead><tr><th>Ano</th><th>Total reembolsado</th></tr></thead>
                    <tbody>{anos_html}</tbody>
                </table>
                <h3 class="card-title" style="margin-top: 18px;">Principais fornecedores</h3>
                <ul class="styled-list">{fornecedores_html}</ul>
            </div>
        """

    # Redes sociais
    redes = data.get('redes_sociais', [])
    redes_html = ""
    if isinstance(redes, list):
        for r in redes:
            if isinstance(r, str) and r.startswith('http'):
                platform = "Link Oficial"
                if "twitter.com" in r or "x.com" in r: platform = "𝕏 Twitter"
                elif "instagram.com" in r: platform = "📸 Instagram"
                elif "facebook.com" in r: platform = "📘 Facebook"
                elif "youtube.com" in r: platform = "▶️ YouTube"
                redes_html += f"<a href='{html.escape(r)}' target='_blank' rel='noopener' class='social-pill'>{platform} ↗</a> "
            elif isinstance(r, dict):
                redes_html += f"<a href='{html.escape(r.get('url', '#'))}' target='_blank' rel='noopener' class='social-pill'>{html.escape(r.get('rede', 'Social'))} ↗</a> "
    if not redes_html:
        redes_html = "<span class='text-muted'>Não cadastradas oficialmente</span>"

    # Proposições
    props = data.get('proposicoes_principais', [])
    props_html = ""
    if props:
        for p in props:
            sigla = html.escape(str(p.get('tipo', 'PL')))
            num = html.escape(str(p.get('numero', '')))
            ano = html.escape(str(p.get('ano', '')))
            ementa = html.escape(str(p.get('ementa', 'Sem ementa disponível.')))
            data_p = html.escape(str(p.get('data', '')))
            status_tram = html.escape(str(p.get('status_tramitacao') or 'Status não informado'))
            link_p = p.get('link') or "#"
            link_label = html.escape(str(p.get('link_label') or 'Ver ficha de tramitação e texto integral'))
            props_html += f"""
            <div class="proposal-card">
                <div class="proposal-header">
                    <span class="proposal-type">{sigla} {num}/{ano}</span>
                    <span class="proposal-status-badge">{status_tram}</span>
                    <span class="proposal-date">{data_p}</span>
                </div>
                <p class="proposal-ementa">{ementa}</p>
                <div class="proposal-footer">
                    <a href="{html.escape(link_p)}" target="_blank" rel="noopener" class="btn-link">{link_label} ↗</a>
                </div>
            </div>
            """
    else:
        props_html = "<p class='text-muted'>Nenhuma proposição registrada no período analisado.</p>"

    # Notícias e Controvérsias
    controversias_html = ""
    categories_set = set()
    if controversias:
        for idx, c in enumerate(controversias):
            titulo = html.escape(str(c.get('titulo', 'Fato Registrado')))
            data_c = html.escape(str(c.get('data') or 'Data não informada'))
            tipo = str(c.get('categoria', 'Notícia / Investigação'))
            categories_set.add(tipo)
            status = html.escape(str(c.get('status') or 'Status não classificado'))
            badge_cls = get_badge_class(status)
            resumo = html.escape(str(c.get('resumo', '')))
            posicao_defesa = html.escape(str(c.get('posicao_defesa') or 'Manifestação da defesa não localizada no recorte pesquisado.'))
            evidence_level = html.escape(str(c.get('grau_veracidade') or 'Não classificado'))
            evidence_class = get_evidence_class(str(c.get('grau_veracidade') or ''))
            evidence_criteria = html.escape(str(c.get('criterio_veracidade') or (
                'Classificação ainda não fundamentada no payload; consulte as fontes vinculadas.'
            )))
            proven = html.escape(str(c.get('o_que_esta_comprovado') or (
                'Somente a existência das fontes e do estágio processual descrito foi documentada.'
            )))
            unproven = html.escape(str(c.get('o_que_nao_esta_comprovado') or (
                'A responsabilidade pessoal e as alegações de mérito não devem ser presumidas.'
            )))
            fontes = c.get('fontes', [])
            
            fontes_links = ""
            if isinstance(fontes, list):
                for f in fontes:
                    if isinstance(f, dict) and not str(f.get('url') or '').startswith('http'):
                        # Veículo e data sem URL: melhor declarar a lacuna do que citar link inventado.
                        f_nome = html.escape(str(f.get('veiculo') or 'Fonte'))
                        f_data = html.escape(str(f.get('data') or ''))
                        sufixo = f" ({f_data})" if f_data else ""
                        fontes_links += (
                            f"<span class='source-tag source-nolink' title='URL não localizada; confira pelo "
                            f"nome do veículo e pela data'>📄 {f_nome}{sufixo} — URL não localizada</span> "
                        )
                    elif isinstance(f, dict):
                        f_nome = html.escape(f.get('veiculo', 'Fonte'))
                        f_url = html.escape(f.get('url', '#'))
                        f_status = str(f.get('status_link') or '')
                        if f_status.startswith('quebrado') or f_status.startswith('indisponivel'):
                            mark, cls, hint = '⚠️', 'source-tag source-dead', f'Link não resolveu na verificação: {html.escape(f_status)}'
                        elif f_status.startswith('nao verificavel'):
                            mark, cls, hint = '🔒', 'source-tag', f'Site bloqueou a verificação automática: {html.escape(f_status)}'
                        elif f_status == 'ok':
                            mark, cls, hint = '🔗', 'source-tag', 'Link verificado na geração do dossiê'
                        else:
                            mark, cls, hint = '🔗', 'source-tag', 'Link não verificado automaticamente'
                        fontes_links += f"<a href='{f_url}' target='_blank' rel='noopener' class='{cls}' title='{hint}'>{mark} {f_nome}</a> "
                    elif isinstance(f, str) and f.startswith('http'):
                        fontes_links += f"<a href='{html.escape(f)}' target='_blank' rel='noopener' class='source-tag'>🔗 Matéria Original</a> "

            fallback_fontes = "<span class='text-muted'>Nenhuma fonte vinculada; verificação pendente.</span>"
            final_fontes = fontes_links if fontes_links else fallback_fontes

            cat_slug = re.sub(r'\W+', '_', tipo.lower())

            controversias_html += f"""
            <div class="timeline-item" data-category="{cat_slug}">
                <div class="timeline-marker"></div>
                <div class="timeline-content card">
                    <div class="timeline-header">
                        <div class="timeline-tags">
                            <span class="category-tag">{html.escape(tipo)}</span>
                            <span class="badge {badge_cls}">{status}</span>
                            <span class="evidence-badge {evidence_class}">🔎 {evidence_level}</span>
                        </div>
                        <span class="timeline-date">📅 {data_c}</span>
                    </div>
                    <h3 class="timeline-title">{titulo}</h3>
                    <div class="timeline-text">
                        <p>{resumo}</p>
                    </div>
                    <div class="evidence-box">
                        <strong>🔎 Grau de veracidade / força da evidência:</strong>
                        <p>{evidence_criteria}</p>
                        <ul>
                            <li><strong>O que está comprovado:</strong> {proven}</li>
                            <li><strong>O que não está comprovado:</strong> {unproven}</li>
                        </ul>
                    </div>
                    <div class="defense-box">
                        <strong>⚖️ Posição da Defesa / Desfecho Jurídico:</strong>
                        <p>{posicao_defesa}</p>
                    </div>
                    <div class="sources-box">
                        <span class="sources-label">Fontes Auditadas:</span> {final_fontes}
                    </div>
                </div>
            </div>
            """
    else:
        controversias_html = f"""
        <div class="empty-state card">
            <p>{empty_controversies_note}</p>
        </div>
        """

    # Filter buttons for controversies
    filter_buttons_html = "<button class='filter-btn active' onclick='filterControversies(\"all\", this)'>Todos ({})</button>".format(controversias_total)
    for cat in sorted(categories_set):
        cat_slug = re.sub(r'\W+', '_', cat.lower())
        count = sum(1 for item in controversias if item.get('categoria') == cat)
        filter_buttons_html += f"<button class='filter-btn' onclick='filterControversies(\"{cat_slug}\", this)'>{html.escape(cat)} ({count})</button>"

    # Evolução Patrimonial
    patrimonio_list = data.get('evolucao_patrimonial', [])
    patrimonio_html = ""
    if patrimonio_list:
        for p in patrimonio_list:
            ano_eleicao = html.escape(str(p.get('ano', '')))
            cargo_disp = html.escape(str(p.get('cargo_disputado', '')))
            valor = html.escape(str(p.get('valor_formatado') or format_currency(p.get('valor', 0))))
            variacao = html.escape(str(p.get('variacao_percentual', '-')))
            detalhe_bens = html.escape(str(p.get('principais_bens') or 'Detalhamento não localizado'))
            patrimonio_html += f"""
            <tr class="table-row">
                <td class="td-year"><strong>{ano_eleicao}</strong></td>
                <td><span class="badge-subtle">{cargo_disp}</span></td>
                <td class="td-value">{valor}</td>
                <td><span class="growth-tag">{variacao}</span></td>
                <td class="td-details">{detalhe_bens}</td>
            </tr>
            """
    else:
        patrimonio_html = "<tr><td colspan='5' class='text-muted text-center'>Consulte o portal TSE DivulgaCandContas para histórico eleitoral de bens.</td></tr>"

    # Atuação institucional (coletada pelas APIs e antes descartada na renderização)
    def _lista(items, render):
        return "".join(render(i) for i in items if i)

    comissoes = data.get('comissoes_orgaos') or []
    comissoes_html = _lista(
        [c for c in comissoes if isinstance(c, dict)],
        lambda o: "<li><strong>{sigla}</strong> {nome} — {cargo}{desde}</li>".format(
            sigla=html.escape(str(o.get('sigla') or '')),
            nome=html.escape(str(o.get('nome') or '')),
            cargo=html.escape(str(o.get('cargo') or 'Membro')),
            desde=f" <span class='text-muted'>(desde {html.escape(str(o.get('data_inicio'))[:10])})</span>" if o.get('data_inicio') else "",
        ),
    )

    frentes = data.get('frentes_destaque') or []
    frentes_total = data.get('frentes_parlamentares_count')
    frentes_html = _lista(frentes, lambda f: f"<li>{html.escape(str(f))}</li>")

    discursos = data.get('discursos_recentes') or []
    discursos_html = _lista(
        [d for d in discursos if isinstance(d, dict)],
        lambda d: "<li><strong>{dt}</strong> — {sumario}</li>".format(
            dt=html.escape(str(d.get('data_hora') or '')[:10]),
            sumario=html.escape(str(d.get('sumario') or d.get('fase') or 'Sem sumário registrado')),
        ),
    )

    suplentes = data.get('suplentes') or []
    suplentes_html = _lista(
        [x for x in suplentes if isinstance(x, dict)],
        lambda x: f"<li>{html.escape(str(x.get('participacao') or 'Suplente'))}: {html.escape(str(x.get('nome') or 'Não informado'))}</li>",
    )

    institucional_blocos = ""
    if comissoes_html:
        institucional_blocos += f"<div class='card'><h3 class='card-title'>🏛️ Comissões e órgãos</h3><ul class='styled-list'>{comissoes_html}</ul></div>"
    if frentes_html:
        total_txt = f" ({frentes_total} no total)" if frentes_total else ""
        institucional_blocos += f"<div class='card'><h3 class='card-title'>🤝 Frentes parlamentares{html.escape(total_txt)}</h3><ul class='styled-list'>{frentes_html}</ul></div>"
    if suplentes_html:
        institucional_blocos += f"<div class='card'><h3 class='card-title'>👥 Suplentes do mandato</h3><ul class='styled-list'>{suplentes_html}</ul></div>"
    if discursos_html:
        institucional_blocos += f"<div class='card'><h3 class='card-title'>🎙️ Discursos recentes em plenário</h3><ul class='styled-list'>{discursos_html}</ul></div>"

    institucional_html = ""
    if institucional_blocos:
        institucional_html = f"""
        <section>
            <h2 class="section-title">🏛️ Atuação institucional</h2>
            <div class="proposals-grid">{institucional_blocos}</div>
        </section>
        """

    # Links de transparência para conferência independente
    links_transp = data.get('links_transparencia') or {}
    transparencia_html = ""
    if isinstance(links_transp, dict):
        transparencia_html = "".join(
            f"<a href='{html.escape(str(url))}' target='_blank' rel='noopener' class='btn-link'>"
            f"{html.escape(TRANSPARENCY_LABELS.get(key, key.replace('_', ' ').capitalize()))}"
            f"{' (digite o nome)' if key in TRANSPARENCY_MANUAL else ''} ↗</a>"
            for key, url in links_transp.items()
            if isinstance(url, str) and url.startswith('http')
        )
    if transparencia_html:
        transparencia_html = f"""
        <section>
            <h2 class="section-title">🔎 Onde conferir por conta própria</h2>
            <div class="card">
                <p style="margin-bottom: 14px; font-size: 0.92rem;">
                    Buscas abertas nos portais oficiais. São pontos de partida de consulta pública, não resultados já apurados
                    neste dossiê. Onde aparece “(digite o nome)”, o portal não aceita o termo pela URL: pesquise por
                    <strong>{nome_eleitoral}</strong> ou <strong>{nome_civil}</strong>.
                </p>
                <div style="display: flex; gap: 14px; flex-wrap: wrap;">{transparencia_html}</div>
            </div>
        </section>
        """

    # Identificação complementar
    email_contato = html.escape(str(data.get('email') or 'Não informado'))
    data_nascimento = html.escape(str(data.get('data_nascimento') or 'Não informada'))
    gabinete_sala = html.escape(str(data.get('sala_gabinete') or ''))
    bloco_parlamentar = html.escape(str(data.get('bloco_parlamentar') or ''))
    bio_extra_html = f"""
                    <div class="bio-item">
                        <span class="bio-label">Nascimento</span>
                        <span class="bio-val">{data_nascimento}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">E-mail institucional</span>
                        <span class="bio-val">{email_contato}</span>
                    </div>"""
    if bloco_parlamentar:
        bio_extra_html += f"""
                    <div class="bio-item">
                        <span class="bio-label">Bloco / Liderança</span>
                        <span class="bio-val">{bloco_parlamentar}</span>
                    </div>"""
    if gabinete_sala:
        bio_extra_html += f"""
                    <div class="bio-item">
                        <span class="bio-label">Endereço do gabinete</span>
                        <span class="bio-val">{gabinete_sala}</span>
                    </div>"""

    tipo_dossie = data.get('tipo_dossie') or ('governo_presidencial' if data.get('mandato_executivo') else 'perfil_politico')
    is_governo = (tipo_dossie == 'governo_presidencial')

    mandato = data.get('mandato_executivo') or {}
    if is_governo and mandato.get('vice'):
        bio_extra_html += f"""
                    <div class="bio-item">
                        <span class="bio-label">Vice-Presidente</span>
                        <span class="bio-val">{html.escape(str(mandato.get('vice')))}</span>
                    </div>"""

    # 1. Mandato Executivo e Ministros Notáveis
    governo_ministerio_html = ""
    if is_governo and mandato:
        ministros = mandato.get('ministros_notaveis') or []
        ministros_li = "".join(
            f"<li><strong>{html.escape(str(m.get('pasta', 'Ministério')))}:</strong> {html.escape(str(m.get('nome', '')))}</li>"
            for m in ministros if isinstance(m, dict)
        )
        pres_nome = html.escape(str(mandato.get('presidente') or nome_civil))
        vice_nome = html.escape(str(mandato.get('vice') or 'Não informado'))
        periodo_gestao = html.escape(str(mandato.get('periodo') or mandato_periodo))
        mandatos_str = html.escape(str(mandato.get('mandatos') or ''))

        governo_ministerio_html = f"""
        <section>
            <h2 class="section-title">🏛️ Mandato Executivo e Equipe Ministerial</h2>
            <div class="proposals-grid">
                <div class="card">
                    <h3 class="card-title">👤 Chefia do Poder Executivo</h3>
                    <ul class="styled-list">
                        <li><strong>Presidente da República:</strong> {pres_nome}</li>
                        <li><strong>Vice-Presidente:</strong> {vice_nome}</li>
                        <li><strong>Período de Gestão:</strong> {periodo_gestao} ({mandatos_str})</li>
                        <li><strong>Partido Político:</strong> {partido}</li>
                    </ul>
                </div>
                <div class="card">
                    <h3 class="card-title">🏛️ Equipe Ministerial de Destaque</h3>
                    <ul class="styled-list">
                        {ministros_li if ministros_li else "<li>Sem ministros notáveis cadastrados.</li>"}
                    </ul>
                </div>
            </div>
        </section>
        """

    # 2. Indicadores Macroeconômicos e Contas Públicas (BCB SGS)
    indicadores = data.get('indicadores_economicos') or {}
    resumo_macro = indicadores.get('resumo_macro') or {}
    grafico_anual = indicadores.get('grafico_anual') or []
    cofres = data.get('cofres_publicos') or {}

    governo_macro_html = ""
    if is_governo and (indicadores or cofres):
        ipca_acum = resumo_macro.get('ipca_acumulado')
        ipca_acum_str = f"{ipca_acum:.2f}%" if isinstance(ipca_acum, (int, float)) else "Não informado"
        ipca_media = resumo_macro.get('ipca_media_anual')
        ipca_media_str = f"{ipca_media:.2f}% a.a." if isinstance(ipca_media, (int, float)) else "Não informado"

        selic_ini = resumo_macro.get('selic_inicial')
        selic_fim = resumo_macro.get('selic_final')
        selic_med = resumo_macro.get('selic_media')
        selic_fim_str = f"{selic_fim:.2f}% a.a." if isinstance(selic_fim, (int, float)) else "Não informado"

        dolar_ini = resumo_macro.get('dolar_inicial')
        dolar_fim = resumo_macro.get('dolar_final')
        dolar_var = resumo_macro.get('dolar_variacao_pct')
        dolar_fim_str = f"R$ {dolar_fim:.2f}" if isinstance(dolar_fim, (int, float)) else "Não informado"
        dolar_var_str = f"{'+' if (dolar_var or 0) > 0 else ''}{dolar_var:.2f}%" if isinstance(dolar_var, (int, float)) else ""

        div_ini = resumo_macro.get('divida_bruta_inicial')
        div_fim = resumo_macro.get('divida_bruta_final')
        div_var = resumo_macro.get('divida_bruta_variacao_pp')
        div_fim_str = f"{div_fim:.2f}% PIB" if isinstance(div_fim, (int, float)) else "Não informado"
        div_var_str = f"{'+' if (div_var or 0) > 0 else ''}{div_var:.2f} p.p." if isinstance(div_var, (int, float)) else ""

        macro_kpis_html = f"""
        <div class="kpi-grid" style="margin-bottom: 24px;">
            <div class="kpi-card">
                <div class="kpi-title">Inflação (IPCA) Acumulada</div>
                <div class="kpi-value">{ipca_acum_str}</div>
                <div class="kpi-subtext">Média anual: {ipca_media_str}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Taxa Selic no Término</div>
                <div class="kpi-value">{selic_fim_str}</div>
                <div class="kpi-subtext">Início: {selic_ini if selic_ini is not None else '-'}% | Média: {selic_med if selic_med is not None else '-'}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Câmbio Dólar Comercial (PTAX)</div>
                <div class="kpi-value">{dolar_fim_str}</div>
                <div class="kpi-subtext">Início: R$ {dolar_ini if dolar_ini is not None else '-'} ({dolar_var_str})</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Dívida Bruta do Governo (% PIB)</div>
                <div class="kpi-value">{div_fim_str}</div>
                <div class="kpi-subtext">Início: {div_ini if div_ini is not None else '-'}% ({div_var_str})</div>
            </div>
        </div>
        """

        anual_rows = ""
        for ano_item in grafico_anual:
            ano_val = html.escape(str(ano_item.get('ano', '')))
            ipca_v = f"{ano_item['ipca']:.2f}%" if isinstance(ano_item.get('ipca'), (int, float)) else "-"
            selic_v = f"{ano_item['selic_fim']:.2f}%" if isinstance(ano_item.get('selic_fim'), (int, float)) else "-"
            dolar_v = f"R$ {ano_item['dolar_fim']:.4f}" if isinstance(ano_item.get('dolar_fim'), (int, float)) else "-"
            div_v = f"{ano_item['divida_bruta_pib']:.2f}%" if isinstance(ano_item.get('divida_bruta_pib'), (int, float)) else "-"
            pib_v = f"{ano_item['pib_crescimento']:.2f}%" if isinstance(ano_item.get('pib_crescimento'), (int, float)) else "-"
            anual_rows += f"""
            <tr class="table-row">
                <td class="td-year"><strong>{ano_val}</strong></td>
                <td class="td-value">{ipca_v}</td>
                <td class="td-value">{selic_v}</td>
                <td class="td-value">{dolar_v}</td>
                <td class="td-value">{div_v}</td>
                <td class="td-value">{pib_v}</td>
            </tr>
            """

        anual_table_html = f"""
        <div class="card" style="padding: 0; overflow-x: auto; margin-bottom: 24px;">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Ano</th>
                        <th>Inflação (IPCA)</th>
                        <th>Taxa Selic (Fim do Ano)</th>
                        <th>Dólar PTAX (Fim do Ano)</th>
                        <th>Dívida Bruta (% PIB)</th>
                        <th>Crescimento Real do PIB</th>
                    </tr>
                </thead>
                <tbody>
                    {anual_rows if anual_rows else "<tr><td colspan='6' class='text-muted text-center'>Séries anuais não informadas.</td></tr>"}
                </tbody>
            </table>
        </div>
        """ if grafico_anual else ""

        fontes_cofres = cofres.get('fontes') or []
        fontes_cofres_html = "".join(f"<li>{html.escape(str(f))}</li>" for f in fontes_cofres)
        cofres_detalhes_html = ""
        if cofres:
            res_fiscal = html.escape(str(cofres.get('resultado_fiscal_acumulado') or 'Não informado'))
            div_traj = html.escape(str(cofres.get('divida_publica_trajetoria') or 'Não informado'))
            cartao = html.escape(str(cofres.get('cartao_corporativo_total') or 'Não informado'))
            cofres_detalhes_html = f"""
            <div class="card">
                <h3 class="card-title">🏛️ Contas Públicas e Despesas do Poder Executivo</h3>
                <p style="margin-bottom: 12px; font-size: 0.92rem;">{html.escape(str(cofres.get('descricao') or 'Dados consolidados das finanças federais.'))}</p>
                <ul class="styled-list">
                    <li><strong>Resultado Primário / Fiscal:</strong> {res_fiscal}</li>
                    <li><strong>Trajetória da Dívida Pública:</strong> {div_traj}</li>
                    <li><strong>Cartões Corporativos / Suprimento da Presidência:</strong> {cartao}</li>
                </ul>
                <div style="margin-top: 14px; font-size: 0.85rem; color: var(--text-muted);">
                    <strong>Fontes oficiais:</strong>
                    <ul style="margin-top: 4px; padding-left: 20px;">{fontes_cofres_html}</ul>
                </div>
            </div>
            """

        governo_macro_html = f"""
        <section>
            <h2 class="section-title">📊 Indicadores Macroeconômicos e Contas Públicas (Banco Central do Brasil - SGS)</h2>
            {macro_kpis_html}
            {anual_table_html}
            {cofres_detalhes_html}
        </section>
        """

    # 3. Balanço de Promessas de Campanha
    promessas_data = data.get('promessas_campanha') or {}
    governo_promessas_html = ""
    if is_governo and promessas_data:
        total_p = promessas_data.get('total', 0)
        cump = promessas_data.get('cumpridas', 0)
        parc = promessas_data.get('parciais', 0)
        nao_cump = promessas_data.get('nao_cumpridas', 0)
        taxa = promessas_data.get('taxa_cumprimento_pct')
        if taxa is None and total_p > 0:
            taxa = round((cump / total_p) * 100.0, 1)

        pct_cump = (cump / total_p * 100.0) if total_p > 0 else 0
        pct_parc = (parc / total_p * 100.0) if total_p > 0 else 0
        pct_nao = (nao_cump / total_p * 100.0) if total_p > 0 else 0

        itens_promessas = promessas_data.get('itens') or []
        promessas_cards = ""
        for pr in itens_promessas:
            tit = html.escape(str(pr.get('titulo', '')))
            cat = html.escape(str(pr.get('categoria', 'Geral')))
            st = html.escape(str(pr.get('status', 'Não informado')))
            det = html.escape(str(pr.get('detalhes', '')))
            fn = html.escape(str(pr.get('fonte', '')))
            b_class = get_badge_class(st)
            promessas_cards += f"""
            <div class="card" style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
                    <span class="badge-subtle">{cat}</span>
                    <span class="badge {b_class}">{st}</span>
                </div>
                <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--text-main); margin-top: 4px;">{tit}</h4>
                <p style="font-size: 0.92rem; color: var(--text-main); flex: 1;">{det}</p>
                <span style="font-size: 0.8rem; color: var(--text-muted);">Fonte: {fn}</span>
            </div>
            """

        governo_promessas_html = f"""
        <section>
            <h2 class="section-title">📋 Balanço de Promessas de Campanha</h2>
            <div class="card" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                    <div>
                        <h3 class="card-title" style="margin-bottom: 4px;">Cumprimento das Diretrizes de Governo</h3>
                        <p style="font-size: 0.88rem; color: var(--text-muted);">Fonte metodológica: {html.escape(str(promessas_data.get('fonte', 'Programa de Governo registrado no TSE')))}</p>
                    </div>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <span class="badge badge-success">✓ Cumpridas: {cump}</span>
                        <span class="badge badge-warning">⚡ Parciais: {parc}</span>
                        <span class="badge badge-danger">✗ Não cumpridas: {nao_cump}</span>
                        <span class="growth-tag">Taxa: {taxa}%</span>
                    </div>
                </div>
                <div style="background: var(--bg-card-alt); border-radius: 999px; height: 16px; width: 100%; display: flex; overflow: hidden; margin: 10px 0;">
                    <div style="width: {pct_cump}%; background: #10b981;" title="Cumpridas ({cump})"></div>
                    <div style="width: {pct_parc}%; background: #f59e0b;" title="Parciais ({parc})"></div>
                    <div style="width: {pct_nao}%; background: #ef4444;" title="Não cumpridas ({nao_cump})"></div>
                </div>
            </div>
            <div class="proposals-grid">
                {promessas_cards}
            </div>
        </section>
        """

    # 4. Reformas Estruturais e Marcos Legais
    reformas_data = data.get('projetos_de_lei_e_reformas') or []
    governo_reformas_html = ""
    if is_governo and reformas_data:
        reformas_cards = ""
        for ref in reformas_data:
            tit = html.escape(str(ref.get('titulo', '')))
            norma = html.escape(str(ref.get('norma', '')))
            ano_ref = html.escape(str(ref.get('ano', '')))
            ementa = html.escape(str(ref.get('ementa', '')))
            impacto = html.escape(str(ref.get('impacto', '')))
            link_ref = ref.get('link', '')
            link_html = f"<a href='{html.escape(link_ref)}' target='_blank' rel='noopener' class='btn-link' style='margin-top: 10px; align-self: flex-start;'>Ver texto oficial da norma ↗</a>" if link_ref else ""

            reformas_cards += f"""
            <div class="card" style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px;">
                    <span class="badge-subtle">{norma}</span>
                    <span class="stat-pill" style="font-size: 0.75rem;">Ano {ano_ref}</span>
                </div>
                <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--text-main); margin-top: 4px;">{tit}</h4>
                <p style="font-size: 0.9rem; color: var(--text-muted);"><strong>Ementa:</strong> {ementa}</p>
                <p style="font-size: 0.92rem; color: var(--text-main); flex: 1;"><strong>Impacto:</strong> {impacto}</p>
                {link_html}
            </div>
            """

        governo_reformas_html = f"""
        <section>
            <h2 class="section-title">📜 Reformas Estruturais e Marcos Legais Promulgados</h2>
            <div class="proposals-grid">
                {reformas_cards}
            </div>
        </section>
        """

    # Bloco Patrimonial reaproveitável
    patrimonio_bloco_html = f"""
        <!-- Evolução Patrimonial -->
        <section>
            <h2 class="section-title">📈 Evolução Patrimonial Declarada à Justiça Eleitoral (TSE)</h2>
            <div class="card" style="padding: 0; overflow-x: auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Ano da Eleição</th>
                            <th>Cargo Disputado</th>
                            <th>Total em Bens Declarados</th>
                            <th>Variação</th>
                            <th>Composição dos Principais Bens</th>
                        </tr>
                    </thead>
                    <tbody>
                        {patrimonio_html}
                    </tbody>
                </table>
            </div>
        </section>
    """

    if is_governo:
        summary_heading_title = "Balanço do Governo: consolidado por IA"
        ipca_val_kpi = f"{resumo_macro.get('ipca_acumulado', 'N/D')}%" if resumo_macro.get('ipca_acumulado') is not None else "N/D"
        selic_val_kpi = f"{resumo_macro.get('selic_final', 'N/D')}% a.a." if resumo_macro.get('selic_final') is not None else "N/D"
        summary_facts_html = f"""
                <div class="summary-fact"><span>Mandato</span><strong>{mandato_periodo}</strong></div>
                <div class="summary-fact"><span>Inflação (IPCA)</span><strong>{ipca_val_kpi}</strong></div>
                <div class="summary-fact"><span>Selic (Final)</span><strong>{selic_val_kpi}</strong></div>
                <div class="summary-fact"><span>Reformas promulgadas</span><strong>{len(reformas_data)} marcos</strong></div>
                <div class="summary-fact"><span>Polêmicas e crises</span><strong>{controversias_total} casos</strong></div>
        """
    else:
        summary_heading_title = "Raio-X do candidato: consolidado por IA"
        summary_facts_html = f"""
                <div class="summary-fact"><span>Status eleitoral</span><strong>{status_eleitoral}</strong></div>
                <div class="summary-fact"><span>Remuneração</span><strong>{salario_base.split('(')[0].strip()}</strong></div>
                <div class="summary-fact"><span>Patrimônio declarado</span><strong>{patrimonio_recente.split('/')[0].strip()}</strong></div>
                <div class="summary-fact"><span>Atuação / propostas</span><strong>{props_total} itens</strong></div>
                <div class="summary-fact"><span>Polêmicas e processos</span><strong>{controversias_total} casos</strong></div>
        """

    revisoes = [r for r in (data.get('revisoes_anteriores') or []) if r]
    revisoes_html = (
        "<p><strong>Revisões anteriores deste relatório:</strong> "
        + html.escape("; ".join(str(r) for r in revisoes[-6:]))
        + ". O conteúdo é reescrito a cada geração; compare com a data de corte antes de citar.</p>"
        if revisoes else ""
    )

    link_votacoes = data.get('link_votacoes')
    votacoes_link_html = (
        f'<a href="{html.escape(str(link_votacoes))}" target="_blank" rel="noopener">🗳️ Histórico de votações</a>'
        if isinstance(link_votacoes, str) and link_votacoes.startswith('http') else ''
    )

    # Links oficiais
    link_perfil = data.get('link_perfil_oficial') or "https://www.camara.leg.br"
    link_gastos = data.get('link_transparencia_gastos') or "https://portaldatransparencia.gov.br"
    link_presenca = data.get('link_presenca') or "#"
    link_tse = data.get('link_tse') or "https://divulgacandcontas.tse.jus.br"

    if is_governo:
        corpo_secoes_html = f"""
        {governo_macro_html}
        {governo_promessas_html}
        {governo_reformas_html}
        {governo_ministerio_html}
        {patrimonio_bloco_html if data.get('evolucao_patrimonial') else ''}
        """
    else:
        corpo_secoes_html = f"""
        <!-- KPI Dashboard -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">{salario_label}</div>
                <div class="kpi-value">{salario_base.split('(')[0].strip()}</div>
                <div class="kpi-subtext">{salario_contexto}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">{assiduidade_label}</div>
                <div class="kpi-value">{assiduidade}</div>
                <div class="kpi-subtext">{assiduidade_contexto}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Patrimônio Declarado (TSE)</div>
                <div class="kpi-value">{patrimonio_recente.split('/')[0].strip()}</div>
                <div class="kpi-subtext">Declaração oficial no DivulgaCandContas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Polêmicas & Processos</div>
                <div class="kpi-value">{controversias_total} Casos</div>
                <div class="kpi-subtext">Fatos com fontes, contraditório e força da evidência</div>
            </div>
        </section>

        <!-- Remuneração e Verbas -->
        <section>
            <h2 class="section-title">{remuneration_section_title}</h2>
            <div class="card">
                <h3 class="card-title">💵 Estrutura Remuneratória e Benefícios Oficiais</h3>
                <p style="margin-bottom: 14px; font-size: 0.92rem;">
                    Remuneração oficial base: <strong>{salario_base}</strong>. {remuneration_description}
                </p>
                <ul class="styled-list">
                    {auxilios_html}
                </ul>
                <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border-color); display: flex; gap: 16px; flex-wrap: wrap;">
                    <a href="{link_gastos}" target="_blank" rel="noopener" class="btn-link">📊 Consultar painel oficial de gastos e notas fiscais da cota ↗</a>
                    <a href="{link_presenca}" target="_blank" rel="noopener" class="btn-link">📋 Consultar diário de presença em plenário ↗</a>
                </div>
            </div>
            {despesas_resumo_html}
            <div class="expenses-grid">{gastos_html}</div>
        </section>

        <!-- Atuação Legislativa -->
        <section>
            <h2 class="section-title">{activity_section_title}</h2>
            <div class="proposals-grid">
                {props_html}
            </div>
        </section>

        {institucional_html}

        {patrimonio_bloco_html}
        """

    template = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dossiê de Transparência Cidadã: {nome_eleitoral} ({partido}-{uf})</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-card: #131c2e;
            --bg-card-alt: #1e293b;
            --bg-card-hover: #26354d;
            --bg-input: #0f172a;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --danger-bg: rgba(239, 68, 68, 0.18);
            --danger-text: #fca5a5;
            --danger-border: #ef4444;
            --warning-bg: rgba(245, 158, 11, 0.18);
            --warning-text: #fde047;
            --warning-border: #f59e0b;
            --success-bg: rgba(34, 197, 94, 0.18);
            --success-text: #86efac;
            --success-border: #22c55e;
            --info-bg: rgba(59, 130, 246, 0.18);
            --info-text: #93c5fd;
            --info-border: #3b82f6;
            --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            --radius: 14px;
        }}

        [data-theme="light"] {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-alt: #f1f5f9;
            --bg-card-hover: #e2e8f0;
            --bg-input: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --accent: #0284c7;
            --accent-hover: #0369a1;
            --accent-glow: rgba(2, 132, 199, 0.12);
            --danger-bg: #fee2e2;
            --danger-text: #991b1b;
            --danger-border: #ef4444;
            --warning-bg: #fef3c7;
            --warning-text: #92400e;
            --warning-border: #f59e0b;
            --success-bg: #dcfce7;
            --success-text: #166534;
            --success-border: #22c55e;
            --info-bg: #dbeafe;
            --info-text: #1e40af;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding-bottom: 80px;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header Bar */
        .top-nav {{
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}

        .top-nav-inner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand {{
            font-size: 1.2rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-main);
            text-decoration: none;
        }}

        .brand-badge {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #0f172a;
            font-size: 0.72rem;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 999px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .nav-actions {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .btn-nav {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .btn-nav:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}

        .btn-theme {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .btn-theme:hover {{
            border-color: var(--accent);
            transform: translateY(-1px);
        }}

        /* Profile Hero */
        .hero-section {{
            margin-top: 30px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 32px;
            box-shadow: var(--shadow);
            display: grid;
            grid-template-columns: 210px 1fr;
            gap: 32px;
            align-items: center;
        }}

        @media (max-width: 768px) {{
            .hero-section {{
                grid-template-columns: 1fr;
                text-align: center;
            }}
            .profile-photo {{
                margin: 0 auto;
            }}
            .hero-tags {{
                justify-content: center;
            }}
            .quick-bio {{
                grid-template-columns: 1fr 1fr;
            }}
        }}

        .profile-photo {{
            width: 210px;
            height: 260px;
            object-fit: cover;
            border-radius: 12px;
            border: 2px solid var(--border-color);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            background-color: var(--bg-card-alt);
        }}

        .profile-info {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .hero-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}

        .tag-party {{
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--accent);
            font-weight: 800;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 6px;
        }}

        .tag-role {{
            background: var(--bg-card-alt);
            color: var(--text-main);
            font-weight: 700;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}

        .profile-name {{
            font-size: 2.3rem;
            font-weight: 900;
            color: var(--text-main);
            line-height: 1.15;
            letter-spacing: -0.5px;
        }}

        .profile-civil-name {{
            font-size: 0.95rem;
            color: var(--text-muted);
        }}

        .quick-bio {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
            margin-top: 10px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}

        .bio-item {{
            font-size: 0.85rem;
        }}
        .bio-label {{
            color: var(--text-muted);
            display: block;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}
        .bio-val {{
            font-weight: 700;
            color: var(--text-main);
        }}

        /* Resumo cidadão */
        .citizen-summary {{
            margin: 24px 0;
            border: 1px solid var(--accent);
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 28px;
            box-shadow: var(--shadow);
        }}

        .summary-heading {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}

        .summary-heading h2 {{
            font-size: 1.45rem;
            line-height: 1.25;
        }}

        .ai-label {{
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--accent);
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.45px;
        }}

        .summary-copy p {{
            margin-bottom: 12px;
            font-size: 0.96rem;
        }}

        .summary-facts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 18px 0;
        }}

        .summary-fact {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            border-radius: 9px;
            padding: 12px;
        }}

        .summary-fact span {{
            display: block;
            color: var(--text-muted);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.45px;
            text-transform: uppercase;
        }}

        .summary-fact strong {{ font-size: 0.9rem; }}

        .summary-cases {{
            margin-top: 20px;
            border-top: 1px solid var(--border-color);
            padding-top: 18px;
        }}

        .summary-cases h3 {{
            color: var(--accent);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.45px;
            margin-bottom: 10px;
        }}

        .summary-case {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            border-radius: 9px;
            margin-bottom: 9px;
            padding: 12px 14px;
        }}

        .summary-case summary {{
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            gap: 12px;
            font-weight: 800;
        }}

        .summary-case-status {{
            color: var(--text-muted);
            font-size: 0.74rem;
            font-weight: 700;
            text-align: right;
        }}

        .summary-case p {{ margin: 10px 0 6px; font-size: 0.86rem; }}
        .summary-case ul {{ margin-left: 20px; color: var(--text-muted); font-size: 0.82rem; }}
        .summary-case-defense {{ color: var(--text-muted); }}
        .summary-case-empty {{ color: var(--text-muted); font-size: 0.88rem; }}

        .summary-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 18px;
            margin-top: 20px;
        }}

        .summary-panel {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 18px;
        }}

        .summary-panel h3 {{
            color: var(--accent);
            font-size: 0.86rem;
            text-transform: uppercase;
            letter-spacing: 0.45px;
            margin-bottom: 10px;
        }}

        .summary-panel ul {{
            padding-left: 20px;
        }}

        .summary-panel li {{
            margin-bottom: 8px;
            font-size: 0.88rem;
        }}

        .ai-notice {{
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.8rem;
        }}

        @media (max-width: 768px) {{
            .summary-grid {{ grid-template-columns: 1fr; }}
        }}

        /* KPI Dashboard Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 22px;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent-hover));
        }}

        .kpi-title {{
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted);
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.2;
        }}

        .kpi-subtext {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 6px;
        }}

        /* Sections */
        .section-title {{
            font-size: 1.35rem;
            font-weight: 800;
            margin: 40px 0 16px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-main);
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
            margin-bottom: 24px;
        }}

        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Lists */
        ul.styled-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        ul.styled-list li {{
            font-size: 0.92rem;
            color: var(--text-main);
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}

        .bullet {{
            color: var(--accent);
            font-weight: 900;
            font-size: 1.2rem;
            line-height: 1;
        }}

        .social-pill {{
            display: inline-block;
            background: var(--bg-card-alt);
            color: var(--text-main);
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 6px;
            margin: 4px 4px 4px 0;
            border: 1px solid var(--border-color);
            transition: all 0.15s ease;
        }}

        .social-pill:hover {{
            border-color: var(--accent);
            color: var(--accent);
            background: var(--bg-card-hover);
        }}

        /* Proposals Grid */
        .proposals-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 16px;
        }}

        .proposal-card {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 14px;
            transition: all 0.2s ease;
        }}

        .proposal-card:hover {{
            border-color: var(--accent);
            background: var(--bg-card-hover);
        }}

        .proposal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .proposal-type {{
            background: var(--accent-glow);
            color: var(--accent);
            font-weight: 800;
            font-size: 0.82rem;
            padding: 3px 10px;
            border-radius: 6px;
        }}

        .proposal-status-badge {{
            background: var(--bg-card);
            color: var(--text-muted);
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}

        .proposal-date {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .proposal-ementa {{
            font-size: 0.9rem;
            color: var(--text-main);
            line-height: 1.5;
        }}

        .btn-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 0.82rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .btn-link:hover {{
            text-decoration: underline;
        }}

        /* Filter Controls */
        .filter-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }}

        .filter-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent);
            color: #0f172a;
            border-color: var(--accent);
        }}

        /* Timeline for News & Scandals */
        .timeline {{
            position: relative;
            padding-left: 28px;
            margin-top: 16px;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            top: 0;
            bottom: 0;
            left: 10px;
            width: 2px;
            background: var(--border-color);
        }}

        .timeline-item {{
            position: relative;
            margin-bottom: 28px;
            transition: all 0.2s ease;
        }}

        .timeline-marker {{
            position: absolute;
            top: 24px;
            left: -28px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--accent);
            border: 2px solid var(--bg-body);
        }}

        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }}

        .timeline-tags {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .category-tag {{
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-size: 0.74rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}

        .timeline-date {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 600;
        }}

        .timeline-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 10px;
            line-height: 1.3;
        }}

        .timeline-text {{
            font-size: 0.92rem;
            color: var(--text-main);
            margin-bottom: 14px;
            line-height: 1.55;
        }}

        .evidence-badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            border: 1px solid;
            padding: 4px 9px;
            font-size: 0.72rem;
            font-weight: 800;
        }}

        .evidence-confirmed {{ color: #86efac; border-color: #22c55e; background: rgba(34, 197, 94, 0.14); }}
        .evidence-supported {{ color: #93c5fd; border-color: #3b82f6; background: rgba(59, 130, 246, 0.14); }}
        .evidence-pending {{ color: #fde047; border-color: #f59e0b; background: rgba(245, 158, 11, 0.14); }}
        .evidence-unproven {{ color: #cbd5e1; border-color: #64748b; background: rgba(100, 116, 139, 0.14); }}
        .evidence-false {{ color: #fca5a5; border-color: #ef4444; background: rgba(239, 68, 68, 0.14); }}

        .evidence-box {{
            margin-top: 14px;
            padding: 14px 16px;
            border: 1px solid var(--info-border);
            border-radius: 10px;
            background: var(--info-bg);
            color: var(--text-main);
        }}

        .evidence-box p {{ margin: 7px 0; }}
        .evidence-box ul {{ margin-left: 20px; color: var(--text-muted); }}

        .coverage-audit {{
            margin: 12px 0 18px;
            padding: 16px 18px;
            color: var(--text-muted);
        }}

        .coverage-audit summary {{
            color: var(--text-main);
            cursor: pointer;
            font-weight: 800;
        }}

        .coverage-audit p {{ margin: 10px 0 6px; }}
        .coverage-audit ul {{ margin-left: 20px; }}

        .defense-box {{
            background: var(--bg-card-alt);
            border-left: 4px solid var(--accent);
            padding: 14px;
            border-radius: 0 8px 8px 0;
            font-size: 0.88rem;
            margin-bottom: 14px;
            line-height: 1.5;
        }}

        .defense-box strong {{
            display: block;
            margin-bottom: 6px;
            color: var(--accent);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .sources-box {{
            font-size: 0.82rem;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border-color);
        }}

        .sources-label {{
            color: var(--text-muted);
            font-weight: 700;
        }}

        .source-tag {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 700;
            transition: color 0.15s ease;
        }}
        .source-tag:hover {{
            text-decoration: underline;
        }}
        /* Despesas discriminadas */
        .expenses-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 14px;
            margin-top: 16px;
        }}
        .expense-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 16px;
        }}
        .expense-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 10px;
            margin-bottom: 6px;
        }}
        .expense-category {{
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: var(--text-muted);
        }}
        .expense-value {{
            font-size: 1rem;
            font-weight: 800;
            color: var(--accent);
            white-space: nowrap;
        }}
        .expense-detail {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .proportion-warning {{
            margin-top: 14px;
            padding: 12px 14px;
            border-left: 4px solid var(--warning-border);
            background: var(--warning-bg);
            color: var(--warning-text);
            border-radius: 6px;
            font-size: 0.9rem;
        }}
        .source-nolink {{
            color: var(--text-muted);
            font-weight: 600;
        }}
        .source-dead {{
            color: var(--text-muted);
            text-decoration: line-through;
        }}

        /* Badges */
        .badge {{
            font-size: 0.74rem;
            font-weight: 800;
            padding: 3px 9px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .badge-danger {{
            background: var(--danger-bg);
            color: var(--danger-text);
            border: 1px solid var(--danger-border);
        }}
        .badge-warning {{
            background: var(--warning-bg);
            color: var(--warning-text);
            border: 1px solid var(--warning-border);
        }}
        .badge-success {{
            background: var(--success-bg);
            color: var(--success-text);
            border: 1px solid var(--success-border);
        }}
        .badge-info {{
            background: var(--info-bg);
            color: var(--info-text);
            border: 1px solid var(--info-border);
        }}

        .badge-subtle {{
            background: var(--bg-card-alt);
            color: var(--text-main);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .growth-tag {{
            background: var(--accent-glow);
            color: var(--accent);
            font-weight: 800;
            font-size: 0.8rem;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        /* Table */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}

        .data-table th {{
            text-align: left;
            padding: 14px;
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-weight: 800;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }}

        .data-table td {{
            padding: 14px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
            vertical-align: middle;
        }}

        .td-value {{
            font-weight: 800;
            color: var(--accent);
            white-space: nowrap;
        }}

        .td-details {{
            font-size: 0.84rem;
            color: var(--text-muted);
        }}

        .text-center {{
            text-align: center;
        }}

        /* Footer & Audit Trail */
        .footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        .audit-links {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 16px;
        }}

        .audit-links a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 700;
        }}

        .audit-links a:hover {{
            text-decoration: underline;
        }}

        @media print {{
            .top-nav, .btn-theme, .audit-links, .filter-bar {{ display: none !important; }}
            body {{ background: #fff !important; color: #000 !important; }}
            .card, .hero-section, .kpi-card {{ border: 1px solid #ccc !important; box-shadow: none !important; }}
        }}
    </style>
</head>
<body>

    <header class="top-nav">
        <div class="container top-nav-inner">
            <a href="index.html" class="brand">
                <span>🏛️ Dossiê Político</span>
                <span class="brand-badge">Auditoria Cidadã</span>
            </a>
            <div class="nav-actions">
                <a href="index.html" class="btn-nav">📋 Ver Índice Geral</a>
                <button class="btn-theme" onclick="toggleTheme()" id="themeBtn">🌓 Alternar Tema</button>
            </div>
        </div>
    </header>

    <main class="container">

        <!-- Perfil Hero -->
        <section class="hero-section">
            <img src="{html.escape(foto_url)}" alt="Foto de {nome_eleitoral}" class="profile-photo" onerror="{image_error_handler()}">
            <div class="profile-info">
                <div class="hero-tags">
                    <span class="tag-party">{partido}</span>
                    <span class="tag-role">{cargo} • {uf}</span>
                    <span class="badge badge-info">{situacao}</span>
                </div>
                <h1 class="profile-name">{nome_eleitoral}</h1>
                <p class="profile-civil-name">Nome Civil: <strong>{nome_civil}</strong></p>

                <div class="quick-bio">
                    <div class="bio-item">
                        <span class="bio-label">Mandato / Legislatura</span>
                        <span class="bio-val">{mandato_periodo}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">Naturalidade</span>
                        <span class="bio-val">{municipio_nascimento}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">Escolaridade</span>
                        <span class="bio-val">{escolaridade}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">Gabinete / Contato</span>
                        <span class="bio-val">{telefone_gabinete}</span>
                    </div>
                    {bio_extra_html}
                </div>

                <div style="margin-top: 10px;">
                    <span class="bio-label" style="margin-bottom: 6px;">Redes Sociais Oficiais:</span>
                    {redes_html}
                </div>
            </div>
        </section>

        <!-- Resumo cidadão gerado por IA -->
        <section class="citizen-summary" aria-labelledby="resumo-cidadao-title">
            <div class="summary-heading">
                <div>
                    <span class="bio-label">Raio-X consolidado • data de corte: {data_corte}</span>
                    <h2 id="resumo-cidadao-title">{summary_heading_title}</h2>
                </div>
                <span class="ai-label">Síntese por IA</span>
            </div>
            <div class="summary-copy">
                {citizen_summary['summary_html']}
            </div>
            <div class="summary-facts">
                {summary_facts_html}
            </div>
            <div class="summary-cases">
                <h3>Escândalos, polêmicas e processos — todos os casos catalogados</h3>
                {summary_cases_html}
            </div>
            <div class="summary-grid">
                <div class="summary-panel">
                    <h3>Pontos-chave</h3>
                    <ul>{citizen_summary['points_html']}</ul>
                </div>
                <div class="summary-panel">
                    {proporcao_aviso_html}
                <h3>Lacunas e limites</h3>
                    <ul>{citizen_summary['gaps_html']}</ul>
                </div>
            </div>
            <p class="ai-notice"><strong>Status eleitoral:</strong> {status_eleitoral}<br>{citizen_summary['notice']}</p>
        </section>

        {corpo_secoes_html}

        <!-- Notícias, Investigações e Escândalos -->
        <section>
            <h2 class="section-title">{controversies_section_title}</h2>
            <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 16px;">
                Levantamento cronológico de fatos de interesse público, com estágio atual, contraditório e força da evidência. “Escândalo” ou “polêmica” descreve a repercussão pública e não presume culpa.
            </p>
            <div class="evidence-legend card">
                <strong>Como ler o grau de veracidade:</strong>
                <p><b>Confirmado por documento/decisão</b> comprova o evento descrito, não necessariamente a acusação de mérito. <b>Fortemente sustentado</b> reúne fontes independentes convergentes. <b>Alegação oficial em apuração</b> confirma que existe investigação ou acusação, mas não culpa. <b>Contestado / não comprovado</b> não possui base suficiente. <b>Falso ou enganoso</b> exige checagem documental explícita.</p>
            </div>
            {coverage_html}
            
            <div class="filter-bar">
                {filter_buttons_html}
            </div>

            <div class="timeline" id="controversiesTimeline">
                {controversias_html}
            </div>
        </section>

        {transparencia_html}

        <!-- Fontes e Trilha de Auditoria -->
        <footer class="footer">
            {revisoes_html}
            <p><strong>Dossiê gerado em:</strong> {data_geracao} | Metodologia: Auditoria em APIs de Dados Abertos, Diários Oficiais e Veículos Jornalísticos Auditáveis.</p>
            <div class="audit-links">
                <a href="index.html">📋 Índice Geral</a>
                <a href="{link_perfil}" target="_blank" rel="noopener">🏛️ Portal Oficial do Mandato</a>
                <a href="{link_gastos}" target="_blank" rel="noopener">💸 Portal da Transparência de Gastos</a>
                <a href="{link_tse}" target="_blank" rel="noopener">🗳️ TSE DivulgaCandContas</a>
                {votacoes_link_html}
                <a href="https://portaldatransparencia.gov.br" target="_blank" rel="noopener">🔎 Portal da Transparência CGU</a>
            </div>
        </footer>

    </main>

    <script>
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('dossie_theme', next);
        }}

        (function initTheme() {{
            const saved = localStorage.getItem('dossie_theme');
            if (saved) {{
                document.documentElement.setAttribute('data-theme', saved);
            }}
        }})();

        function filterControversies(categorySlug, btn) {{
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const items = document.querySelectorAll('.timeline-item');
            items.forEach(item => {{
                if (categorySlug === 'all' || item.getAttribute('data-category') === categorySlug) {{
                    item.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    return template

def generate_index_html(entries: List[Dict[str, Any]]) -> str:
    data_atualizacao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    total_politicos = len(entries)
    total_propostas = sum(e.get('proposicoes_total', 0) for e in entries)
    total_controversias = sum(e.get('controversias_total', 0) for e in entries)
    
    cards_html = ""
    for e in entries:
        nome_eleitoral = html.escape(e.get('nome_eleitoral', 'Político'))
        nome_civil = html.escape(e.get('nome_civil', ''))
        cargo = html.escape(e.get('cargo', 'Agente Público'))
        partido = html.escape(e.get('partido', 'S/ Partido'))
        uf = html.escape(e.get('uf', 'BR'))
        foto_url = safe_image_url(e.get('foto_url'))
        salario = html.escape(str(e.get('salario_base') or 'Não informado').split('(')[0].strip())
        patrimonio = html.escape(str(e.get('patrimonio_recente', 'Consultar TSE')).split('/')[0].strip())
        filename = html.escape(e.get('filename', '#'))
        props_c = e.get('proposicoes_total', 0)
        contr_c = e.get('controversias_total', 0)
        itens_label = html.escape(str(e.get('itens_label') or 'Propostas'))
        data_analise = html.escape(e.get('data_atualizacao', 'Recente'))
        resumo_curto = html.escape(str(e.get('resumo_curto') or 'Abra o relatório para consultar o panorama cidadão.'))
        tipo_dossie = e.get('tipo_dossie', 'perfil_politico')
        periodo_mandato = html.escape(str(e.get('periodo_mandato') or ''))
        tipo_tag = ""
        if tipo_dossie == 'governo_presidencial':
            tag_label = f"Governo {periodo_mandato}".strip() if periodo_mandato else "Governo Presidencial"
            tipo_tag = f"<span class='tag-party' style='background: linear-gradient(135deg, #0284c7, #38bdf8); color: #0f172a;'>{tag_label}</span>"
        
        cards_html += f"""
        <div class="politician-card" data-search="{nome_eleitoral.lower()} {nome_civil.lower()} {partido.lower()} {uf.lower()} {cargo.lower()} {tipo_dossie.lower()} {periodo_mandato.lower()}">
            <div class="card-hero">
                <img src="{html.escape(foto_url)}" alt="{nome_eleitoral}" class="card-avatar" onerror="{image_error_handler()}">
                <div class="card-header-info">
                    <div class="card-tags">
                        {tipo_tag}
                        <span class="tag-party">{partido}</span>
                        <span class="tag-uf">{uf}</span>
                    </div>
                    <h2 class="card-name">{nome_eleitoral}</h2>
                    <p class="card-role">{cargo}</p>
                </div>
            </div>
            <div class="card-body">
                <p class="card-summary">{resumo_curto}</p>
                <div class="card-metric-row">
                    <div class="card-metric">
                        <span class="metric-label">Salário Base</span>
                        <span class="metric-val">{salario}</span>
                    </div>
                    <div class="card-metric">
                        <span class="metric-label">Patrimônio</span>
                        <span class="metric-val">{patrimonio}</span>
                    </div>
                </div>
                <div class="card-stats-row">
                    <span class="stat-pill">📜 {props_c} {itens_label}</span>
                    <span class="stat-pill">⚖️ {contr_c} Polêmicas/Casos</span>
                </div>
            </div>
            <div class="card-footer">
                <span class="audit-date">Atualizado: {data_analise}</span>
                <a href="{filename}" class="btn-dossie">Acessar Dossiê ➔</a>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Índice Geral — Dossiê Político & Auditoria Cidadã</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-card: #131c2e;
            --bg-card-alt: #1e293b;
            --bg-card-hover: #26354d;
            --bg-input: #0f172a;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            --radius: 14px;
        }}

        [data-theme="light"] {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-alt: #f1f5f9;
            --bg-card-hover: #e2e8f0;
            --bg-input: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --accent: #0284c7;
            --accent-hover: #0369a1;
            --accent-glow: rgba(2, 132, 199, 0.12);
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding-bottom: 80px;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header Bar */
        .top-nav {{
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 18px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}

        .top-nav-inner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand {{
            font-size: 1.25rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-main);
            text-decoration: none;
        }}

        .brand-badge {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #0f172a;
            font-size: 0.72rem;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 999px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .btn-theme {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .btn-theme:hover {{
            border-color: var(--accent);
            transform: translateY(-1px);
        }}

        /* Hero Banner */
        .index-hero {{
            margin-top: 32px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 36px;
            box-shadow: var(--shadow);
            text-align: center;
        }}

        .index-title {{
            font-size: 2.2rem;
            font-weight: 900;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}

        .index-subtitle {{
            color: var(--text-muted);
            font-size: 1rem;
            max-width: 680px;
            margin: 0 auto 24px auto;
        }}

        /* Search Bar */
        .search-box {{
            max-width: 540px;
            margin: 0 auto;
            position: relative;
        }}

        .search-input {{
            width: 100%;
            padding: 14px 20px 14px 44px;
            border-radius: 10px;
            background: var(--bg-input);
            border: 2px solid var(--border-color);
            color: var(--text-main);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 4px var(--accent-glow);
        }}

        .search-icon {{
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.1rem;
            color: var(--text-muted);
        }}

        /* Aggregate Stats Bar */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin: 32px 0;
        }}

        .stat-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 20px;
            text-align: center;
            box-shadow: var(--shadow);
        }}

        .stat-num {{
            font-size: 1.8rem;
            font-weight: 900;
            color: var(--accent);
            line-height: 1.1;
        }}

        .stat-desc {{
            font-size: 0.78rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }}

        /* Cards Grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 22px;
            margin-top: 24px;
        }}

        .politician-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .politician-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent);
        }}

        .card-hero {{
            padding: 22px;
            display: flex;
            gap: 18px;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
        }}

        .card-avatar {{
            width: 72px;
            height: 90px;
            border-radius: 8px;
            object-fit: cover;
            border: 2px solid var(--border-color);
            background: var(--bg-card-alt);
        }}

        .card-header-info {{
            flex: 1;
        }}

        .card-tags {{
            display: flex;
            gap: 6px;
            margin-bottom: 6px;
        }}

        .tag-party {{
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--accent);
            font-weight: 800;
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .tag-uf {{
            background: var(--bg-card-alt);
            color: var(--text-main);
            font-weight: 700;
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}

        .card-name {{
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.2;
        }}

        .card-role {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .card-body {{
            padding: 18px 22px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .card-summary {{
            color: var(--text-muted);
            font-size: 0.82rem;
            line-height: 1.45;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        .card-metric-row {{
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }}

        .card-metric {{
            display: flex;
            flex-direction: column;
        }}

        .metric-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 700;
            letter-spacing: 0.4px;
        }}

        .metric-val {{
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--text-main);
        }}

        .card-stats-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .stat-pill {{
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}

        .card-footer {{
            padding: 14px 22px;
            background: var(--bg-card-alt);
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .audit-date {{
            font-size: 0.72rem;
            color: var(--text-muted);
        }}

        .btn-dossie {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #0f172a;
            font-size: 0.8rem;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 6px;
            text-decoration: none;
            transition: all 0.2s ease;
        }}

        .btn-dossie:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px var(--accent-glow);
        }}

        .footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>

    <header class="top-nav">
        <div class="container top-nav-inner">
            <a href="index.html" class="brand">
                <span>🏛️ Dossiê Político</span>
                <span class="brand-badge">Índice Geral</span>
            </a>
            <div class="nav-actions">
                <button class="btn-theme" onclick="toggleTheme()" id="themeBtn">🌓 Alternar Tema</button>
            </div>
        </div>
    </header>

    <main class="container">

        <section class="index-hero">
            <h1 class="index-title">Painel de Auditoria & Transparência Cidadã</h1>
            <p class="index-subtitle">Consolidado de figuras públicas brasileiras com dados de remuneração, assiduidade, evolução patrimonial no TSE e histórico de investigações.</p>
            
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-input" placeholder="Buscar por nome, partido, cargo ou estado..." onkeyup="filterCards()">
            </div>
        </section>

        <!-- Stats Bar -->
        <section class="stats-grid">
            <div class="stat-box">
                <div class="stat-num">{total_politicos}</div>
                <div class="stat-desc">Políticos Auditados</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{total_propostas}</div>
                <div class="stat-desc">Itens Públicos Catalogados</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{total_controversias}</div>
                <div class="stat-desc">Investigações & Notícias Catalogadas</div>
            </div>
        </section>

        <!-- Cards List -->
        <section>
            <div class="cards-grid" id="cardsGrid">
                {cards_html}
            </div>
        </section>

        <footer class="footer">
            <p><strong>Índice atualizado em:</strong> {data_atualizacao} | Diretório: <code>~/.dossie-politico/</code></p>
        </footer>

    </main>

    <script>
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('dossie_theme', next);
        }}

        (function initTheme() {{
            const saved = localStorage.getItem('dossie_theme');
            if (saved) {{
                document.documentElement.setAttribute('data-theme', saved);
            }}
        }})();

        function filterCards() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.politician-card');
            cards.forEach(card => {{
                const searchData = card.getAttribute('data-search') || '';
                if (searchData.includes(query)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

def update_index_catalog(output_dir: str, data: Dict[str, Any], filename: str):
    index_json_path = os.path.join(output_dir, "index.json")
    index_html_path = os.path.join(output_dir, "index.html")
    
    entries = []
    if os.path.exists(index_json_path):
        try:
            with open(index_json_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        except Exception:
            entries = []

    nome_eleitoral = data.get('nome_eleitoral') or data.get('nome') or 'Politico'
    card_id = sanitize_filename(nome_eleitoral)
    
    patrimonio = 'Consultar TSE'
    if data.get('evolucao_patrimonial'):
        patrimonio = str(data['evolucao_patrimonial'][0].get('valor_formatado') or 'Consultar TSE')

    tipo_dossie = data.get('tipo_dossie') or ('governo_presidencial' if data.get('mandato_executivo') else 'perfil_politico')
    mandato_exec = data.get('mandato_executivo') or {}
    periodo_mandato = str(data.get('mandato_periodo') or mandato_exec.get('periodo') or '')
    indicadores = data.get('indicadores_economicos') or {}
    resumo_indicadores = indicadores.get('resumo_macro')

    reformas = data.get('projetos_de_lei_e_reformas', [])
    props = data.get('proposicoes_principais', [])
    if tipo_dossie == 'governo_presidencial' and reformas and not props:
        proposicoes_total = len(reformas)
        itens_label = data.get('itens_label', 'Reformas / Atos')
    else:
        proposicoes_total = len(props)
        itens_label = data.get('itens_label', 'Propostas')
        
    entry_dict = {
        'id': card_id,
        'nome_eleitoral': nome_eleitoral,
        'nome_civil': data.get('nome_civil', nome_eleitoral),
        'cargo': data.get('cargo', 'Presidente da República' if tipo_dossie == 'governo_presidencial' else 'Agente Público'),
        'partido': data.get('partido', 'S/ Partido'),
        'uf': data.get('uf', 'BR'),
        'foto_url': data.get('foto_url', ''),
        'salario_base': data.get('salario_oficial_base', 'Não informado'),
        'patrimonio_recente': patrimonio,
        'proposicoes_total': proposicoes_total,
        'controversias_total': len(data.get('controversias_e_noticias', [])),
        'itens_label': itens_label,
        'resumo_curto': build_citizen_summary(data)['excerpt'],
        'filename': filename,
        'revisoes': [d for d in (data.get('revisoes_anteriores') or []) if d],
        'data_atualizacao': datetime.datetime.now().strftime("%d/%m/%Y às %H:%M"),
        'tipo_dossie': tipo_dossie,
        'periodo_mandato': periodo_mandato,
        'resumo_indicadores': resumo_indicadores,
    }

    # Atualiza ou insere
    existing_idx = next((i for i, item in enumerate(entries) if item.get('id') == card_id or item.get('filename') == filename), None)
    if existing_idx is not None:
        entries[existing_idx] = entry_dict
    else:
        entries.insert(0, entry_dict)

    # Grava index.json
    with open(index_json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    # Renderiza e grava index.html
    index_html_content = generate_index_html(entries)
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(index_html_content)


def remove_dossier_entry(output_dir: str, filename: str, delete_html: bool = False) -> bool:
    """Remove uma entrada exata do catálogo e, opcionalmente, seu HTML individual."""
    if os.path.basename(filename) != filename:
        raise ValueError("O nome do arquivo não pode conter diretórios.")

    index_json_path = os.path.join(output_dir, "index.json")
    index_html_path = os.path.join(output_dir, "index.html")
    entries: List[Dict[str, Any]] = []
    if os.path.exists(index_json_path):
        with open(index_json_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            if isinstance(loaded, list):
                entries = loaded

    filtered = [entry for entry in entries if entry.get('filename') != filename]
    removed = len(filtered) != len(entries)
    if not removed:
        return False

    with open(index_json_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(generate_index_html(filtered))

    if delete_html:
        dossier_path = Path(output_dir, filename)
        if dossier_path.is_file():
            dossier_path.unlink()
        dossier_json_path = Path(output_dir, f"{Path(filename).stem}.json")
        if dossier_json_path.is_file():
            dossier_json_path.unlink()
    return True

def validate_coverage_record(data: Dict[str, Any]) -> None:
    """Impede que um dossiê seja entregue sem auditoria mínima de cobertura."""
    coverage = data.get('cobertura_pesquisa')
    if not isinstance(coverage, dict):
        raise ValueError(
            "Dossiê incompleto: informe 'cobertura_pesquisa' após executar a auditoria "
            "mínima descrita em references/sources-guide.md."
        )

    missing_scalars = [
        key for key in ('data_execucao', 'periodo')
        if not str(coverage.get(key) or '').strip()
    ]
    missing_lists = [
        key for key in ('nomes_consultados', 'eixos_verificados', 'fontes_consultadas')
        if not isinstance(coverage.get(key), list) or not coverage.get(key)
    ]
    if 'limitacoes' not in coverage or not isinstance(coverage.get('limitacoes'), list):
        missing_lists.append('limitacoes')

    missing = missing_scalars + missing_lists
    if missing:
        raise ValueError(
            "Dossiê incompleto: o registro 'cobertura_pesquisa' precisa preencher: "
            + ", ".join(missing)
            + "."
        )


def read_previous_revisions(output_dir: str, filename: str) -> List[str]:
    """Datas das gerações anteriores deste mesmo relatório, para o leitor saber que houve revisão."""
    index_json_path = os.path.join(output_dir, "index.json")
    if not os.path.exists(index_json_path):
        return []
    try:
        with open(index_json_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except Exception:
        return []
    for entry in entries if isinstance(entries, list) else []:
        if entry.get('filename') == filename:
            anteriores = [d for d in (entry.get('revisoes') or []) if d]
            atual = entry.get('data_atualizacao')
            return (anteriores + [atual]) if atual else anteriores
    return []


def build_dossier_file(data: Dict[str, Any], output_dir: Optional[str] = None,
                       check_links: bool = True) -> str:
    validate_coverage_record(data)
    if check_links:
        tally = verify_sources(data)
        if tally:
            resumo = ", ".join(f"{qtd} {nome}" for nome, qtd in sorted(tally.items()))
            print(f"[*] Verificação das fontes citadas: {resumo}.")
            mortos = tally.get('quebrado', 0) + tally.get('indisponivel', 0)
            if mortos:
                print(f"[!] {mortos} fonte(s) não resolveram e aparecem marcadas no relatório. "
                      "Substitua por URLs conferidas antes de tratar o dossiê como auditável.",
                      file=sys.stderr)
    if output_dir is None:
        home = str(Path.home())
        output_dir = os.path.join(home, ".dossie-politico")
    
    os.makedirs(output_dir, exist_ok=True)
    
    nome_politico = data.get('nome_eleitoral') or data.get('nome') or 'Politico'
    filename = f"{sanitize_filename(nome_politico)}.html"
    filepath = os.path.join(output_dir, filename)
    json_filename = f"{sanitize_filename(nome_politico)}.json"
    json_filepath = os.path.join(output_dir, json_filename)
    
    if not data.get('links_transparencia'):
        sys.path.insert(0, str(Path(__file__).parent.resolve()))
        from fetch_tse_transparency import build_transparency_links
        data['links_transparencia'] = build_transparency_links(nome_politico)
    data.setdefault('revisoes_anteriores', read_previous_revisions(output_dir, filename))
    html_content = generate_dossier_html(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    # Atualiza catálogo e index.html
    update_index_catalog(output_dir, data, filename)
    
    return filepath

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gera o dossiê HTML, atualiza o catálogo e abre o índice geral.")
    parser.add_argument('json_path', nargs='?', help="Payload JSON completo do dossiê")
    parser.add_argument('--remove', metavar='ARQUIVO.html',
                        help="Retira uma pessoa do catálogo (retificação / direito de resposta)")
    parser.add_argument('--apagar-html', action='store_true',
                        help="Com --remove, apaga também o relatório individual")
    parser.add_argument('output_dir', nargs='?', default=None, help="Diretório de saída (padrão: ~/.dossie-politico)")
    parser.add_argument('--output-dir', dest='output_dir_flag', default=None, help="Mesma coisa, na forma de opção")
    parser.add_argument('--no-open-index', action='store_true', help="Não abre o índice (somente testes/ambientes sem interface)")
    parser.add_argument('--no-check-links', action='store_true', help="Não verifica se as URLs das fontes citadas resolvem")
    args = parser.parse_args()
    json_path = args.json_path
    out_dir = args.output_dir_flag or args.output_dir or os.path.join(str(Path.home()), ".dossie-politico")

    if args.remove:
        if remove_dossier_entry(out_dir, args.remove, delete_html=args.apagar_html):
            print(f"Entrada removida do catálogo: {args.remove}")
        else:
            print(f"Nada a remover: '{args.remove}' não está no catálogo.", file=sys.stderr)
            raise SystemExit(1)
        raise SystemExit(0)

    if not json_path:
        parser.error("informe o payload JSON ou use --remove ARQUIVO.html")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        dossier_data = json.load(f)
        
    generated_path = build_dossier_file(dossier_data, out_dir, check_links=not args.no_check_links)
    index_path = os.path.join(os.path.dirname(generated_path), 'index.html')
    print(f"Dossiê HTML gerado com sucesso em:\n{generated_path}")
    print(f"Índice atualizado em:\n{index_path}")
    if not args.no_open_index:
        if open_index_file(index_path):
            print("Índice aberto no navegador padrão.")
