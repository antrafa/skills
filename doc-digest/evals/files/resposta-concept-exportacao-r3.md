Fechei a terceira rodada de clarificação da issue de exportação de relatórios. Chegaram as respostas do jurídico e da privacidade, e o financeiro trouxe um pedido novo. Abaixo o consolidado atualizado.

## Contexto

Hoje o módulo de relatórios só permite visualizar os dados na tela, com paginação de 50 linhas. O financeiro copia página por página para o Excel no fechamento do mês. A issue pede um botão de exportação.

Nas duas primeiras rodadas fechamos formato, volume, arquitetura, permissão e filtros. Nesta rodada fechamos as pendências que dependiam de outras áreas.

## O que ficou decidido

### Formato

A exportação continua em CSV, com separador ponto e vírgula e UTF-8 com BOM.

### Volume

O relatório de lançamentos contábeis do fechamento chega a 500 mil linhas e precisa sair completo, porque vai para a auditoria externa.

### Arquitetura

A exportação continua síncrona. Para caber o volume do fechamento, vamos aumentar o timeout do gateway da API de 30 para 120 segundos. É só uma linha na configuração do gateway, e resolve o problema sem precisar de fila.

### Permissão

Só exporta quem já tem permissão de visualizar o relatório.

### Filtros

O arquivo respeita os filtros aplicados na tela: período, centro de custo e conta contábil.

### Auditoria da exportação

O jurídico respondeu: precisamos registrar quem exportou, quando e com quais filtros, e guardar o registro por cinco anos. Vamos criar a tabela `exportacao_log` com usuário, data e hora, tipo de relatório e os filtros em JSON.

### Mascaramento de dados

A privacidade decidiu que o CPF de fornecedor pessoa física sai mascarado, no formato `***.456.789-**`. Quem precisar do CPF completo pede à controladoria.

### Nome do arquivo

O financeiro validou `relatorio_<tipo>_<periodo>.csv`.

## O que voltou para a mesa

### XLSX

O financeiro pediu para reconsiderar o XLSX nesta entrega, porque a auditoria externa prefere receber planilha com as colunas já formatadas. Ficou em aberto se entra agora ou na próxima entrega.

## O que descartamos

### Exportação assíncrona com notificação

Continua descartada: exige fila, bucket, expiração do link e envio de e-mail, e o time quer uma entrega pequena.

### PDF

Descartado, porque o financeiro precisa manipular os números.

## Próximos passos

1. Decidir com o financeiro se o XLSX entra nesta entrega.
2. Quebrar a issue em sub-issues: endpoint de exportação, tabela de auditoria, mascaramento e ajuste do gateway.
3. Estimar depois da quebra.

Se estiver de acordo, sigo para a divisão em sub-issues.
