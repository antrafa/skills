# ADR 0001 — Implementar o frontend em Next.js antes do Payload CMS

- **Status:** aceita
- **Data:** 19 de agosto de 2026
- **Responsáveis:** projeto Rádio Nova Mensagem

## Contexto

O site atual é executado sobre PHP e o framework proprietário AFF. Conteúdo, rotas, templates e administração estão acoplados à estrutura `pages/novamensagem2017` e ao banco MySQL legado.

O objetivo é reconstruir a experiência pública com uma interface contemporânea e, posteriormente, substituir o painel administrativo pelo Payload CMS. A aprovação visual precisa acontecer antes da modelagem e da migração definitiva dos dados.

## Decisão

Criar um projeto independente chamado `novamensagem2026`, irmão do repositório `nm`, usando Next.js com App Router e TypeScript.

A entrega será dividida em duas fases deliberadas:

### Fase 1 — frontend validável

- Implementar home e páginas internas completas.
- Usar conteúdo tipado e mockado em `src/data/mock-content.ts`.
- Manter o frontend desacoplado do AFF, do MySQL e do Payload.
- Colocar o player da rádio no layout raiz para preservar a reprodução nas transições internas.
- Simular o formulário de contato sem realizar envio externo.
- Gerar rotas estáticas para validar navegação, responsividade, acessibilidade e SEO estrutural.

### Fase 2 — Payload CMS

- Adicionar o Payload ao mesmo projeto Next.js.
- Modelar Collections e Globals a partir dos contratos dos mocks.
- Substituir consultas aos arrays por consultas à Local API do Payload.
- Migrar os registros do MySQL para PostgreSQL.
- Migrar imagens e áudios para uma Collection de mídia e storage persistente.
- Implementar autenticação, controle de acesso e o envio real do formulário.
- Preservar slugs existentes e cadastrar redirects quando uma URL precisar mudar.

## Player

O player é um Client Component montado no layout raiz. Layouts do App Router permanecem montados durante a navegação interna, permitindo que o áudio continue tocando enquanto apenas o conteúdo da página é substituído.

O player aguarda uma ação explícita do ouvinte para reproduzir o stream. Recarregar a página, fechar a aba ou navegar para outro domínio ainda encerra o áudio.

## Atualização

Em 19 de agosto de 2026, após a validação inicial do frontend, a fase 2 foi iniciada. O Payload foi instalado e as entidades legadas foram mapeadas, sem substituir ainda os mocks consumidos pelo site público.

## Consequências

### Positivas

- A interface pode ser aprovada sem depender da migração do legado.
- Os contratos tipados dos mocks orientam a futura modelagem do Payload.
- O frontend não precisará ser refeito ao conectar o CMS.
- O player passa a persistir na navegação normal do site.
- A aplicação pode ser validada por build estático antes de existir banco.

### Custos e limitações temporárias

- Conteúdo editado no site PHP não aparece automaticamente nesta fase.
- Formulário, áudios sob demanda e vídeos são apenas representações de interface.
- A integração com Payload exigirá ambiente Node.js, PostgreSQL e storage persistente.
- Será necessária uma estratégia de congelamento ou sincronização final do conteúdo na publicação.

## Alternativas rejeitadas

### Criar `pages/novamensagem2026` dentro do AFF

Rejeitada porque manteria a nova interface presa ao roteamento PHP e criaria retrabalho caso a migração para Payload acontecesse depois.

### Integrar o Payload antes da validação visual

Rejeitada porque misturaria duas fontes grandes de risco — produto e migração de dados — e atrasaria a validação do que o público realmente verá.

### Manter o player somente em popup

Rejeitada como comportamento principal porque o App Router permite preservar o player no layout compartilhado. Uma janela independente poderá ser reconsiderada como recurso opcional, não como requisito da arquitetura.
