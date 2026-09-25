# Diagnóstico de Performance por Camada

Este arquivo cobre onde olhar em **performance sob carga**, camada por
camada. Os exemplos de código são Spring Boot porque é o caso mais comum
neste time; a seção final traduz os mesmos pontos para outras stacks. Para
o fluxo de acesso ao cluster e os comandos de coleta, use
`coleta-cluster.md`; para os métodos (USE, RED, joelho de utilização),
`objetivos-e-metodos.md`.

## Índice
- [Ordem de investigação](#ordem-de-investigação)
- [Sintoma → causa provável → evidência](#sintoma--causa-provável--evidência)
- [Camada 1: caminho crítico da request](#camada-1-caminho-crítico-da-request)
- [Camada 2: transação e pool de conexões](#camada-2-transação-e-pool-de-conexões)
- [Camada 3: memória e GC](#camada-3-memória-e-gc)
- [Camada 4: banco de dados](#camada-4-banco-de-dados)
- [Camada 5: cluster e escala](#camada-5-cluster-e-escala)
- [Idempotência: o bug que só aparece sob carga](#idempotência-o-bug-que-só-aparece-sob-carga)
- [Por stack: onde os mesmos problemas aparecem](#por-stack-onde-os-mesmos-problemas-aparecem)
- [O que pedir quando não há métrica nenhuma](#o-que-pedir-quando-não-há-métrica-nenhuma)

## Ordem de investigação

Sempre de fora para dentro, porque o gargalo tem que estar em algum lugar e
a saturação aponta onde:

1. O que satura primeiro no pico — CPU, memória, pool de conexões, pool de
   threads, I/O, rede, ou nada (e aí o gargalo é uma espera externa)?
2. Qual etapa da request consome o tempo — precisa de breakdown por etapa,
   não de tempo total.
3. Só então, o código daquela etapa.

Pular do sintoma direto para o código é o erro mais comum: leva a otimizar
uma função que responde por 3% do tempo enquanto 70% está numa espera de I/O.

**Saturação em nada** é o caso mais mal diagnosticado: se nenhum recurso
local satura e a latência sobe, o gargalo é fila em espera externa (banco,
storage, serviço terceiro) ou serialização por lock. Não adiciona réplica —
mede a espera.

## Sintoma → causa provável → evidência

| Sintoma | Causa provável | Evidência que confirma |
|---|---|---|
| Latência sobe no pico, CPU baixa | espera em I/O ou pool exausto | saturação do pool, tempo de espera por conexão, breakdown de latência |
| Pool de conexões exausto, CPU do banco baixa | conexão retida por trabalho que não é de banco (upload, chamada HTTP dentro da transação) | tempo médio de uso da conexão vs tempo de query; `@Transactional` no método que faz I/O |
| Latência proporcional ao tamanho do anexo | anexo lido inteiro em memória antes de gravar | correlação latência × tamanho, picos de heap, GC log |
| `OutOfMemoryError` só no pico | acumulação de payload/anexo em heap × concorrência | heap dump, GC log, `-XX:+HeapDumpOnOutOfMemoryError` |
| Pausas periódicas de centenas de ms | GC full recorrente por pressão de alocação | GC log (`-Xlog:gc*`), tempo em pausa por minuto |
| Timeout do cliente, servidor sem erro | trabalho síncrono desnecessário no caminho da request | breakdown por etapa; comparar tempo do que é obrigatório vs total |
| Throughput não cresce ao adicionar réplica | gargalo compartilhado (banco, storage, lock) ou estado na aplicação | throughput por réplica caindo conforme réplicas sobem |
| Uma query específica degrada com o volume | falta de índice, ou índice não usado pelo predicado | `EXPLAIN` / `EXPLAIN ANALYZE` |
| Muitas queries pequenas por request | N+1 do ORM | log de SQL com contagem por request |
| Registro duplicado sob carga | reenvio do cliente em timeout sem idempotência | contagem de duplicatas por chave natural, log do cliente |
| Pod reiniciando no pico | limite de memória abaixo do uso real sob carga | `describe` (exit 137, `OOMKilled`), `top pod` |
| Latência com degrau em múltiplos de 100 ms | CPU throttling por `limits` baixo | `container_cpu_cfs_throttled_seconds_total`, `limits` vs uso |
| Resposta de sucesso, dado não aparece depois | resposta enviada antes da durabilidade (trabalho assíncrono em memória, fila sem confirm) | ler o handler: o que acontece entre o `return` e o commit; restart descarta o quê? |
| Erro de infraestrutura devolvido como `4xx` | cliente automatizado lê "não reenvie" e o dado se perde | mapeamento de exceções no controller; log de `4xx` correlacionado a falha de dependência |
| Job termina fora da janela | commit por linha, `findAll()` em memória, sem paralelismo por partição | registros/s atuais vs necessários; onde o tempo é gasto (leitura/escrita/espera) |
| Throughput não cresce com réplica mesmo com banco folgado | serialização em linha de controle (gerador de ID por tabela, contador, lock de aplicação) | trace de um INSERT; quem faz `SELECT … FOR UPDATE` em toda escrita |

## Camada 1: caminho crítico da request

Leia o handler de ponta a ponta e classifique **cada** operação em uma de
três caixas:

- **Obrigatória antes de responder** — sem isso a resposta é uma mentira.
  Ex.: persistir de forma durável o dado que não pode ser perdido.
- **Necessária, mas não antes de responder** — pode ser assíncrona. Ex.:
  classificar, calcular, notificar, indexar, gerar derivados.
- **Desnecessária** — dá para não fazer. Ex.: consulta cujo resultado ninguém
  usa, validação repetida, serialização de resposta que o cliente descarta.

O tempo de resposta mínimo alcançável é a soma da primeira caixa. Tudo que
está nela e não deveria estar é a maior oportunidade de ganho de um serviço
de ingestão — e é ganho de arquitetura, não de micro-otimização.

Onde olhar num Spring Boot:

- O controller e o serviço no caminho da ingestão.
- Como o anexo é recebido: `MultipartFile.getBytes()` / `byte[]` / `String`
  em base64 carregam o arquivo inteiro em heap. `getInputStream()` com
  streaming para o destino, não.
- Chamadas de rede síncronas (`RestTemplate`, `WebClient.block()`, Feign) no
  caminho: cada uma soma sua latência e seu timeout ao total.
- `@Transactional` — onde começa e onde termina de verdade.
- Trabalho que roda "de brinde": listeners, interceptors, auditoria, aspectos,
  serialização/validação pesada, log de payload inteiro.
- Timeout explícito em todo cliente externo. Ausência de timeout num serviço
  de ingestão sob pico não é lentidão, é indisponibilidade: as threads ficam
  presas e o serviço para de aceitar tráfego.

## Camada 2: transação e pool de conexões

A regra que resolve a maioria dos casos: **nenhuma chamada de rede, nenhum
upload e nenhuma espera externa dentro da fronteira transacional.** A conexão
de banco é o recurso mais escasso e mais caro do caminho, e ela fica retida
pelo tempo da transação inteira, não pelo tempo das queries.

Ver o cálculo em `volumetria.md` ("Dimensionamento de threads e conexões"):
o mesmo throughput exige 3,5 ou 210 conexões dependendo apenas do que está
dentro da transação.

O que verificar:

- `@Transactional` em método que também grava anexo, chama API ou publica em
  fila → a conexão paga por tudo isso.
- `@Transactional` na classe inteira ou em método muito acima na pilha,
  englobando bem mais do que precisa ser atômico.
- Métricas do Hikari: `hikaricp_connections_pending`,
  `hikaricp_connections_acquire_seconds`, `hikaricp_connections_usage_seconds`.
  Espera por conexão com CPU de banco baixa é assinatura de retenção indevida.
- `maximumPoolSize` maior do que o banco suporta: transfere a fila para o
  banco, onde é mais difícil de ver.
- Pool de threads do servidor (`server.tomcat.threads.max`) desalinhado da
  concorrência calculada — pequeno demais enfileira antes de entrar,
  grande demais deixa a aplicação aceitar mais do que consegue processar e
  transforma lentidão em timeout generalizado.

## Camada 3: memória e GC

Numa aplicação de ingestão com anexo, a memória escala com
`tamanho do anexo × concorrência`, e é isso que estoura no pico — não no
teste local com uma requisição.

- Anexo em heap: 3 imagens de 200 KB × 84 requisições em voo ≈ 50 MB só em
  buffers, e isso na melhor hipótese (sem cópia intermediária). Base64 na
  travessia aumenta o payload em ~33% e costuma dobrar a alocação por causa
  da conversão.
- Pedir: GC log (`-Xlog:gc*:file=...`), tempo em pausa por minuto, heap após
  full GC (é o número que diz se há vazamento ou só pressão de alocação).
- Heap após full GC estável e alto = trabalho legítimo, precisa de mais
  memória ou menos alocação. Crescente ao longo do tempo = vazamento.
- `limits.memory` do container precisa de folga sobre o heap (metaspace,
  thread stacks, buffers diretos, código nativo). Heap igual ao limite é
  `OOMKilled` esperando o pico.

## Camada 4: banco de dados

No caminho de ingestão, escrita domina. O que verificar:

- `EXPLAIN` das consultas do caminho crítico — inclusive as de validação
  ("essa passagem já existe?"), que são fáceis de esquecer e rodam em toda
  requisição.
- Índices que servem a escrita e a consulta operacional (tipicamente
  identificador de negócio + janela de tempo), sem exagerar:
  cada índice extra é custo em toda inserção.
- Inserção uma a uma vs em lote. Em ingestão de alto volume, lote muda a
  ordem de grandeza — mas exige que a durabilidade seja garantida antes
  (ver `arquitetura-ingestao.md`).
- Crescimento da tabela e particionamento por data — decisão que é barata
  antes e caríssima depois.
- Anexo em coluna de banco (`BLOB`/`bytea`): inviável neste volume. Custo de
  backup, de replicação e de cache do banco disparam.
- Escrita de ingestão competindo com leitura analítica na mesma instância.

## Camada 5: cluster e escala

- Réplicas e `requests` coerentes com o dimensionamento da Fase 1.
- `limits.cpu` baixo causa throttling que aparece como latência em degraus,
  não como CPU alta — engana o diagnóstico.
- HPA: por qual métrica? CPU não representa bem um serviço que espera I/O;
  RPS ou profundidade de fila representam.
- Escala horizontal exige aplicação sem estado local: sessão, cache em
  memória com significado e arquivo em disco local quebram a escala.
- `terminationGracePeriodSeconds` e shutdown graceful: sem isso, cada rolling
  update descarta as requisições em voo — em centenas de req/s, um deploy vira
  incidente.
- Teto do HPA que o cluster consegue alocar de fato.

## Idempotência: o bug que só aparece sob carga

Cliente automatizado que sofre timeout **reenvia**. Sob pico, timeout deixa
de ser raro. Sem chave de idempotência, o reenvio gera registro duplicado —
e quando o registro tem consequência jurídica (uma infração, uma cobrança),
o duplicado é um problema muito maior que a lentidão que o causou.

O que verificar: existe chave natural única (ex.: origem + timestamp +
identificador de negócio) com constraint no banco? O reenvio da mesma
requisição produz o mesmo resultado, ou produz um segundo registro? O
processamento assíncrono, se existir, também é idempotente — entrega
duplicada é comportamento normal de fila, não anomalia.

## Por stack: onde os mesmos problemas aparecem

Os problemas são os mesmos — conexão retida, alocação × concorrência,
trabalho síncrono desnecessário, ausência de timeout. Muda onde olhar.

| Stack | Pool de conexões / threads | Memória | Concorrência: o que trava tudo | O que pedir |
|---|---|---|---|---|
| **JVM** (Spring, Quarkus) | Hikari (`connections_pending`, `acquire_seconds`), `server.tomcat.threads.max` | heap vs `limits.memory` (metaspace, stacks, direct buffers ficam fora); `getBytes()` de anexo | `@Transactional` englobando I/O; `synchronized` em singleton; `parallelStream` no pool comum | GC log (`-Xlog:gc*`), heap dump no OOM, Actuator/Micrometer |
| **Node.js** | `pg`/`mysql2` pool por processo; **um** processo = um thread de evento | heap do V8 (`--max-old-space-size`) vs `limits`; buffers de upload em memória | qualquer trabalho CPU-bound (JSON grande, criptografia, compressão) bloqueia o event loop inteiro — latência de tudo sobe junto | event loop lag, `--heapsnapshot`; rodar em cluster/PM2 ou 1 processo por pod com mais réplicas |
| **.NET** | `SqlConnection` pool por string de conexão; ThreadPool | GC server vs workstation; `LOH` com arrays grandes | **sync-over-async** (`.Result`, `.Wait()`) esgotando o ThreadPool — thread pool starvation aparece como latência com CPU baixa | `dotnet-counters` (threadpool queue length, GC), `dotnet-trace` |
| **Python** (Django, FastAPI) | pool por **worker**: `workers × pool_size` conexões no banco; gunicorn/uvicorn workers × threads | RSS por worker × workers vs `limits` | GIL: CPU-bound serializa por processo; I/O síncrono em handler async trava o loop | `workers` coerente com CPU; `EXPLAIN`; profile com `py-spy` |
| **Go** | `database/sql` `SetMaxOpenConns` (default ilimitado!); goroutines baratas | `GOMEMLIMIT`; `GOMAXPROCS` ≠ cgroup limit sem `automaxprocs` (throttling) | goroutine leak (esperando canal que nunca fecha); `sync.Mutex` global | `pprof` (CPU, heap, goroutines), `runtime/metrics` |

Em todas: timeout explícito em todo cliente externo; teto em toda fila em
memória; probe de readiness que só libera após conexões e caches estarem
prontos; shutdown graceful que drena o que está em voo.

## O que pedir quando não há métrica nenhuma

Cenário comum e não bloqueante. Nesta ordem de custo/benefício:

1. **Actuator + Prometheus** já expõem o essencial no Spring Boot: latência
   por endpoint, métricas do Hikari, GC, threads. É a menor mudança com o
   maior retorno de informação.
2. **GC log** ligado — arquivo, sem custo relevante em produção.
3. **`EXPLAIN`** das consultas do caminho crítico, que não exige nada em
   produção.
4. **`kubectl top` e `describe`** para uso real vs requests e histórico de
   restart — somente leitura, seguindo `coleta-cluster.md`.
5. **Teste de carga de uma instância** para descobrir a capacidade por
   réplica — sem esse número, todo cálculo de réplica é hipótese.

Enquanto esses dados não existirem, entregue a análise com as conclusões
marcadas como hipótese e a instrumentação como o primeiro item do plano. Uma
análise honesta com lacunas declaradas é útil; uma análise que finge ter
medido, não.
