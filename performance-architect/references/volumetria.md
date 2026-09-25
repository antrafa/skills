# Volumetria e Dimensionamento

## Índice
- [Roteiro de levantamento](#roteiro-de-levantamento)
- [Volume de negócio → req/s](#volume-de-negócio--reqs)
- [Fator de pico](#fator-de-pico)
- [Volume de dados e storage](#volume-de-dados-e-storage)
- [Dimensionamento de threads e conexões](#dimensionamento-de-threads-e-conexões)
- [Quando o objetivo não é volume](#quando-o-objetivo-não-é-volume)
- [Réplicas e margem](#réplicas-e-margem)
- [Exemplo trabalhado: ingestão de radares](#exemplo-trabalhado-ingestão-de-radares)

## Roteiro de levantamento

Todas as perguntas são puláveis. Quando o usuário não souber, **assuma um
default, declare o default no relatório e marque como premissa** — nunca
trave a análise esperando um número que ninguém tem. Uma premissa marcada é
revisável; um número inventado sem etiqueta é dívida.

| # | Pergunta | Default se não souber |
|---|---|---|
| 1 | Volume total por dia (hoje e no alvo) | usar o alvo declarado, sem crescimento adicional |
| 2 | Como o volume se distribui nas 24h? | pico diurno concentrado: fator 6x sobre a média |
| 3 | Tamanho médio do payload (sem anexos) | 2 KB de JSON |
| 4 | Quantidade e tamanho médio dos anexos/imagens | assumir o máximo declarado; 200 KB por imagem |
| 5 | Retenção legal do dado e do anexo | 5 anos para o registro, questionar se o anexo precisa do mesmo prazo |
| 6 | Tempo de resposta aceitável na ingestão | 200 ms p95 |
| 7 | O que acontece se uma requisição for perdida? | tolerância zero (é o caso mais caro; se houver tolerância, ela simplifica muito a arquitetura) |
| 8 | Qual a janela real de "quase tempo real"? | segundos para o dado ficar consultável |
| 9 | Crescimento esperado em 2 anos | +30% |
| 10 | Existe reenvio automático do cliente em timeout? | sim — assumir que existe até prova em contrário (define a necessidade de idempotência) |

A pergunta 7 e a 8 são as que mais mudam a arquitetura. A 10 é a que mais
gera bug em produção quando ninguém pergunta.

## Volume de negócio → req/s

```
req/s médio = volume por dia ÷ 86.400
```

Este número serve para uma coisa só: dar escala ao problema. **Nunca
dimensione pela média** — o sistema não é dimensionado para o dia, é
dimensionado para a pior hora do dia.

## Fator de pico

```
req/s de projeto = req/s médio × fator de pico
```

| Distribuição | Fator | Quando aplicar |
|---|---|---|
| Uniforme 24h | 1,5x | processo automatizado sem ritmo humano (batch, telemetria constante) |
| Horário comercial (8h úteis) | 3x | uso humano em expediente |
| Pico diurno concentrado | 6x | tráfego que segue o movimento das pessoas — trânsito, varejo, atendimento. Conservador: equivale a ~25% do volume do dia na hora de pico |
| Evento concentrado | 20x+ | bilheteria, matrícula, Black Friday |

Prefira o fator medido ao fator da tabela: se existe métrica de requisições
por minuto, o fator real é `pico_medido ÷ média_medida`, e ele vale mais que
qualquer estimativa. A tabela é para quando não há métrica — e nesse caso o
fator entra no relatório como premissa.

Dimensione com margem sobre o pico de projeto (2x é razoável para ingestão
que não pode perder dado), porque o pico do pico não avisa.

### Pico horário ≠ rajada

São dois fatores diferentes, e confundi-los erra em uma ordem de grandeza:

```
fator de pico horário = hora mais cheia ÷ média horária        (ex.: 1,6x)
fator de rajada       = segundo mais cheio ÷ média da hora     (ex.: 30x)
```

O **pico horário** se absorve com réplica: é carga sustentada. A **rajada**
se absorve com fila ou buffer: dura segundos, e escalar por CPU não reage a
tempo. Clientes automatizados (equipamentos, integrações, jobs de terceiros)
costumam acumular e despejar em lote — rajada alta com pico horário baixo é
o perfil típico. Meça os dois quando houver log com timestamp por evento
(`objetivos-e-metodos.md`, "Medir o estado atual"); ao escalar o volume,
a rajada **não** escala linearmente — mais fontes se dessincronizam e o
agregado suaviza. Modele um piso (Poisson: `média + 3√média`) e um teto
(rajadas correlacionadas) e declare o que adotou como premissa.

## Volume de dados e storage

```
objetos/dia   = req/dia × anexos por requisição
storage/dia   = objetos/dia × tamanho médio do anexo
storage total = storage/dia × dias de retenção
```

Faça esta conta **antes** de qualquer discussão de código. Em sistemas de
ingestão com anexo (imagem, áudio, documento), o storage é o item que decide
a viabilidade do projeto muito antes de qualquer gargalo de CPU — e é o único
número que cresce mesmo quando o sistema está funcionando perfeitamente.

Se o resultado for grande, o assunto vira **retenção em camadas**, não
otimização de código: quanto tempo o anexo fica em acesso imediato, quando
migra para armazenamento frio, quando é descartado. Isso é decisão jurídica e
de negócio, não técnica — leve o número para quem decide.

Some também o crescimento do banco: `req/dia × tamanho da linha × retenção`,
mais índices (estime 30-50% sobre os dados para tabela com poucos índices).

## Dimensionamento de threads e conexões

Little's Law:

```
concorrência necessária = throughput (req/s) × tempo de resposta (s)
```

Ex.: 700 req/s a 200 ms → 140 requisições em voo simultâneas. Este é o número
que o pool de threads do servidor precisa suportar no agregado de todas as
réplicas.

Para o **pool de conexões de banco**, o que conta não é o tempo total da
requisição, é o tempo em que a conexão fica retida:

```
conexões necessárias = throughput × tempo com a conexão na mão
```

Ex.: 700 req/s retendo conexão por 5 ms → 3,5 conexões. As mesmas 700 req/s
retendo conexão por 300 ms (porque a transação envolve o upload do anexo) →
210 conexões, que nenhum banco entrega confortavelmente. **É o mesmo
throughput.** A diferença é só o que está dentro da transação — e é por isso
que "aumentar o pool" quase nunca é a resposta certa: o pool é onde o problema
aparece, não onde ele está.

Pool grande demais também custa: cada conexão consome memória e concorrência
no banco. Pool maior que a capacidade real do banco só transfere a fila de
dentro da aplicação para dentro do banco, onde ela é mais caro de diagnosticar.

## Quando o objetivo não é volume

A mesma aritmética serve com outra entrada:

- **Batch:** `registros/s necessários = volume ÷ segundos da janela`, com o
  volume do ano que vem; compare com registros/s medidos hoje.
- **Custo:** `custo por 1.000 requisições = custo mensal ÷ (req/mês ÷ 1.000)`
  — é o número que compara alternativas e mostra se escalar é linear.
- **Latência:** orçamento por etapa — o p95 alvo dividido entre as etapas
  do caminho crítico, para saber quanto cada dependência pode consumir.

Detalhes por objetivo em `objetivos-e-metodos.md`.

## Réplicas e margem

```
réplicas = ceil(req/s de projeto ÷ capacidade medida por réplica) + margem
```

`capacidade medida por réplica` precisa vir de teste de carga ou de métrica de
produção. Sem esse número, o cálculo de réplicas é chute — declare como
hipótese e diga que a medição pendente é um teste de carga de uma instância.

Margem: pelo menos +1 réplica para sobreviver a rolling update e à queda de um
nó, e HPA configurado com teto que o cluster consiga realmente alocar (HPA que
pede réplica que não cabe no cluster não escala, só acumula pod `Pending`).

## Exemplo trabalhado: ingestão de radares

Alvo declarado: 6 milhões de requisições/dia, payload + até 3 imagens,
distribuição com pico diurno, dado precisa ficar consultável em segundos.

```
req/s médio      = 6.000.000 ÷ 86.400        ≈ 70 req/s
req/s de projeto = 70 × 6 (pico diurno)      ≈ 420 req/s
com margem 2x                                 ≈ 840 req/s de dimensionamento

objetos/dia   = 6.000.000 × 3                = 18.000.000 imagens/dia
storage/dia   = 18.000.000 × 200 KB          ≈ 3,4 TB/dia
storage/ano                                   ≈ 1,2 PB/ano

concorrência a 200 ms = 420 × 0,2            ≈ 84 requisições em voo
conexões, transação de 5 ms = 420 × 0,005    ≈ 2 conexões
conexões, transação de 300 ms = 420 × 0,3    ≈ 126 conexões
```

Leitura destes números:

- **420 req/s não é um problema de linguagem.** Um Spring Boot bem
  configurado atende isso com poucas réplicas. Quem propõe reescrita neste
  patamar está resolvendo o problema errado.
- **3,4 TB/dia é o problema real.** É a linha que domina o custo, e ela é
  decidida por retenção — não por código.
- **A diferença entre 2 e 126 conexões é só o conteúdo da transação.** Este é
  o gargalo mais provável de um serviço de ingestão com anexo, e ele se
  resolve tirando o I/O de dentro da transação, não aumentando o pool.
