#!/usr/bin/env python3
"""Legal pay and allowance values for a federal legislative term.

The single place to update when the governing norm changes. Before, the value was
written twice inside the collectors and came out in the report as verified data,
with no effective date or source — it rotted silently with every pay adjustment.

Nothing here is rechecked automatically: the report states the source norm and
sends the reader to the official portal instead of claiming the number is current.
"""

# Norm that sets the salary (subsídio) of federal legislators.
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
