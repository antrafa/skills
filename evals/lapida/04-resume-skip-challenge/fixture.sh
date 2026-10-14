#!/usr/bin/env bash
set -eu
mkdir -p ideas
cat > ideas/estoque-feirantes.md <<'MD'
# Feirante perde venda por não saber o que tem no estoque

Classe: negócio · Fase: CHALLENGE · Atualizado: 2026-09-20

## Ideia original
Um app de controle de estoque para feirantes.

## Problema real
Feirantes de hortifrúti descartam mercadoria e perdem venda porque decidem a compra no atacado de memória, sem saber o que sobrou da última feira.

## Público-alvo
Feirantes de hortifrúti com banca própria em feiras livres de São Paulo, que compram no Ceagesp duas ou mais vezes por semana.

## Job to be done
Quando vou ao Ceagesp de madrugada, quero saber quanto sobrou de cada item, para comprar só o que vou vender e não jogar mercadoria fora.

## Evidência atual
- Três feirantes conhecidos do usuário relatam descarte semanal — weak (opinião, sem número)
- O usuário estima 15% de perda por semana — none (estimativa própria)

## Workaround atual
Anotam no caderno, fotografam a banca no fim da feira ou compram de memória.

## Registro de decisões
- 2026-09-20 — público restrito a hortifrúti — perecível concentra a perda
MD
