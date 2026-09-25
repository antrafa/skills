# Objetivos e Métodos

O workflow da skill é o mesmo para qualquer objetivo. O que muda é como o
alvo se escreve, o que costuma decidir o caso e a armadilha típica. Este
arquivo cobre isso e os métodos padrão de mercado que sustentam a análise.

## Índice
- [Os seis tipos de objetivo](#os-seis-tipos-de-objetivo)
- [Objetivos combinados](#objetivos-combinados)
- [Medir o estado atual quando não há métrica](#medir-o-estado-atual-quando-não-há-métrica)
- [Métodos padrão](#métodos-padrão)
  - USE · RED · Little's Law · Joelho de utilização · Lei de Escalabilidade Universal · Percentis · Testes de carga · Margem · SLO
- [Quando uma tecnologia nova se justifica](#quando-uma-tecnologia-nova-se-justifica)

## Os seis tipos de objetivo

### 1. Escalar para volume X

- **Alvo:** req/s de pico de projeto, p95 aceitável, tolerância a perda,
  janela de "consultável". Ex.: "400 req/s de pico, p95 < 300 ms, perda zero".
- **O que decide:** o que satura primeiro no pico; o que está dentro da
  fronteira transacional; storage acumulado por retenção; se o gargalo é
  compartilhado entre réplicas (banco, storage, lock, gerador de ID).
- **Armadilha:** dimensionar pela média, ou tratar o volume diário como carga
  instantânea. E confundir pico horário com rajada (ver `volumetria.md`).
- **Padrões:** `arquitetura-ingestao.md` para escrita; `padroes-por-objetivo.md`
  para leitura.

### 2. Reduzir latência

- **Alvo:** p95 (e p99, se houver SLO de cauda) por endpoint ou por jornada,
  em ms, **a um volume declarado** — latência sem volume não é alvo.
- **O que decide:** breakdown por etapa (sem ele, otimiza-se o que responde
  por 3% do tempo); trabalho síncrono que poderia não estar na resposta;
  chamadas em série que poderiam ser paralelas; N+1; espera externa sem
  timeout; serialização/desserialização de payload grande.
- **Armadilha:** otimizar código antes de ter o breakdown. E olhar a média:
  p50 ótimo com p99 ruim é o caso mais comum, e o usuário sente o p99.
- **Padrões:** `padroes-por-objetivo.md` § latência.

### 3. Reduzir custo / right-sizing

- **Alvo:** R$ ou recursos (vCPU, GiB, nós) por mês, **com SLO mantido** —
  escreva o SLO ao lado do alvo de custo, senão o corte vai ser cobrado como
  incidente três semanas depois.
- **O que decide:** `requests` vs uso real p95 (não média); réplicas com
  utilização baixa e constante; heap/`limits` desalinhados; HPA com `min`
  alto demais; storage e retenção de log/métrica; ambientes não produtivos
  ligados 24 h; instâncias reservadas vs sob demanda.
- **Armadilha:** cortar `requests` abaixo do p95 de uso — não economiza,
  troca custo por throttling/OOM. Cortar réplica em serviço que já não tem
  N+1. E medir "antes" só na hora mais calma do dia.
- **Padrões:** `padroes-por-objetivo.md` § custo.

### 4. Estabilidade sob carga

- **Alvo:** zero `OOMKilled`/restart no pico; taxa de erro < x%; nenhum
  timeout de cliente com servidor "saudável"; deploy sem erro.
- **O que decide:** memória = alocação por request × concorrência (estoura
  no pico, não no teste local); ausência de timeout em cliente externo;
  pools e filas em memória sem teto; probes ausentes ou agressivas; shutdown
  não graceful; retry sem jitter derrubando a dependência.
- **Armadilha:** subir o limite de memória como solução — trata o sintoma; a
  alocação escala com a concorrência e sempre existe uma rajada maior.
- **Padrões:** `padroes-por-objetivo.md` § resiliência.

### 5. Janela de batch / job

- **Alvo:** "terminar antes das 6h" vira `registros/s necessários = volume ÷
  segundos da janela`, com margem para o volume do ano que vem.
- **O que decide:** se o job é paralelizável por partição (data, cliente,
  faixa de ID); tamanho do lote e frequência de commit; índices que servem a
  leitura do job e atrapalham a escrita; competição com OLTP na mesma
  instância; se é reiniciável (checkpoint idempotente).
- **Armadilha:** paralelizar sem partição (todos os workers disputando as
  mesmas linhas), e "otimizar a query" sem `EXPLAIN` do plano com o volume
  real.
- **Padrões:** `padroes-por-objetivo.md` § batch.

### 6. Leitura intensiva

- **Alvo:** p95 da página ou consulta **no pico de acesso** (publicação,
  abertura de inscrição, fechamento de mês), não na média do dia.
- **O que decide:** `EXPLAIN` das consultas das páginas pesadas; com que
  frequência o dado muda (define a cacheabilidade); paginação do que hoje
  carrega tudo; N+1; réplica de leitura; busca textual com índice adequado.
- **Armadilha:** aplicar padrões de ingestão (fila, processamento
  assíncrono, idempotência) num sistema onde ninguém escreve. E cache antes
  do `EXPLAIN`: cache esconde a query ruim até o primeiro miss em massa.
- **Padrões:** `padroes-por-objetivo.md` § leitura.

## Objetivos combinados

"Escalar 10x sem aumentar o custo mais que 2x", "reduzir latência sem mexer
no banco", "cortar custo sem tocar em código". Sempre há um **primário** —
o que define o veredito (aguenta / não aguenta / atingiu / não atingiu) — e
**restrições**, que toda proposta precisa respeitar e que aparecem na tabela
de custos e nos ADRs como alternativa descartada ("descartada porque viola a
restrição X").

Escreva explicitamente qual é qual. Quando o usuário não souber, proponha:
o primário é o que dói hoje; o resto é restrição.

## Medir o estado atual quando não há métrica

Cenário comum e não bloqueante. O volume atual pode quase sempre ser medido
com o que já existe, e **volume medido vale mais que volume declarado**:

| Fonte | O que dá | Como |
|---|---|---|
| Log da aplicação (1 linha por evento) | volume por hora, hora mais cheia, rajada por segundo | contar linhas por hora (`cut` no timestamp + `sort \| uniq -c`); para rajada, contar por segundo no minuto mais cheio |
| Access log do gateway / ingress / Istio | RPS real por endpoint, status, latência | mesmo procedimento; costuma ter latência por request |
| Banco | volume por dia/hora histórico, tamanho das tabelas, crescimento | `COUNT(*) GROUP BY` data de criação; visões de catálogo para tamanho |
| Broker (RabbitMQ, SQS, Kafka) | taxa de publicação e consumo, profundidade de fila, idade da mensagem mais antiga | console/API de gestão; é a melhor fonte para o consumidor |
| `kubectl top` / `describe` | uso real de CPU e memória, restarts e motivo | ver `coleta-cluster.md`; colete no pico |
| Fatura / console da nuvem | custo atual por serviço, por ambiente | baseline obrigatório para objetivo de custo |

Registre no inventário de evidências como o número foi obtido (comando,
janela de tempo) e o que faltou na janela (horas sem log, dia atípico).
Interpolação de horas faltantes é aceitável se declarada como premissa.

## Métodos padrão

### USE — por recurso

Para **cada recurso** do caminho (CPU, memória, pool de conexões de banco,
pool de threads, disco/IO, rede, fila, storage externo), responda três
perguntas: **U**tilização (quanto está em uso), **S**aturação (quanto está
esperando na fila do recurso), **E**rros. Um recurso pode estar em 40% de
utilização e saturado (fila de espera por conexão com CPU do banco baixa é o
exemplo clássico). A tabela sintoma → causa de `diagnostico.md` é USE
aplicado.

### RED — por serviço

Para **cada serviço**: **R**ate (req/s), **E**rrors (taxa de erro),
**D**uration (latência em percentis). São os "golden signals" mínimos; sem
eles não há SLO possível. Quando não existem, o primeiro item do plano é
expô-los (Actuator/Prometheus, OpenTelemetry, ou o equivalente da stack).

### Little's Law

```
concorrência = throughput × tempo de residência
```

Vale para requisições em voo, conexões retidas, mensagens em processamento.
É o que converte req/s em threads, conexões e réplicas. Detalhes e exemplo em
`volumetria.md`.

### Joelho de utilização

Num recurso compartilhado com chegadas aleatórias, o tempo de espera na fila
cresce aproximadamente com `utilização / (1 − utilização)`, em múltiplos do
tempo de serviço. A 50% de utilização a espera é
igual ao tempo de serviço; a 80% é 4x; a 90% é 9x. **Acima de ~70–80% de
utilização sustentada, a latência deixa de ser previsível.** Consequências:

- "CPU a 85% está ótimo, sobra 15%" está errado para latência — sobra
  capacidade, não sobra previsibilidade.
- Dimensione recurso compartilhado (banco, pool, storage) para ficar abaixo
  do joelho no pico, não em 100%.
- Pool de conexões maior que a capacidade do banco só move a fila para dentro
  do banco, onde é mais cara de ver.

### Lei de Escalabilidade Universal (por que réplica para de ajudar)

Throughput não cresce linearmente com réplicas por duas razões:
**contenção** (parte serial: lock, linha de controle de ID, tabela
compartilhada, storage único) e **coerência** (custo de manter estado
consistente entre instâncias: cache distribuído, sessão replicada). A
partir de certo ponto, réplica a mais **reduz** throughput.

Diagnóstico prático: meça throughput com 1, 2 e 4 réplicas. Se não dobra ao
dobrar, o gargalo é compartilhado — e está fora da aplicação. Adicionar
réplica só distribui a espera. É a medição que decide entre "escalar" e
"remover a contenção".

### Percentis, não médias

Média esconde a cauda, e o usuário sente a cauda. Sempre p50, p95, p99 —
e a **taxa** junto, porque p99 de 3 req/s não significa nada.

**Amplificação de cauda:** se uma jornada toca N serviços e cada um tem 1%
de respostas lentas, a probabilidade de a jornada ser lenta é
`1 − 0,99^N`: com 10 chamadas, ~10%. Em fan-out, o p99 de cada dependência
vira o p90 do agregado. É o argumento numérico contra colocar chamadas em
série no caminho crítico.

### Tipos de teste de carga e o que cada um responde

| Teste | Pergunta que responde | Quando |
|---|---|---|
| Smoke | o ambiente de teste funciona com carga mínima? | antes de qualquer outro |
| **Carga em 1 réplica** | **capacidade por réplica** — o número sem o qual o cálculo de réplicas é chute | primeiro teste de verdade |
| Carga (load) | no volume de projeto, o SLO se mantém? | valida o dimensionamento |
| Stress | onde quebra, e como (graciosamente ou perdendo dado)? | descobre o teto e o modo de falha |
| Soak (endurance) | em horas no volume de projeto, há vazamento, crescimento de heap, degradação? | antes de ligar em produção |
| Spike | a rajada é absorvida (fila/buffer) ou derruba? | quando o fator de rajada é alto |

A skill **não roda** teste de carga; ela diz qual teste falta, o que ele
precisa medir, e o coloca como item do plano. Recomende ferramenta só se o
time não tiver uma (k6, Gatling, JMeter, Locust são todas adequadas; a
escolha é do time).

### Margem (headroom)

- Dimensionar para o **pico de projeto × margem**: 1,3–2x conforme a
  tolerância a perda (2x para ingestão que não pode perder dado).
- **N+1** réplicas: sobreviver a rolling update e à queda de um nó.
- Teto do HPA que o cluster consegue **alocar de fato** (`Pending` não
  escala).
- Recurso compartilhado abaixo do joelho de utilização no pico.

### SLO: o alvo tem que ser um

SLI é a medida (p95 de latência do endpoint X). SLO é o alvo sobre a medida
(p95 < 300 ms em 99% dos minutos do mês). Sem SLO, "performance boa" é
opinião e "cortar custo sem degradar" não é verificável. Quando o usuário
não tiver SLO, proponha um a partir do que o negócio tolera, marque como
premissa e coloque a medição do SLI como primeiro item do plano.

## Quando uma tecnologia nova se justifica

Cada tecnologia entra acompanhada do **número que a exige** e do **custo
operacional que traz**. Regras rápidas, com a alternativa proporcional:

| Tecnologia | O número que a justifica | Se o número não sustenta |
|---|---|---|
| Fila/broker (quando não há) | pico ≫ média e processamento amortizável; produtor e consumidor com perfis de carga diferentes; falha do processamento não pode rejeitar o produtor | estado `pendente` no próprio banco com `SKIP LOCKED` |
| Kafka especificamente | replay do histórico ou múltiplos consumidores independentes do mesmo evento | fila simples (RabbitMQ/SQS): centenas ou milhares de msg/s não pedem Kafka |
| Cache distribuído | leitura repetida do mesmo dado com hit ratio previsível > 80% e freshness tolerável; ou estado compartilhado entre réplicas | cache local por réplica; ou só o índice que faltava |
| Réplica de leitura | leitura pesada competindo com escrita na mesma instância, visível no p95 de escrita | índice + paginação + cache |
| Object storage | anexo binário em volume relevante (praticamente sempre) | — (é o padrão, não a exceção) |
| Particionamento | tabela que cresce sem teto e descarte por retenção | — (barato antes, caríssimo depois) |
| Outro banco (NoSQL) | modelo de dados ou garantia diferente exigidos pelo caso; **nunca** velocidade | particionar e indexar o relacional |
| Outra linguagem | CPU-bound comprovado por profile no caminho crítico, depois de eliminado o I/O | medir o breakdown; o gargalo em serviço web é I/O em 9 de 10 casos, e a reescrita descarta regra de negócio já validada sem tocar a causa |
| Microserviços | perfis de carga ou ciclos de deploy genuinamente distintos | separar só o que tem perfil diferente (tipicamente ingestão vs processamento) |
| Serverless | tráfego esporádico com longos períodos ociosos | escala horizontal com HPA |
