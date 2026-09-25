#!/usr/bin/env python3
"""
fetch_governo.py - Coleta e estruturação de indicadores macroeconômicos do BCB SGS.
Fonte oficial: Banco Central do Brasil - Sistema Gerenciador de Séries Temporais (SGS)
API: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json
"""

import sys
import json
import time
import argparse
import unicodedata
import urllib.error
import urllib.request
from typing import Dict, Any, Optional, List

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PoliticoDossie/1.0; +https://github.com/dossie-politico)",
    "Accept": "application/json",
}

# Códigos oficiais das séries no SGS do Banco Central
BCB_SERIES = {
    "ipca_mensal": 433,            # Variação mensal do IPCA (%)
    "selic_meta": 432,              # Meta Selic fixada pelo Copom (% a.a.)
    "selic_diaria": 1178,           # Selic diária anualizada base 252 (% a.a.)
    "dolar_ptax": 1,                # Dólar comercial PTAX venda diário (R$)
    "divida_bruta_pib": 13762,      # Dívida Bruta do Governo Geral (% PIB)
    "divida_liquida_pib": 4505,     # Dívida Líquida do Setor Público (% PIB)
    "pib_crescimento_real": 7326,   # PIB - variação real anual (%)
}

PRESETS_GOVERNO: Dict[str, Dict[str, Any]] = {
    "fhc": {
        "id": "fhc",
        "presidente": "Fernando Henrique Cardoso",
        "partido": "PSDB",
        "vice": "Marco Maciel",
        "periodo": "1995–2002",
        "ano_inicio": 1995,
        "ano_fim": 2002,
        "data_inicio": "01/01/1995",
        "data_fim": "31/12/2002",
        "mandatos": "1º e 2º mandatos",
        "ministros_notaveis": [
            {"pasta": "Fazenda", "nome": "Pedro Malan"},
            {"pasta": "Planejamento", "nome": "José Serra / Martus Tavares"},
            {"pasta": "Banco Central", "nome": "Gustavo Franco / Armínio Fraga"},
        ],
    },
    "lula": {
        "id": "lula",
        "presidente": "Luiz Inácio Lula da Silva",
        "partido": "PT",
        "vice": "José Alencar",
        "periodo": "2003–2010",
        "ano_inicio": 2003,
        "ano_fim": 2010,
        "data_inicio": "01/01/2003",
        "data_fim": "31/12/2010",
        "mandatos": "1º e 2º mandatos",
        "ministros_notaveis": [
            {"pasta": "Fazenda", "nome": "Antônio Palocci / Guido Mantega"},
            {"pasta": "Planejamento", "nome": "Guido Mantega / Paulo Bernardo"},
            {"pasta": "Banco Central", "nome": "Henrique Meirelles"},
        ],
    },
    "dilma": {
        "id": "dilma",
        "presidente": "Dilma Rousseff",
        "partido": "PT",
        "vice": "Michel Temer",
        "periodo": "2011–2016",
        "ano_inicio": 2011,
        "ano_fim": 2016,
        "data_inicio": "01/01/2011",
        "data_fim": "31/08/2016",
        "mandatos": "1º mandato e 2º até impeachment",
        "ministros_notaveis": [
            {"pasta": "Fazenda", "nome": "Guido Mantega / Joaquim Levy / Nelson Barbosa"},
            {"pasta": "Planejamento", "nome": "Miriam Belchior / Valdir Simão"},
            {"pasta": "Banco Central", "nome": "Alexandre Tombini"},
        ],
    },
    "temer": {
        "id": "temer",
        "presidente": "Michel Temer",
        "partido": "MDB",
        "vice": "Vacante",
        "periodo": "2016–2018",
        "ano_inicio": 2016,
        "ano_fim": 2018,
        "data_inicio": "31/08/2016",
        "data_fim": "31/12/2018",
        "mandatos": "Mandato pós-impeachment",
        "ministros_notaveis": [
            {"pasta": "Fazenda", "nome": "Henrique Meirelles / Eduardo Guardia"},
            {"pasta": "Planejamento", "nome": "Romero Jucá / Dyogo Oliveira / Esteves Colnago"},
            {"pasta": "Banco Central", "nome": "Ilan Goldfajn"},
        ],
    },
    "bolsonaro": {
        "id": "bolsonaro",
        "presidente": "Jair Bolsonaro",
        "partido": "PSL / PL",
        "vice": "Hamilton Mourão",
        "periodo": "2019–2022",
        "ano_inicio": 2019,
        "ano_fim": 2022,
        "data_inicio": "01/01/2019",
        "data_fim": "31/12/2022",
        "mandatos": "1º mandato",
        "ministros_notaveis": [
            {"pasta": "Economia", "nome": "Paulo Guedes"},
            {"pasta": "Banco Central", "nome": "Roberto Campos Neto"},
        ],
    },
}


def _normalize(text: str) -> str:
    """Normaliza texto removendo acentos, caracteres especiais e espaços extras."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ASCII", "ignore").decode("utf-8")
    return ascii_text.lower().strip()


def get_preset_governo(nome_ou_preset: str) -> Optional[Dict[str, Any]]:
    """
    Retorna a configuração do preset para um presidente/governo pré-definido.
    Aceita apelidos e nomes comuns ('bolsonaro', 'lula', 'fhc', 'dilma', 'temer').
    """
    if not nome_ou_preset:
        return None

    normalized = _normalize(nome_ou_preset)

    alias_map = {
        "fhc": "fhc",
        "fernando henrique": "fhc",
        "fernando henrique cardoso": "fhc",
        "cardoso": "fhc",
        "lula": "lula",
        "luiz inacio lula da silva": "lula",
        "luis inacio lula da silva": "lula",
        "dilma": "dilma",
        "dilma rousseff": "dilma",
        "temer": "temer",
        "michel temer": "temer",
        "bolsonaro": "bolsonaro",
        "jair bolsonaro": "bolsonaro",
        "jair messias bolsonaro": "bolsonaro",
    }

    preset_key = alias_map.get(normalized)
    if not preset_key:
        tokens = set(normalized.split())
        for k in PRESETS_GOVERNO:
            if k in tokens or (len(normalized) >= 3 and (k in normalized or normalized in k)):
                preset_key = k
                break

    if preset_key and preset_key in PRESETS_GOVERNO:
        return json.loads(json.dumps(PRESETS_GOVERNO[preset_key]))

    return None


def calcular_variacao_acumulada(taxas: List[float]) -> float:
    """
    Calcula a taxa de variação acumulada composta a partir de uma lista de percentuais.
    Fórmula: [produtorio(1 + t_i / 100) - 1] * 100
    Retorna percentual com 2 casas decimais.
    """
    if not taxas:
        return 0.0

    fator = 1.0
    for t in taxas:
        try:
            fator *= 1.0 + (float(t) / 100.0)
        except (ValueError, TypeError):
            continue

    acumulada = (fator - 1.0) * 100.0
    return round(acumulada, 2)


def http_get_json(url: str, timeout: int = 10, tentativas: int = 3) -> Optional[Any]:
    """
    Executa requisição HTTP GET retornando JSON com retentativas e timeout.
    """
    for tentativa in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw)
                return None
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"[WARN] HTTP {e.code} ao consultar {url}\n")
            return None
        except Exception as e:
            if tentativa == tentativas:
                sys.stderr.write(f"[WARN] Falha ao consultar {url} ({tentativas} tentativas): {e}\n")
            else:
                time.sleep(0.5 * tentativa)
    return None


def consultar_serie_bcb(
    codigo: int, data_inicio: str, data_fim: str, timeout: int = 10
) -> List[Dict[str, Any]]:
    """
    Consulta uma série temporal específica na API aberta do BCB SGS.
    Parâmetros:
      - codigo: identificador numérico da série no SGS.
      - data_inicio: 'DD/MM/AAAA'
      - data_fim: 'DD/MM/AAAA'
    Retorna lista de dicionários [{'data': 'DD/MM/AAAA', 'valor': float}].
    """
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        f"?formato=json&dataInicial={data_inicio}&dataFinal={data_fim}"
    )

    dados = http_get_json(url, timeout=timeout)
    if not isinstance(dados, list):
        return []

    resultado: List[Dict[str, Any]] = []
    for item in dados:
        if not isinstance(item, dict):
            continue
        raw_val = item.get("valor")
        data_str = item.get("data", "")
        if raw_val is None or not data_str:
            continue
        try:
            if isinstance(raw_val, str):
                raw_val = raw_val.strip()
                if "," in raw_val:
                    # Padrão brasileiro: remove pontos de milhar e substitui vírgula decimal por ponto
                    raw_val = raw_val.replace(".", "").replace(",", ".")
            valor_float = float(raw_val)
            resultado.append({"data": data_str, "valor": valor_float})
        except (ValueError, TypeError):
            continue

    return resultado


def _converter_data(data_str: str) -> tuple:
    """Converte 'DD/MM/AAAA' para tupla ordenável (ano, mês, dia)."""
    partes = data_str.split("/")
    if len(partes) == 3:
        try:
            return (int(partes[2]), int(partes[1]), int(partes[0]))
        except ValueError:
            pass
    return (0, 0, 0)


def _extrair_ano(data_str: str) -> Optional[int]:
    """Extrai o ano (int) de datas no formato DD/MM/AAAA."""
    ano = _converter_data(data_str)[0]
    return ano if ano > 0 else None


def fetch_dados_governo(
    nome_ou_preset: str,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Coleta indicadores macroeconômicos e estrutura os dados de mandato presidencial.
    Produz os blocos:
      - tipo_dossie: 'governo_presidencial'
      - mandato_executivo: metadados do presidente, período, ministros
      - indicadores_economicos: resumo macro, séries completas e agrupamento anual
      - cofres_publicos: resultado primário, dívida pública e fontes
    """
    preset = get_preset_governo(nome_ou_preset)

    if preset:
        dt_ini = data_inicio or preset["data_inicio"]
        dt_fim = data_fim or preset["data_fim"]
        mandato_meta = preset
    else:
        # Período customizado
        dt_ini = data_inicio or "01/01/2019"
        dt_fim = data_fim or "31/12/2022"
        ano_i = _extrair_ano(dt_ini) or 2019
        ano_f = _extrair_ano(dt_fim) or 2022
        mandato_meta = {
            "id": _normalize(nome_ou_preset).replace(" ", "_"),
            "presidente": nome_ou_preset,
            "partido": "Não especificado",
            "vice": "Não especificado",
            "periodo": f"{ano_i}–{ano_f}",
            "ano_inicio": ano_i,
            "ano_fim": ano_f,
            "data_inicio": dt_ini,
            "data_fim": dt_fim,
            "mandatos": "Personalizado",
            "ministros_notaveis": [],
        }

    # Consulta séries históricas no BCB SGS
    serie_ipca = consultar_serie_bcb(BCB_SERIES["ipca_mensal"], dt_ini, dt_fim)
    serie_selic = consultar_serie_bcb(BCB_SERIES["selic_meta"], dt_ini, dt_fim)
    if not serie_selic:
        serie_selic = consultar_serie_bcb(BCB_SERIES["selic_diaria"], dt_ini, dt_fim)
    else:
        # A meta Selic fixada pelo Copom (série 432) iniciou em 05/03/1999.
        # Para períodos que iniciam antes disso (ex: governo FHC 1995-2002),
        # complementa os anos anteriores usando a taxa Selic diária anualizada (série 1178).
        dt_ini_tuple = _converter_data(dt_ini)
        primeira_dt_432 = _converter_data(serie_selic[0]["data"])
        if dt_ini_tuple < primeira_dt_432:
            serie_diaria = consultar_serie_bcb(BCB_SERIES["selic_diaria"], dt_ini, dt_fim)
            pontos_anteriores = [
                p for p in serie_diaria if _converter_data(p["data"]) < primeira_dt_432
            ]
            serie_selic = pontos_anteriores + serie_selic
    serie_dolar = consultar_serie_bcb(BCB_SERIES["dolar_ptax"], dt_ini, dt_fim)
    serie_divida = consultar_serie_bcb(BCB_SERIES["divida_bruta_pib"], dt_ini, dt_fim)
    serie_pib = consultar_serie_bcb(BCB_SERIES["pib_crescimento_real"], dt_ini, dt_fim)

    ano_ini_calc = _extrair_ano(dt_ini) or mandato_meta["ano_inicio"]
    ano_fim_calc = _extrair_ano(dt_fim) or mandato_meta["ano_fim"]
    anos_total = max(1, ano_fim_calc - ano_ini_calc + 1)

    # 1. Cálculos de IPCA
    taxas_ipca = [item["valor"] for item in serie_ipca]
    ipca_acumulado = calcular_variacao_acumulada(taxas_ipca)
    ipca_media_anual = round(ipca_acumulado / anos_total, 2) if taxas_ipca else 0.0

    # 2. Cálculos de Selic
    selic_inicial = round(serie_selic[0]["valor"], 2) if serie_selic else 0.0
    selic_final = round(serie_selic[-1]["valor"], 2) if serie_selic else 0.0
    selic_media = round(sum(p["valor"] for p in serie_selic) / len(serie_selic), 2) if serie_selic else 0.0

    # 3. Cálculos de Câmbio (Dólar PTAX)
    dolar_inicial = round(serie_dolar[0]["valor"], 4) if serie_dolar else 0.0
    dolar_final = round(serie_dolar[-1]["valor"], 4) if serie_dolar else 0.0
    if dolar_inicial > 0 and dolar_final > 0:
        dolar_var_pct = round(((dolar_final - dolar_inicial) / dolar_inicial) * 100.0, 2)
    else:
        dolar_var_pct = 0.0

    # 4. Cálculos de Dívida Bruta (% PIB)
    divida_inicial = round(serie_divida[0]["valor"], 2) if serie_divida else None
    divida_final = round(serie_divida[-1]["valor"], 2) if serie_divida else None
    divida_var_pp = round(divida_final - divida_inicial, 2) if (divida_inicial is not None and divida_final is not None) else None

    # 5. Cálculos de PIB
    pib_valores = [p["valor"] for p in serie_pib]
    pib_medio_anual = round(sum(pib_valores) / len(pib_valores), 2) if pib_valores else None

    # 6. Agrupamento anual para gráficos (Recharts)
    anos_range = range(ano_ini_calc, ano_fim_calc + 1)
    grafico_anual: List[Dict[str, Any]] = []

    for ano in anos_range:
        pontos_ipca_ano = [p["valor"] for p in serie_ipca if _extrair_ano(p["data"]) == ano]
        ipca_ano = calcular_variacao_acumulada(pontos_ipca_ano) if pontos_ipca_ano else None

        selic_ano = [p["valor"] for p in serie_selic if _extrair_ano(p["data"]) == ano]
        selic_fim_ano = round(selic_ano[-1], 2) if selic_ano else None

        dolar_ano = [p["valor"] for p in serie_dolar if _extrair_ano(p["data"]) == ano]
        dolar_fim_ano = round(dolar_ano[-1], 4) if dolar_ano else None

        divida_ano = [p["valor"] for p in serie_divida if _extrair_ano(p["data"]) == ano]
        divida_fim_ano = round(divida_ano[-1], 2) if divida_ano else None

        pib_ano_pts = [p["valor"] for p in serie_pib if _extrair_ano(p["data"]) == ano]
        pib_ano = round(pib_ano_pts[-1], 2) if pib_ano_pts else None

        grafico_anual.append({
            "ano": ano,
            "ipca": ipca_ano,
            "selic_fim": selic_fim_ano,
            "dolar_fim": dolar_fim_ano,
            "divida_bruta_pib": divida_fim_ano,
            "pib_crescimento": pib_ano,
        })

    return {
        "tipo_dossie": "governo_presidencial",
        "mandato_executivo": mandato_meta,
        "indicadores_economicos": {
            "resumo_macro": {
                "ipca_acumulado": ipca_acumulado,
                "ipca_media_anual": ipca_media_anual,
                "selic_inicial": selic_inicial,
                "selic_final": selic_final,
                "selic_media": selic_media,
                "dolar_inicial": dolar_inicial,
                "dolar_final": dolar_final,
                "dolar_variacao_pct": dolar_var_pct,
                "divida_bruta_inicial": divida_inicial,
                "divida_bruta_final": divida_final,
                "divida_bruta_variacao_pp": divida_var_pp,
                "pib_crescimento_medio_anual": pib_medio_anual,
            },
            "series": {
                "ipca": serie_ipca,
                "selic": serie_selic,
                "dolar": serie_dolar,
                "divida_bruta": serie_divida,
                "pib": serie_pib,
            },
            "grafico_anual": grafico_anual,
        },
        "cofres_publicos": {
            "fontes": [
                "Banco Central do Brasil - Sistema Gerenciador de Séries Temporais (SGS)",
                "Secretaria do Tesouro Nacional / Portal da Transparência",
            ],
            "descricao": "Dados macrofiscais oficiais consolidados do Governo Federal.",
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Coletor macroeconômico do BCB SGS para governos presidenciais."
    )
    parser.add_argument(
        "governo",
        type=str,
        help="Nome ou identificador do preset (ex: 'bolsonaro', 'lula', 'fhc', 'dilma', 'temer').",
    )
    parser.add_argument(
        "--inicio",
        type=str,
        default=None,
        help="Data inicial customizada no formato DD/MM/AAAA.",
    )
    parser.add_argument(
        "--fim",
        type=str,
        default=None,
        help="Data final customizada no formato DD/MM/AAAA.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Caminho opcional para salvar o JSON resultante.",
    )

    args = parser.parse_args()

    dados = fetch_dados_governo(args.governo, args.inicio, args.fim)
    output_json = json.dumps(dados, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        sys.stderr.write(f"[INFO] Dados salvos com sucesso em {args.output}\n")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
