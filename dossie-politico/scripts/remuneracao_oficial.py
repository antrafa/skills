#!/usr/bin/env python3
"""Valores legais de remuneração e verbas do mandato parlamentar federal.

Único lugar para atualizar quando a norma mudar. Antes, o valor estava escrito
duas vezes dentro dos coletores e saía no relatório como dado apurado, sem
vigência nem fonte — apodrecia em silêncio a cada reajuste.

Nada aqui é reconferido automaticamente: o relatório declara a norma de origem
e manda o leitor ao portal oficial em vez de afirmar que o número está atual.
"""

# Norma que fixa o subsídio dos parlamentares federais.
SUBSIDIO_NORMA = "Decreto Legislativo 172/2022"
SUBSIDIO_VALOR = "R$ 44.008,52"
SUBSIDIO_CONFERIR_EM = "https://www2.camara.leg.br/transparencia/remuneracao-dos-parlamentares"

CEAP_CONFERIR_EM = "https://www2.camara.leg.br/transparencia/cota-para-exercicio-da-atividade-parlamentar"
CEAPS_CONFERIR_EM = "https://www12.senado.leg.br/transparencia/ceaps"


def subsidio(cargo: str) -> str:
    return f"{SUBSIDIO_VALOR} (subsídio de {cargo} fixado pelo {SUBSIDIO_NORMA})"


def contexto_remuneracao(conferir_em: str) -> str:
    return (
        f"Valor bruto previsto no {SUBSIDIO_NORMA}, sem descontos. "
        f"A skill não reconfere reajustes: confirme o valor vigente em {conferir_em}"
    )


AUXILIOS_DEPUTADO = [
    "Cota para o Exercício da Atividade Parlamentar (CEAP): teto mensal varia por UF — "
    f"confira a tabela vigente em {CEAP_CONFERIR_EM}",
    "Verba de Gabinete para contratação de secretários parlamentares (limite fixado por ato da Mesa)",
    "Auxílio-moradia ou apartamento funcional em Brasília",
    "Ajuda de custo no início e no fim do mandato, equivalente a um subsídio mensal",
]

AUXILIOS_SENADOR = [
    "Cota para o Exercício da Atividade Parlamentar dos Senadores (CEAPS): teto mensal varia por UF — "
    f"confira a tabela vigente em {CEAPS_CONFERIR_EM}",
    "Verba de Gabinete para contratação de assessores (limite fixado por ato da Mesa)",
    "Auxílio-moradia ou apartamento funcional em Brasília",
    "Assistência à saúde custeada pela Casa, nos termos do ato interno vigente",
]
