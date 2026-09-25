Terminei a análise do incidente de ontem, quando a API de pedidos ficou fora do ar das 9h05 às 9h47. Segue o que encontrei, a causa raiz e as ações sugeridas.

## Linha do tempo

- **8h58:** a pipeline iniciou o deploy da versão 4.12 em produção, disparado manualmente pelo plantonista.
- **9h01:** o job de migração do Flyway começou a rodar a migração `V87__add_index_pedidos_status.sql`.
- **9h03:** os novos pods subiram e passaram no readiness probe.
- **9h05:** os alertas de erro 5xx dispararam. O p99 de latência passou de 30 s.
- **9h12:** o plantonista tentou rollback pela pipeline, mas o job falhou porque a migração ainda estava em andamento.
- **9h40:** a migração terminou.
- **9h47:** a API voltou a responder normalmente, sem nenhuma ação adicional.

## O que os dados mostram

Olhando as métricas do banco no intervalo, a tabela `pedidos` ficou com um lock exclusivo das 9h01 às 9h40. A migração V87 cria um índice com `CREATE INDEX` comum, sem `CONCURRENTLY`, e a tabela tem 38 milhões de linhas.

Durante esse período, todas as consultas que tocavam `pedidos` ficaram esperando o lock. As conexões do pool foram sendo ocupadas por essas consultas presas e, às 9h06, o pool de 20 conexões de cada pod estava esgotado. A partir daí até as rotas que não usam `pedidos` passaram a falhar, porque não havia conexão livre.

O tráfego no horário estava normal para uma segunda-feira, cerca de 15% acima da média da semana, sem nenhum pico fora do padrão.

## Causa raiz

A causa raiz do incidente foi o tamanho do pool de conexões. Com apenas 20 conexões por pod, o pool esgotou rapidamente e derrubou todas as rotas. Se o pool fosse maior, a API teria absorvido a lentidão sem sair do ar.

## Fatores que contribuíram

### Processo

- O deploy foi feito às 9h, no horário de maior uso, porque não existe janela de deploy definida para a API de pedidos.
- A migração não passou por revisão de DBA. O checklist de MR não pede revisão para migrações.

### Tecnologia

- O rollback da pipeline depende de a migração terminar, então não havia como voltar a versão durante o lock.
- A migração não foi testada num banco com volume próximo ao de produção. Em homologação a tabela tem 200 mil linhas e o índice ficou pronto em 2 segundos.

### Pessoas

- O plantonista não sabia que a migração criava índice numa tabela grande, porque a descrição do MR só dizia "ajuste de performance".

### Ambiente

- Homologação não reflete o volume de produção, como dito acima.

## Ações sugeridas

1. Aumentar o pool de conexões de 20 para 60 por pod. Essa é a ação principal e resolve a causa raiz.
2. Definir uma janela de deploy fora do horário comercial para a API de pedidos.
3. Incluir no checklist de MR a revisão de DBA para qualquer migração.
4. Criar um job de restauração parcial da base de produção em homologação, para testar migrações com volume real.

Posso abrir as issues dessas quatro ações, começando pelo aumento do pool, que é a mais rápida de aplicar.
