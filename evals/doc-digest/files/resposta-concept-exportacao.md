Fechei a segunda rodada de clarificação da issue de exportação de relatórios. Abaixo está o consolidado do que conversamos, o que já ficou decidido, o que ainda depende de resposta e o que descartamos no caminho.

## Contexto

Hoje o módulo de relatórios só permite visualizar os dados na tela, com paginação de 50 linhas. Os usuários do financeiro copiam página por página para o Excel, o que leva horas no fechamento do mês. A issue pede um botão de exportação.

Na primeira rodada levantamos quem usa, com que volume e em que formato. Nesta rodada fechamos as decisões de arquitetura e de escopo.

## O que ficou decidido

### Formato

A exportação será em CSV, com separador ponto e vírgula e codificação UTF-8 com BOM, para o Excel abrir acentuação corretamente sem configuração. XLSX ficou para uma próxima entrega.

### Volume

O financeiro confirmou que o relatório de lançamentos contábeis do fechamento chega a 500 mil linhas. A exportação precisa suportar esse volume completo, sem corte, porque o arquivo vai para a auditoria externa.

### Arquitetura

A exportação será síncrona: o usuário clica no botão, o backend monta o CSV e devolve o arquivo na mesma requisição. Escolhemos esse caminho porque é o mais simples de implementar e não exige fila nem armazenamento temporário. O gateway da API mantém o timeout padrão de 30 segundos.

### Permissão

Só exporta quem já tem permissão de visualizar o relatório. Não haverá permissão nova específica para exportação.

### Filtros

O arquivo respeita os mesmos filtros aplicados na tela no momento do clique: período, centro de custo e conta contábil.

## O que ainda está em aberto

1. **Auditoria da exportação:** o jurídico ainda não respondeu se precisamos registrar quem exportou, quando e com quais filtros. Isso muda o modelo de dados se for obrigatório.
2. **Mascaramento de dados:** alguns relatórios têm CPF de fornecedores pessoa física. Falta a área de privacidade dizer se o CPF sai completo, mascarado ou não sai.
3. **Limite por usuário:** não definimos se um usuário pode disparar várias exportações seguidas. O time de infraestrutura pediu para pensar nisso, mas não chegou a propor um número.
4. **Nome do arquivo:** sugestão atual é `relatorio_<tipo>_<periodo>.csv`, pendente de validação com o financeiro.

## O que descartamos

### Exportação assíncrona com notificação

Consideramos gerar o arquivo em segundo plano, guardar num bucket e mandar um link por e-mail quando ficasse pronto. Descartamos porque exige fila, bucket, política de expiração do link e envio de e-mail, e o time queria uma entrega pequena.

### PDF

O PDF foi descartado porque o financeiro precisa manipular os números no Excel, e PDF não resolve o problema de copiar dados.

### Exportar só a página atual

Chegamos a discutir exportar só as 50 linhas visíveis como primeira versão. Descartamos porque não resolve a dor: o problema é justamente juntar todas as páginas.

## Próximos passos

1. Cobrar o jurídico sobre a auditoria da exportação.
2. Cobrar a área de privacidade sobre o CPF.
3. Com as duas respostas, a issue fica pronta para quebrar em tarefas.
4. Estimar o desenvolvimento depois da quebra.

Se estiver de acordo com as decisões acima, posso seguir para a divisão em sub-issues assim que as pendências forem respondidas.
