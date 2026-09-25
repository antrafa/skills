#!/usr/bin/env bash
set -eu
mkdir -p ideas
cat > ideas/estoque-feirantes.md <<'MD'
# Feirante perde venda por não saber o que tem no estoque

Classe: negócio · Fase: FIT · Atualizado: 2026-09-21

## Ideia original
Um app de controle de estoque para feirantes.

## Problema real
Feirantes de hortifrúti descartam mercadoria e perdem venda porque decidem a compra no atacado de memória, sem saber o que sobrou da última feira.

## Público-alvo
Feirantes de hortifrúti com banca própria em feiras livres de São Paulo, que compram no Ceagesp duas ou mais vezes por semana.

## Job to be done
Quando vou ao Ceagesp de madrugada, quero saber quanto sobrou de cada item, para comprar só o que vou vender e não jogar mercadoria fora.

## Evidência atual
- Três feirantes conhecidos do usuário relatam descarte semanal — weak (relato, sem número)
- O usuário estima 15% de perda por semana — none (estimativa própria)

## Workaround atual
Anotam no caderno, fotografam a banca no fim da feira ou compram de memória.

## Riscos e premissas
| Premissa | Lente | Importância | Evidência |
|---|---|---|---|
| Feirante registra a sobra no fim da feira, cansado | D | alta | none |
| Feirante paga R$ 30/mês por isso | V | alta | none |
| Registro por foto ou voz é possível sem digitação | F | média | weak |
**Mais arriscada:** feirante registra a sobra no fim da feira — sem registro não há dado, e ninguém observou esse hábito.
**Pre-mortem:** em doze meses, os feirantes testaram duas semanas e pararam de registrar; o app ficou vazio.
**Não fazer nada:** seguem com caderno e memória; a perda continua, mas ninguém deixa de trabalhar.
**Contradições:** nenhuma encontrada.

## Hipótese de solução
Opções consideradas: app com registro por foto · planilha compartilhada no celular · concierge por WhatsApp, em que o feirante manda um áudio com a sobra e recebe de volta a lista de compra
Acreditamos que o concierge por WhatsApp fará o feirante comprar só o que vende, reduzindo o descarte, para feirantes de hortifrúti com banca própria.

## Diferencial
Não pede digitação nem app novo: um áudio de 30 segundos no WhatsApp, que o feirante já usa, contra o caderno que ninguém consulta às 3h da manhã.

## Versão refinada
Durante quatro semanas, um humano recebe por WhatsApp o áudio da sobra de 10 feirantes ao fim de cada feira e devolve, antes da ida ao Ceagesp, uma lista sugerida de compra. Sem app, sem cobrança no piloto.
**Fora da v1:** app próprio — só depois de provar o hábito de registro; previsão de demanda — sem histórico não há o que prever; cobrança — decidir depois de medir a redução de perda.

## Registro de decisões
- 2026-09-20 — público restrito a hortifrúti — perecível concentra a perda
- 2026-09-21 — CHALLENGE aprovado — premissa mais arriscada é o hábito de registro
- 2026-09-22 — REFINE aprovado — concierge por WhatsApp testa o hábito sem construir nada
MD
