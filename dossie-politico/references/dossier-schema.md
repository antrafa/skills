# Dossier Data Structure and Schema (JSON Schema)

The compiled political dossier follows this standardized data structure before HTML rendering. Keys and enum values are a contract with the scripts and stay exactly as written; `example` values show the Portuguese content the dossier carries.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DossiePoliticoData",
  "type": "object",
  "required": [
    "nome_eleitoral",
    "cargo",
    "partido",
    "uf",
    "data_corte",
    "resumo_cidadao_ia",
    "cobertura_pesquisa"
  ],
  "properties": {
    "nome_eleitoral": { "type": "string" },
    "nome_civil": { "type": "string" },
    "cargo": { "type": "string", "example": "Deputado Federal, Senador da República, Governador, etc." },
    "partido": { "type": "string", "example": "PP, PL, PT, PSD, etc." },
    "uf": { "type": "string", "example": "SP, RJ, MG, etc." },
    "situacao": { "type": "string", "example": "Exercício, Licenciado, Afastado" },
    "status_eleitoral": { "type": "string", "example": "Candidatura registrada — aguardando julgamento" },
    "data_corte": { "type": "string", "example": "2026-08-22" },
    "foto_url": { "type": "string" },
    "email": { "type": "string" },
    "telefone_gabinete": { "type": "string" },
    "data_nascimento": { "type": "string" },
    "municipio_nascimento": { "type": "string" },
    "escolaridade": { "type": "string" },
    "redes_sociais": {
      "type": "array",
      "items": { "type": "string" }
    },
    "resumo_cidadao_ia": {
      "type": "object",
      "required": ["sintese", "pontos_chave", "lacunas", "aviso"],
      "properties": {
        "sintese": {
          "type": "string",
          "description": "Factual X-ray in plain language, roughly 300 to 600 words, covering identity, career, activity, public money, assets, proposals, every material catalogued case, the right of reply and gaps, with no voting recommendation."
        },
        "pontos_chave": {
          "type": "array",
          "minItems": 3,
          "maxItems": 6,
          "items": {
            "oneOf": [
              { "type": "string" },
              {
                "type": "object",
                "required": ["titulo", "texto"],
                "properties": {
                  "titulo": { "type": "string" },
                  "texto": { "type": "string" }
                }
              }
            ]
          }
        },
        "lacunas": {
          "type": "array",
          "items": { "type": "string" }
        },
        "aviso": {
          "type": "string",
          "example": "Síntese gerada por IA a partir dos dados e fontes deste dossiê; confira os links antes de formar sua conclusão."
        }
      }
    },
    "cobertura_pesquisa": {
      "type": "object",
      "description": "Auditable record of the reach and limitations of the search for facts of public interest.",
      "properties": {
        "data_execucao": { "type": "string", "example": "2026-08-22" },
        "periodo": { "type": "string", "example": "2021-01-01 a 2026-08-22, com fatos anteriores ainda ativos" },
        "nomes_consultados": {
          "type": "array",
          "items": { "type": "string" }
        },
        "eixos_verificados": {
          "type": "array",
          "items": { "type": "string" }
        },
        "fontes_consultadas": {
          "type": "array",
          "items": { "type": "string" }
        },
        "limitacoes": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "salario_oficial_base": { "type": "string", "example": "R$ 44.008,52" },
    "salario_label": { "type": "string", "example": "Remuneração da candidatura" },
    "salario_contexto": { "type": "string" },
    "assiduidade_label": { "type": "string", "example": "Métrica parlamentar" },
    "assiduidade_contexto": { "type": "string" },
    "titulo_secao_remuneracao": { "type": "string" },
    "remuneracao_descricao": { "type": "string" },
    "titulo_secao_atuacao": { "type": "string", "example": "Plano de governo e atuação pública" },
    "itens_label": { "type": "string", "example": "Eixos" },
    "titulo_secao_controversias": { "type": "string", "example": "Escândalos, polêmicas e fatos verificados" },
    "auxilios_previstos": {
      "type": "array",
      "items": { "type": "string" }
    },
    "assiduidade_percentual": { "type": "string", "example": "94.5% de presença nas sessões deliberativas" },
    "proposicoes_principais": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "tipo": { "type": "string", "example": "PL, PEC, MPV" },
          "numero": { "type": ["string", "number"] },
          "ano": { "type": ["string", "number"] },
          "ementa": { "type": "string" },
          "data": { "type": "string" },
          "link": { "type": "string" }
        }
      }
    },
    "evolucao_patrimonial": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ano": { "type": ["string", "number"] },
          "cargo_disputado": { "type": "string" },
          "valor": { "type": "number" },
          "valor_formatado": { "type": "string" }
        }
      }
    },
    "controversias_e_noticias": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "titulo": { "type": "string" },
          "data": { "type": "string" },
          "categoria": { "type": "string", "example": "Operação Policial, Investigação STF, Uso de Cota, Processo Eleitoral" },
          "status": { "type": "string", "example": "Em Investigação, Denunciado, Réu, Condenado, Absolvido, Arquivado" },
          "grau_veracidade": {
            "type": "string",
            "enum": [
              "Confirmado por documento/decisão",
              "Fortemente sustentado",
              "Alegação oficial em apuração",
              "Contestado / não comprovado",
              "Falso ou enganoso"
            ]
          },
          "criterio_veracidade": { "type": "string" },
          "o_que_esta_comprovado": { "type": "string" },
          "o_que_nao_esta_comprovado": { "type": "string" },
          "resumo": { "type": "string" },
          "posicao_defesa": { "type": "string" },
          "fontes": {
            "type": "array",
            "description": "Each URL is checked at generation time (HTTP). A link that does not resolve appears struck through and flagged with ⚠️ in the report: replace it with a checked URL instead of citing from memory.",
            "items": {
              "type": "object",
              "properties": {
                "veiculo": { "type": "string" },
                "url": { "type": "string", "description": "Omit when you do not have a checked address. Without url, the report shows outlet and date with the mark 'URL não localizada' — which is correct; a link rebuilt from memory is not." },
                "data": { "type": "string", "description": "Shown when there is no url." },
                "status_link": { "type": "string", "description": "Filled automatically: ok, quebrado (broken, 404), nao verificavel (not verifiable, 403), nao verificado (not checked)." }
              }
            }
          }
        }
      }
    },
    "despesas_discriminadas": {
      "type": "array",
      "description": "Public spending broken down by category (parliamentary allowance, office allowance, per diems, corporate card).",
      "items": {
        "type": "object",
        "properties": {
          "categoria": { "type": "string" },
          "valor": { "type": "number" },
          "valor_formatado": { "type": "string" },
          "detalhe": { "type": "string", "description": "Period, relevant suppliers and the receipt link, when public." }
        }
      }
    },
    "despesas_resumo": {
      "type": "object",
      "description": "Parliamentary allowance aggregation produced by scripts/fetch_camara.py. Fill by hand for offices with no collector.",
      "properties": {
        "periodo": { "type": "string", "example": "2023 a 2026" },
        "total": { "type": "number" },
        "total_formatado": { "type": "string" },
        "registros_analisados": { "type": "number" },
        "truncado": { "type": "boolean", "description": "True when reading stopped at the page limit: the total is partial." },
        "por_ano": { "type": "array", "items": { "type": "object", "properties": { "ano": { "type": ["string", "number"] }, "valor": { "type": "number" }, "valor_formatado": { "type": "string" } } } },
        "por_categoria": { "type": "array", "items": { "type": "object", "properties": { "categoria": { "type": "string" }, "valor": { "type": "number" }, "valor_formatado": { "type": "string" }, "notas": { "type": "number" } } } },
        "principais_fornecedores": { "type": "array", "items": { "type": "object", "properties": { "nome": { "type": "string" }, "cnpj_cpf": { "type": "string" }, "valor": { "type": "number" }, "valor_formatado": { "type": "string" }, "notas": { "type": "number" } } } }
      }
    },
    "revisoes_anteriores": {
      "type": "array",
      "description": "Filled automatically from the catalog: dates of earlier generations, shown in the footer.",
      "items": { "type": "string" }
    },
    "mandato_periodo": { "type": "string", "example": "2023 a 2027" },
    "legislatura": { "type": ["string", "number"] },
    "patrimonio_declarado_recente": { "type": "string", "example": "R$ 1.589.369,94 (2022)" },
    "controversias_nota": {
      "type": "string",
      "description": "Replaces the default notice when there are no catalogued cases. Never claim that no facts exist."
    },
    "comissoes_orgaos": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "nome": { "type": "string" },
          "sigla": { "type": "string" },
          "cargo": { "type": "string", "example": "Titular, Suplente, Presidente" },
          "data_inicio": { "type": "string" }
        }
      }
    },
    "frentes_destaque": { "type": "array", "items": { "type": "string" } },
    "frentes_parlamentares_count": { "type": ["string", "number"] },
    "discursos_recentes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "data_hora": { "type": "string" },
          "fase": { "type": "string" },
          "sumario": { "type": "string" }
        }
      }
    },
    "suplentes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "participacao": { "type": "string" },
          "nome": { "type": "string" }
        }
      }
    },
    "bloco_parlamentar": { "type": "string" },
    "sala_gabinete": { "type": "string", "description": "Official office address. Never use a home address." },
    "links_transparencia": {
      "type": "object",
      "description": "Open searches on official portals for independent checking, generated by scripts/fetch_tse_transparency.py.",
      "additionalProperties": { "type": "string" }
    },
    "link_perfil_oficial": { "type": "string" },
    "link_transparencia_gastos": { "type": "string" },
    "link_presenca": { "type": "string" },
    "link_votacoes": { "type": "string" },
    "link_tse": { "type": "string" },
    "tipo_dossie": {
      "type": "string",
      "enum": ["perfil_politico", "governo_presidencial"],
      "default": "perfil_politico",
      "description": "Distinguishes individual profiles (legislators/candidates) from analytical dossiers on executive government terms."
    },
    "mandato_executivo": {
      "type": "object",
      "description": "Metadata on the term of a head of the Executive (former presidents or governors).",
      "properties": {
        "id": { "type": "string", "example": "bolsonaro, lula, fhc" },
        "presidente": { "type": "string" },
        "partido": { "type": "string" },
        "vice": { "type": "string" },
        "periodo": { "type": "string", "example": "2019–2022" },
        "ano_inicio": { "type": "integer" },
        "ano_fim": { "type": "integer" },
        "data_inicio": { "type": "string", "example": "01/01/2019" },
        "data_fim": { "type": "string", "example": "31/12/2022" },
        "mandatos": { "type": "string" },
        "ministros_notaveis": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "pasta": { "type": "string" },
              "nome": { "type": "string" }
            }
          }
        }
      }
    },
    "indicadores_economicos": {
      "type": "object",
      "description": "Macroeconomic series and consolidation generated from the Banco Central do Brasil (SGS).",
      "properties": {
        "resumo_macro": {
          "type": "object",
          "properties": {
            "ipca_acumulado": { "type": "number" },
            "ipca_media_anual": { "type": "number" },
            "selic_inicial": { "type": "number" },
            "selic_final": { "type": "number" },
            "selic_media": { "type": "number" },
            "dolar_inicial": { "type": "number" },
            "dolar_final": { "type": "number" },
            "dolar_variacao_pct": { "type": "number" },
            "divida_bruta_inicial": { "type": ["number", "null"] },
            "divida_bruta_final": { "type": ["number", "null"] },
            "divida_bruta_variacao_pp": { "type": ["number", "null"] },
            "pib_crescimento_medio_anual": { "type": ["number", "null"] }
          }
        },
        "series": {
          "type": "object",
          "description": "Full BCB SGS data series (IPCA inflation, Selic rate, dollar, gross debt, GDP)."
        },
        "grafico_anual": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "ano": { "type": "integer" },
              "ipca": { "type": ["number", "null"] },
              "selic_fim": { "type": ["number", "null"] },
              "dolar_fim": { "type": ["number", "null"] },
              "divida_bruta_pib": { "type": ["number", "null"] },
              "pib_crescimento": { "type": ["number", "null"] }
            }
          }
        }
      }
    },
    "cofres_publicos": {
      "type": "object",
      "description": "Public accounts, primary balance and operating expenses of the Presidency.",
      "properties": {
        "resultado_fiscal_acumulado": { "type": "string" },
        "divida_publica_trajetoria": { "type": "string" },
        "cartao_corporativo_total": { "type": "string" },
        "fontes": { "type": "array", "items": { "type": "string" } },
        "descricao": { "type": "string" }
      }
    },
    "promessas_campanha": {
      "type": "object",
      "description": "Factual scorecard of fulfillment of campaign promises registered with the electoral courts.",
      "properties": {
        "fonte": { "type": "string" },
        "total": { "type": "integer" },
        "cumpridas": { "type": "integer" },
        "parciais": { "type": "integer" },
        "nao_cumpridas": { "type": "integer" },
        "taxa_cumprimento_pct": { "type": "number" },
        "itens": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["titulo", "status", "detalhes"],
            "properties": {
              "titulo": { "type": "string" },
              "categoria": { "type": "string" },
              "status": { "type": "string", "example": "Cumprida, Cumprida em parte, Não cumprida" },
              "detalhes": { "type": "string" },
              "fonte": { "type": "string" }
            }
          }
        }
      }
    },
    "projetos_de_lei_e_reformas": {
      "type": "array",
      "description": "Constitutional amendments, complementary and ordinary laws signed/enacted during the term.",
      "items": {
        "type": "object",
        "required": ["titulo", "norma", "ano", "impacto"],
        "properties": {
          "titulo": { "type": "string" },
          "norma": { "type": "string", "example": "EC 103/2019, LC 179/2021" },
          "ano": { "type": ["integer", "string"] },
          "ementa": { "type": "string" },
          "impacto": { "type": "string" },
          "link": { "type": "string" }
        }
      }
    }
  }
}
```

