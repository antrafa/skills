# Guia de Fontes e Portais de Transparência Pública (Brasil)

Este documento reúne os principais endpoints de APIs oficiais, portais de dados abertos e estratégias de busca (Google Dorking) para auditoria e compilação de dossiês de agentes públicos no Brasil.

---

## 1. Poder Legislativo Federal

### Câmara dos Deputados (Deputados Federais)
- **Portal de Dados Abertos (API REST v2)**: `https://dadosabertos.camara.leg.br/api/v2`
- **Documentação Swagger**: `https://dadosabertos.camara.leg.br/swagger/api.html`
- **Principais Endpoints**:
  - `GET /deputados?nome={nome}`: Busca deputado por nome.
  - `GET /deputados/{id}`: Detalhes biográficos, partido, UF, gabinete, e-mail institucional e redes sociais.
  - `GET /deputados/{id}/despesas?ano={ano}`: Gastos da Cota para o Exercício da Atividade Parlamentar (CEAP).
  - `GET /deputados/{id}/discursos`: Histórico de discursos em plenário.
  - `GET /deputados/{id}/frentes`: Frentes parlamentares das quais participa.
  - `GET /deputados/{id}/orgaos`: Comissões e mesas das quais é titular ou suplente.
  - `GET /proposicoes?idDeputadoAutor={id}&ordem=DESC&ordenarPor=ano`: Projetos de Lei (PL), PECs, requerimentos de autoria.
- **Página Web Oficial do Parlamentar**: `https://www.camara.leg.br/deputados/{id}`
- **Presença em Plenário e Comissões**: `https://www.camara.leg.br/deputados/{id}/presenca-plenario`

### Senado Federal (Senadores da República)
- **API de Dados Abertos (REST JSON/XML)**: `https://legis.senado.leg.br/dadosabertos/`
- **Principais Endpoints**:
  - `GET /senador/lista/atual.json`: Lista completa de senadores em exercício com dados de identificação e mandato.
  - `GET /senador/{codigo}.json`: Detalhes cadastrais, telefones, bloco parlamentar e suplentes.
  - `GET /senador/{codigo}/autorias.json`: Propostas legislativas e relatorias do senador.
  - `GET /senador/{codigo}/votacoes.json`: Histórico de votações nominais.
- **Portal de Transparência do Senado (CEAPS)**: `https://www.senado.leg.br/transparencia/sen/{codigo}/`
- **Página de Perfil do Senador**: `https://www25.senado.leg.br/web/senadores/senador/-/perfil/{codigo}`

---

## 2. Justiça Eleitoral e Patrimônio (TSE)

### TSE DivulgaCandContas
- **Portal Oficial**: `https://divulgacandcontas.tse.jus.br/`
- **Informações Disponibilizadas**:
  - Registro de candidatura e coligações históricas
  - **Declaração de Bens e Evolução Patrimonial** (imóveis, empresas, contas, aplicações)
  - Prestação de contas eleitorais (doadores, receitas de campanha, despesas com fornecedores)
  - Proposta de governo registrada (para cargos executivos: Presidente, Governador, Prefeito)
- **API REST (DivulgaCandContas)**:
  - `GET https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/eleicoes`
  - `GET https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/{ano}/{idEleicao}/candidatos`

### Portal de Dados Abertos do TSE

- **Catálogo por ano**: `https://dadosabertos.tse.jus.br/dataset/candidatos-{ano}`
- **Cadastro nacional**: `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{ano}.zip`
- **Situação de julgamento**: `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand_complementar/consulta_cand_complementar_{ano}.zip`
- Nos CSVs, filtre `DS_CARGO = PRESIDENTE` para a disputa presidencial e associe os arquivos por `SQ_CANDIDATO`.
- Registre `DT_GERACAO` e `HH_GERACAO`: o cadastro muda durante o julgamento e pode receber substituições.
- Para o status, prefira `DS_SITUACAO_JULGAMENTO` do arquivo complementar. Valores como “AGUARDANDO JULGAMENTO” indicam pedido de registro, não deferimento.

Se a API REST ou o CDN negar acesso, consulte a interface do DivulgaCandContas e cruze a lista com uma publicação recente do TSE. Uma cópia ou espelho de terceiros pode ajudar na extração, mas nunca deve ser apresentado como fonte de autoridade e precisa ser conferido contra o catálogo oficial.

---

## 3. Poder Executivo e Governo Federal (CGU / Portal da Transparência)

- **Portal da Transparência do Governo Federal**: `https://portaldatransparencia.gov.br/`
- **API do Portal da Transparência**: `https://api.portaldatransparencia.gov.br/` (Requer chave de API ou scraping/consulta web)
- **Informações Auditáveis**:
  - Remuneração de servidores públicos, ministros e secretários nacionais
  - Registro de Sanções:
    - **CEIS** (Cadastro de Empresas Inidôneas e Suspensas)
    - **CNEP** (Cadastro Nacional de Empresas Punidas)
    - **CEPIM** (Cadastro de Entidades Privadas Sem Fins Lucrativos Impedidas)
    - **CEAF** (Cadastro de Expulsões da Administração Federal)
  - Cartão de Pagamento do Governo Federal (CPGF) e diárias de viagem

---

## 4. Órgãos de Controle e Tribunais Superiores

- **TCU (Tribunal de Contas da União)**:
  - `https://pesquisa.apps.tcu.gov.br/`
  - Consulta de contas julgadas irregulares, inabilitação para função pública e relatórios de auditoria.
- **STF (Supremo Tribunal Federal)**:
  - `https://portal.stf.jus.br/processos/`
  - Inquéritos policiais (INQ), Ações Penais (AP), Reclamações (Rcl) e Ações Diretas de Inconstitucionalidade (ADI).
- **STJ (Superior Tribunal de Justiça)**:
  - `https://processo.stj.jus.br/processo/pesquisa/`
  - Ações contra governadores e desembargadores (foro por prerrogativa de função).

---

## 5. Poderes Estaduais e Municipais

Para **Governadores, Prefeitos, Deputados Estaduais e Vereadores**:

### Assembleias Legislativas (ALEs)
- Exemplos: `ALESP` (SP), `ALERJ` (RJ), `ALMG` (MG), `ALEPE` (PE), `ALRS` (RS).
- Cada ALE mantém seu próprio Portal da Transparência com salários, verbas indenizatórias de gabinete e diárias.

### Câmaras Municipais e Prefeituras
- Consultar o Portal da Transparência do município (`transparencia.<municipio>.<uf>.gov.br` ou `camara<municipio>.<uf>.leg.br`).

---

## 6. Estratégias de Busca Jornalística e Investigativa (Dorks)

Para levantar escândalos, notícias, investigações da Polícia Federal e do Ministério Público com rigor e neutralidade, utilize queries estruturadas:

```text
# Investigações e Operações Policiais
"<Nome do Político>" AND ("operação" OR "Polícia Federal" OR "Ministério Público" OR "busca e apreensão" OR "inquérito")

# Processos Judiciais e Tribunais
"<Nome do Político>" AND ("STF" OR "STJ" OR "Ação Penal" OR "denúncia" OR "réu" OR "Tribunal de Contas")

# Gastos, Salário e Verbas
"<Nome do Político>" AND ("cota parlamentar" OR "verba indenizatória" OR "super-salário" OR "gastos de gabinete" OR "nepotismo")

# Patrimônio e TSE
"<Nome do Político>" AND ("declaração de bens" OR "patrimônio" OR "TSE" OR "DivulgaCandContas")

# Desfechos e Decisões Judiciais (Garantia do contraditório)
"<Nome do Político>" AND ("arquivado" OR "absolvido" OR "defesa alega" OR "inocentado" OR "prescrito" OR "rejeitada a denúncia")
```

---

## 7. Auditoria mínima de cobertura

Esta lista é a porta de saída da pesquisa. Registre o resultado no campo `cobertura_pesquisa`; não trate um dossiê como completo sem percorrê-la.

1. **Identidade e período**: pesquise nome civil, nome eleitoral, abreviações, apelidos públicos e grafias recorrentes. Cubra o ano corrente, os cinco anos anteriores e fatos antigos ainda com efeito jurídico ou político atual.
2. **Órgãos e classes de fato**: verifique PF, MPF/MPE, CGU, TCU/TCE, STF, STJ, tribunal local, TSE/TRE e Conselho de Ética aplicável. Pesquise também gastos, emendas, patrimônio, campanha, conflitos de interesse, desinformação checada e decisões eleitorais.
3. **Segunda passagem por vínculos descobertos**: para cada empresa, financiador, operador, instituto, ONG ou pessoa relevante que surgir, combine o nome dela com o nome do político. Inclua apenas vínculos de interesse público sustentados por documentos ou jornalismo profissional; não investigue relações pessoais sem nexo público.
4. **Atualização e desfecho**: para cada ocorrência, busque decisão, arquivamento, denúncia, absolvição, condenação, recurso, situação processual e manifestação da defesa até a data de corte.
5. **Triangulação**: dê preferência a documento ou portal oficial e use jornalismo profissional para contexto. Uma única reportagem pode revelar um fato, mas alegações contestadas exigem busca adicional e linguagem proporcional à evidência.
6. **Registro visível**: informe data da busca, período, variações de nome, eixos e portais consultados, além de limitações concretas (sigilo, instabilidade do portal, documento não localizado ou ausência de dados consolidados).

A auditoria reduz omissões, mas não autoriza afirmar exaustividade absoluta. O relatório deve dizer “nenhum caso localizado no recorte e nas fontes consultadas”, nunca “não existem outros casos”.
