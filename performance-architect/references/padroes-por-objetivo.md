# Padrões por Objetivo

Padrões para os objetivos que **não** são ingestão de alto volume — para
esse, use `arquitetura-ingestao.md`. Mesmo formato: cada padrão vem com **o
número que o justifica** e **o custo que traz**. Padrão adotado sem o
número é moda; adotado sem o custo é dívida.

## Índice
- [Leitura intensiva](#leitura-intensiva)
- [Latência de caminho crítico](#latência-de-caminho-crítico)
- [Custo e right-sizing](#custo-e-right-sizing)
- [Batch e janela de processamento](#batch-e-janela-de-processamento)
- [Resiliência sob carga](#resiliência-sob-carga)
- [Anti-padrões transversais](#anti-padrões-transversais)

## Leitura intensiva

A pergunta que vem antes: **com que frequência o dado muda, e quanto tempo de
atraso o leitor tolera?** A resposta define a cacheabilidade — e um dado que
só muda à noite é a maior oportunidade que um sistema de leitura pode ter.

Ordem de adoção, por ganho/risco:

1. **`EXPLAIN` das consultas das páginas pesadas** antes de qualquer coisa.
   Seq scan em tabela grande com filtro seletivo é falta de índice; índice
   existente não usado é predicado incompatível (função sobre a coluna, tipo
   diferente, `LIKE '%x'`). Custo: cada índice custa em toda escrita —
   justifique com a consulta real.
2. **N+1 do ORM.** Uma página que dispara 200 queries de 1 ms leva 200 ms
   só em ida e volta. Evidência: log de SQL com contagem por request.
   Correção: fetch join, `IN` em lote, ou projeção direta. Custo: baixo.
3. **Paginação** do que carrega tudo. Justifica quando a lista cresce sem
   teto; **não** justifica quando são 200 linhas por índice (leitura de ms)
   — rejeitar paginação com esse argumento é resposta válida.
4. **Cache**, em camadas, do mais barato para o mais caro:
   - HTTP (`Cache-Control`, ETag, CDN) para resposta idêntica a muitos
     usuários — o maior ganho por esforço em portal público;
   - aplicação (local por réplica, TTL curto) para leitura repetida com
     freshness tolerável;
   - distribuído (Redis) só quando o hit ratio previsível é alto (> 80%) e as
     réplicas precisam compartilhar, ou quando o dado é caro de recalcular.
   Custos: invalidação (a parte difícil); **stampede** no expirar em massa
   (mitigar com jitter no TTL e request coalescing); memória; um componente
   a mais quando é distribuído. Cache antes do `EXPLAIN` esconde a query
   ruim até o primeiro miss em massa.
5. **Materialização / pré-cálculo** pela carga que já existe (noturna, por
   evento): histórico agregado, contadores, visões desnormalizadas. Justifica
   quando o cálculo é caro e o dado muda em ritmo conhecido. Custo: dado
   derivado para manter consistente.
6. **Busca textual** com a técnica certa: índice trigram/GIN para `LIKE`
   parcial e nome de pessoa; motor de busca (Elasticsearch/OpenSearch) só
   quando há relevância, facetas ou volume que o banco não indexa bem —
   custo operacional alto, exige número.
7. **Réplica de leitura** quando leitura pesada compete com escrita na mesma
   instância e isso aparece no p95 de escrita. Custo: lag de replicação (o
   leitor pode ver dado atrasado), licença, mais uma instância.
8. **Escala horizontal do portal por RPS** para o pico de evento (publicação,
   inscrição), com HPA por requisições/s e não por CPU; e o **pico de evento
   é o número de projeto**, não a média do dia (`volumetria.md`, fator 20x+).

## Latência de caminho crítico

Sem **breakdown por etapa** não se otimiza latência — otimiza-se palpite.
Primeira medida sempre: timer por etapa (trace distribuído se houver; um
timer manual por chamada externa se não houver).

| Padrão | Justifica quando | Custo |
|---|---|---|
| Tirar do caminho síncrono o que não é obrigatório antes de responder (notificar, indexar, auditar, calcular derivados) | breakdown mostra que a maior fatia é trabalho cujo resultado o cliente não espera | estado intermediário; processamento assíncrono precisa de SLO e idempotência |
| Paralelizar chamadas independentes | N chamadas em série a dependências independentes; latência = soma vira latência = máximo | complexidade de código; pool de threads/async; timeouts individuais |
| Timeout explícito em todo cliente externo + circuit breaker | qualquer dependência de rede no caminho — ausência de timeout é indisponibilidade, não lentidão | decidir o fallback (erro rápido, resposta parcial, dado em cache) |
| Pool de conexões HTTP com keep-alive | cliente que abre socket novo por request (handshake TCP/TLS a cada chamada; TIME_WAIT acumulado) | configuração; tamanho do pool dimensionado por Little |
| Reduzir payload / serialização | tempo de (de)serialização relevante no profile; resposta com campos que o cliente descarta | contrato de API |
| Warm-up e cold start | latência alta nas primeiras requisições após deploy/scale-up (JIT, cache frio, pool vazio) | readiness que só libera após warm-up; `minReplicas` |
| Índice / plano de execução | consulta do caminho crítico com plano ruim no `EXPLAIN` | custo em toda escrita |

**Amplificação de cauda** (`objetivos-e-metodos.md`): com 10 dependências em
série, p99 de cada uma vira ~p90 do total. Reduzir o número de saltos no
caminho crítico costuma valer mais que acelerar cada salto.

## Custo e right-sizing

Regra que não se negocia: **SLO medido antes e depois**. Corte sem medição de
latência e erro é aposta com produção, e a fatura da aposta chega como
incidente.

Ordem, por segurança:

1. **Baseline.** Custo atual por serviço/ambiente (fatura, console) e SLI
   atual (p95, erro). Sem os dois, não há como provar o ganho nem detectar a
   degradação.
2. **`requests` vs uso real.** Colete `top pod` em vários horários incluindo
   o pico (ou métrica de 2 semanas, se houver). `requests` acima do **p95 de
   uso + margem** é reserva desperdiçada que impede o scheduler de empacotar
   mais pods por nó. `requests` **abaixo** do p95 é a armadilha: o pod
   concorre por CPU não reservada, e memória abaixo do uso vira eviction.
   Ganho típico: densidade por nó, que vira nó a menos.
3. **`limits` e runtime.** Heap da JVM (ou equivalente) coerente com o
   `limits.memory`, com folga para metaspace/stacks/buffers. `limits.cpu`
   baixo economiza zero e gera throttling — em geral vale mais não limitar
   CPU e limitar memória.
4. **Réplicas ociosas.** Serviço com 3 réplicas a 5% cada, sem pico que
   justifique, pode ter `minReplicas: 2` (nunca 1 em produção: N+1). HPA com
   `min` alto "para garantir" é custo permanente por um medo não medido.
5. **Ambientes não produtivos** ligados 24 h × 7: desligar fora do horário
   é frequentemente a maior economia com o menor risco.
6. **Storage, log e métrica.** Retenção de log em DEBUG, métricas de alta
   cardinalidade, volumes órfãos, snapshots antigos. Barato de cortar,
   zero risco funcional.
7. **Compra**: instâncias reservadas / savings plan para a base constante;
   spot para batch tolerante a interrupção. Decisão financeira — leve o
   número para quem decide.

Custo escondido do right-sizing: o tempo de quem faz e a medição contínua
depois. Registre no plano a métrica que **desfaz** o corte (p95 subiu,
throttling apareceu, `OOMKilled`).

## Batch e janela de processamento

Comece pela conta: `registros/s necessários = volume ÷ segundos da janela`,
com o volume do ano que vem. Depois meça o que o job faz hoje: registros/s
atuais, e **onde o tempo é gasto** (leitura, transformação, escrita, espera).

| Padrão | Justifica quando | Custo |
|---|---|---|
| Paralelismo **por partição** (data, cliente, faixa de ID) | job serial que não chega ao registros/s necessário e o dado é particionável sem dependência entre partições | coordenação; garantir que dois workers não pegam a mesma partição |
| Lote na escrita (batch insert/update) e commit por lote | escrita linha a linha com commit por linha — muda a ordem de grandeza | lote grande demais = transação longa, lock e rollback caro; achar o tamanho por medição (centenas a poucos milhares) |
| Leitura por cursor/streaming, não `findAll()` em memória | job que carrega a tabela inteira em heap | código |
| Índices para a leitura do job | `EXPLAIN` da consulta do job com o volume real mostra scan completo | custo em toda escrita OLTP; avaliar índice temporário ou partição |
| Checkpoint e reinício idempotente | job que, ao falhar na hora 5, recomeça do zero | tabela de controle; idempotência da escrita |
| Separar do OLTP (réplica de leitura, janela, instância) | job competindo com o dia (visível no p95 do OLTP durante o job) | infraestrutura |
| Desligar constraints/índices durante carga massiva | carga inicial ou reprocessamento total, nunca o job diário | risco de dado inválido; janela |

**Não** justifica: Kafka, microserviços ou reescrita por causa de um job
lento. Em 9 de 10 casos é commit por linha, `findAll()` ou `EXPLAIN` ruim.

## Resiliência sob carga

Decida **antes** o que o sistema faz quando não acompanha. O modo de falha
aceitável é rejeitar explicitamente; o inaceitável é aceitar e perder.

| Padrão | O que evita | Custo |
|---|---|---|
| Timeout em **todo** cliente externo (conexão e leitura) | thread presa para sempre; ingestão que "para de aceitar" sem erro | escolher o valor: menor que o timeout de quem chama você |
| Backpressure explícito (`429`/`503` + `Retry-After`; fila com teto; `RejectedExecutionHandler` que rejeita ou executa no chamador) | fila em memória crescendo até `OOMKilled`; aceitar o que não se processa | cliente precisa tratar rejeição (cliente automatizado costuma reenviar) |
| Bulkhead (pools separados por dependência/função) | webhook lento esgotando o pool que a ingestão usa | mais pools para dimensionar |
| Retry com backoff exponencial, jitter e **orçamento** | tempestade de retry derrubando a dependência que acabou de voltar | complexidade; retry só em erro transitório e só com idempotência |
| Circuit breaker + fallback definido | esperar o timeout inteiro em dependência que já se sabe caída | decidir o fallback |
| Readiness/liveness/startup probes corretas | tráfego antes da aplicação subir; probe agressiva matando pod saudável sob carga | liveness com `failureThreshold` folgado; startup probe para JVM lenta |
| Shutdown graceful + `terminationGracePeriodSeconds` ≥ tempo de drenar | rolling update descartando requisições em voo e filas em memória | nada relevante |
| `PodDisruptionBudget` | manutenção de nó derrubando todas as réplicas | nada relevante |
| Memória: `limits` com folga sobre heap + alocação por request × concorrência | `OOMKilled` no pico | pode exigir menos réplicas por nó |
| DLQ e alerta de profundidade/idade de fila | mensagem venenosa travando o consumidor; acúmulo silencioso | operação e monitoramento |
| Degradação graciosa (responder o essencial, adiar o resto) | tudo ou nada sob sobrecarga | decidir o que é essencial com o negócio |

**Nunca:** aceitar silenciosamente o que não se consegue processar. Todos os
painéis ficam verdes enquanto o dado se perde.

## Anti-padrões transversais

Recuse em uma linha, com o número, e ofereça a alternativa. Sem sermão.
Tecnologia nova (outra linguagem, Kafka, NoSQL…) segue a tabela única em
`objetivos-e-metodos.md` ("Quando uma tecnologia nova se justifica").

| Proposta | Por que recusar | Alternativa |
|---|---|---|
| Cache antes do `EXPLAIN` | esconde a query ruim até o primeiro miss em massa (deploy, expiração, restart) | `EXPLAIN` e índice primeiro; cache depois, se o número pedir |
| Réplica antes de medir gargalo compartilhado | se throughput não cresce com réplica, réplica só distribui a espera | medir throughput com 1, 2, 4 réplicas |
| Cortar `requests` abaixo do uso real | não economiza; vira throttling e eviction | `requests` = p95 de uso + margem; densidade por nó |
| Aumentar `limits.memory` como solução de OOM | alocação escala com concorrência; sempre há rajada maior | eliminar a alocação (streaming, paginação, teto de fila) |
| Otimizar código sem breakdown | otimiza a função que responde por 3% do tempo | timer por etapa primeiro |
| "Tempo real" sem decompor | dimensiona tudo para a rajada, quando só o "consultável" precisava ser rápido | separar consultável de processado (`arquitetura-ingestao.md`) |
| Cortar custo sem SLO | o corte vira incidente e ninguém prova que economizou | baseline de custo e SLI antes; métrica de rollback no plano |
