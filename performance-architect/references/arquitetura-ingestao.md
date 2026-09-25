# Arquitetura para Ingestão de Alto Volume

Cada padrão aqui vem com **o número que o justifica** e **o custo que traz**.
Padrão adotado sem o número é moda; adotado sem o custo é dívida.

## Índice
- [A pergunta que vem antes de tudo](#a-pergunta-que-vem-antes-de-tudo)
- [Padrão 1: separar ingestão de processamento](#padrão-1-separar-ingestão-de-processamento)
- [Padrão 2: anexo fora do banco e fora da memória](#padrão-2-anexo-fora-do-banco-e-fora-da-memória)
- [Padrão 3: durabilidade da ingestão](#padrão-3-durabilidade-da-ingestão)
- [Padrão 4: idempotência](#padrão-4-idempotência)
- [Padrão 5: backpressure e degradação](#padrão-5-backpressure-e-degradação)
- [Padrão 6: banco dimensionado para escrita](#padrão-6-banco-dimensionado-para-escrita)
- [Padrão 7: escala horizontal de verdade](#padrão-7-escala-horizontal-de-verdade)
- [Anti-padrões a recusar](#anti-padrões-a-recusar)
- [Ordem de adoção](#ordem-de-adoção)

## A pergunta que vem antes de tudo

**O que exatamente precisa estar pronto antes de responder ao cliente?**

Quase toda premissa de "tempo real" se decompõe em duas coisas com custos
muito diferentes:

- **Ingerido e consultável** — o dado existe, é durável e alguém consegue
  achá-lo. Isso costuma ser o requisito real quando a justificativa é
  "um órgão pode pedir esse dado a qualquer momento".
- **Processado** — a regra de negócio rodou, o dado foi classificado,
  enriquecido, transformado em outro registro (uma infração, uma cobrança,
  um alerta).

Se o requisito real é o primeiro, o segundo pode ser assíncrono, e essa
separação é normalmente a mudança de arquitetura com maior efeito e menor
custo num serviço de ingestão. Se o requisito real é o segundo — existe
alguém agindo em segundos sobre o resultado processado — então o requisito é
legítimo e a arquitetura precisa pagar por ele; nesse caso o caminho é
processamento assíncrono com latência baixa e monitorada, não processamento
síncrono.

Faça essa pergunta com o dono do requisito, não deduza. E registre a resposta
como ADR: é a decisão de que todas as outras dependem.

## Padrão 1: separar ingestão de processamento

**Fluxo:** validar o mínimo que impede dado inválido de entrar → persistir o
bruto de forma durável → responder → processar a regra de negócio em
consumidor separado.

**Justifica quando:** o tempo de resposta está preso ao trabalho mais lento do
caminho; ou o processamento tem custo/variância maior que a ingestão; ou o
pico de ingestão é muito maior que a média e o processamento pode ser
amortizado ao longo do dia (é o caso de tráfego com pico diurno: o
consumidor dimensionado um pouco acima da média acumula fila durante o pico
e drena fora dele — o atraso é da ordem da duração do pico, e precisa caber
no SLO de processamento; conta de exemplo em `volumetria.md`).

**Ganhos:** tempo de resposta desacoplado da regra de negócio; pico absorvido
sem escalar tudo; falha no processamento não perde o dado nem rejeita o
cliente; regra de negócio pode ser reprocessada.

**Custos:** duas coisas para operar e monitorar; latência de processamento
passa a ser um SLO explícito (com alerta de atraso); estado intermediário
("recebido, não processado") passa a existir e precisa aparecer para quem
consulta; reprocessamento precisa ser idempotente.

**Cuidado:** responder `202 Accepted` só é honesto se o dado já estiver
durável. Responder antes de persistir troca lentidão por perda silenciosa de
dado — que é pior, especialmente com tolerância zero a perda.

## Padrão 2: anexo fora do banco e fora da memória

**Fluxo:** anexo vai por streaming direto para object storage (S3, MinIO,
compatível); o registro no banco guarda a chave, o tamanho e o hash.

**Justifica quando:** há anexo binário e volume relevante — praticamente
sempre. Com milhões de objetos por dia, `BLOB` em banco relacional é inviável (backup,
replicação e cache do banco disparam), e `byte[]` em heap estoura no pico
(ver `diagnostico.md`, camada 3).

**Ganhos:** heap constante independente do tamanho do anexo; storage escala e
custa por camada (quente/frio); backup do banco volta a ser viável;
retenção do anexo fica independente da retenção do registro.

**Custos:** dois sistemas para manter consistentes — órfãos acontecem
(objeto sem registro, registro sem objeto), e precisam de uma rotina de
reconciliação; storage passa a ser dependência de disponibilidade da
ingestão.

**Variante que vale perguntar:** o cliente consegue enviar o anexo direto ao
storage por URL pré-assinada, mandando à aplicação só o metadado? Se sim, o
tráfego de anexo deixa de passar pela aplicação — o maior ganho possível
neste padrão. Depende do cliente — equipamento embarcado ou integração
legada nem sempre suporta —, então é pergunta, não premissa.

## Padrão 3: durabilidade da ingestão

Duas opções, e a escolha depende do que já existe e da tolerância a perda:

**A) Escrita direta no banco, processamento lido de lá.** O registro entra com
estado `pendente`; um worker consulta e processa. Sem componente novo.
Justifica-se quando o banco aguenta a taxa de escrita da ingestão com folga
(faça a conta: centenas de escritas/s de linha pequena são confortáveis para um
relacional bem dimensionado) e o time não tem operação de fila. Custo:
consulta de polling no mesmo banco que recebe a escrita; precisa de índice
adequado no estado e de cuidado com concorrência entre workers
(`SELECT ... FOR UPDATE SKIP LOCKED` resolve).

**B) Fila/log durável (RabbitMQ, SQS, Kafka).** Ingestão publica; consumidores
processam. Justifica-se quando a taxa de escrita ameaça o banco, quando há
vários consumidores independentes do mesmo evento, ou quando é preciso
reprocessar histórico. Custo: componente novo para operar, monitorar e
dimensionar; DLQ e política de retry para desenhar; entrega duplicada como
comportamento normal (ver Padrão 4).

**Kafka especificamente** só se justifica por retenção e releitura do log,
ou por múltiplos consumidores independentes com necessidade de replay — não
por throughput na faixa de centenas de msg/s, que uma fila simples atende
sem esforço. Se a razão declarada para Kafka é throughput, o número não
sustenta a escolha.

## Padrão 4: idempotência

**Fluxo:** definir a chave natural do evento (ex.: origem + timestamp +
identificador de negócio), aplicar constraint única no banco, tratar a violação
como sucesso ("já registrado") em vez de erro.

**Justifica quando:** existe cliente automatizado que reenvia em timeout —
assuma que sim até prova em contrário. E sempre, se houver fila: entrega
duplicada ("at least once") é o comportamento padrão, não a exceção.

**Ganhos:** reenvio deixa de ser problema; retry seguro; reprocessamento
seguro.

**Custos:** exige acordo sobre o que é "o mesmo evento" (nem sempre óbvio —
timestamp com granularidade errada quebra a chave nos dois sentidos); índice
único a mais.

**O que isso protege de fato:** registro duplicado que virou consequência
jurídica — infração dobrada, cobrança dobrada. É a categoria de defeito que
custa mais caro do que qualquer problema de latência, e ela nasce
justamente sob a carga que se está tentando resolver.

## Padrão 5: backpressure e degradação

Decida **antes** o que o sistema faz quando não consegue acompanhar:

- Consumidor atrasado, ingestão saudável → aceitar e acumular, com alerta de
  profundidade de fila e de idade da mensagem mais antiga. Precisa de teto:
  acúmulo sem limite vira storage cheio e depois indisponibilidade.
- Ingestão saturada → rejeitar explicitamente com `429`/`503` e `Retry-After`
  é melhor que aceitar e perder. Cliente automatizado sabe reenviar; dado
  aceito e descartado ninguém recupera.
- Storage indisponível → o dado precisa ir para onde? Falhar a requisição e
  deixar o cliente reenviar é resposta legítima e simples, desde que o
  cliente reenvie de fato.

O que **nunca** fazer: aceitar silenciosamente o que não se consegue
processar. É o modo de falha mais difícil de detectar, porque todos os painéis
ficam verdes enquanto o dado se perde.

## Padrão 6: banco dimensionado para escrita

- **Particionamento por data** na tabela de eventos: mantém índices em tamanho
  utilizável, torna o descarte por retenção uma operação de metadado
  (`DROP PARTITION` em vez de `DELETE` de milhões de linhas) e mantém as
  consultas por janela de tempo eficientes. Barato de decidir antes, caro
  depois — se o volume justifica particionar em algum momento, o momento é
  agora.
- **Índices para as consultas reais**, não para todas as consultas
  imagináveis: identificador de negócio + janela de tempo costuma cobrir o
  caso operacional. Cada índice extra é custo em toda inserção.
- **Inserção em lote** no consumidor, quando a durabilidade já está garantida
  antes. Muda a ordem de grandeza da escrita. Não use na ingestão síncrona:
  esperar o lote encher é latência e é risco de perda.
- **Separar leitura analítica da escrita de ingestão** (réplica de leitura)
  quando houver consulta pesada — relatório varrendo o histórico não pode
  competir com a escrita da ingestão.
- **Retenção e arquivamento** definidos junto do negócio e do jurídico. Sem
  política de retenção, o sistema tem prazo de validade.

## Padrão 7: escala horizontal de verdade

Escalar só funciona se a aplicação não tiver estado local e o gargalo não for
compartilhado. Verifique: sem sessão em memória, sem cache com significado
funcional, sem arquivo em disco local, sem agendamento que não tolere rodar em
várias instâncias (aí precisa de lock ou de instância dedicada).

Depois: HPA por métrica que represente o trabalho (RPS ou profundidade de
fila; CPU engana em serviço que espera I/O), shutdown graceful com drain do
que está em voo, PDB para não perder réplicas demais numa manutenção de nó, e
teto de HPA que o cluster consiga alocar.

**Se o throughput não cresce ao adicionar réplica, o gargalo é compartilhado**
(banco, storage, lock) — e adicionar réplica só distribui a espera. Meça
throughput por réplica antes de escalar.

## Anti-padrões a recusar

Recuse em uma linha, com o número, e ofereça a alternativa proporcional. Sem
sermão. Reescrita em outra linguagem, Kafka, microserviços, NoSQL e
serverless seguem a tabela única em `objetivos-e-metodos.md` ("Quando uma
tecnologia nova se justifica"); abaixo, só o que é específico de ingestão.

| Proposta | Por que recusar | Alternativa |
|---|---|---|
| Cache para resolver lentidão de escrita | cache resolve leitura repetida; o problema de ingestão é escrita | dimensionar escrita: lote, particionamento, índice certo |
| Aumentar o pool de conexões | pool é onde o problema aparece, não onde está | descobrir o que retém a conexão (quase sempre I/O dentro da transação) |
| Aumentar o pool de threads para "aceitar mais" | aceitar mais do que se processa transforma lentidão em timeout generalizado | backpressure explícito + escala horizontal |
| Tuning de GC como primeira ação | GC costuma ser sintoma de alocação excessiva (anexo em heap) | eliminar a alocação; só depois ajustar GC, com GC log em mãos |

## Ordem de adoção

Não adote tudo. Ordem por relação ganho/risco, para um serviço de ingestão
típico:

1. Tirar I/O de dentro da transação (Padrão 2 parcial) — ganho grande, risco
   baixo, mudança pequena.
2. Anexo por streaming para object storage (Padrão 2) — resolve heap e
   storage de uma vez.
3. Idempotência por chave natural (Padrão 4) — barato, e evita a classe de
   defeito mais caro.
4. Separar ingestão de processamento (Padrão 1 + 3) — o maior ganho de
   arquitetura, e o de maior custo operacional.
5. Particionamento e índices (Padrão 6) — antes de a tabela crescer.
6. Backpressure explícito (Padrão 5) e escala horizontal (Padrão 7).

Os três primeiros costumam ser suficientes para uma ordem de grandeza de
folga. Só vá adiante se o número da Fase 1 exigir.
