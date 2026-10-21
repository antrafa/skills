# Guide to Public Transparency Sources and Portals (Brazil)

This document gathers the main official API endpoints, open data portals and search strategies (Google dorking) for auditing and compiling dossiers on Brazilian public officials.

---

## 1. Federal Legislative branch

### Câmara dos Deputados (federal deputies)
- **Open Data Portal (REST API v2)**: `https://dadosabertos.camara.leg.br/api/v2`
- **Swagger documentation**: `https://dadosabertos.camara.leg.br/swagger/api.html`
- **Main endpoints**:
  - `GET /deputados?nome={nome}`: Searches a deputy by name.
  - `GET /deputados/{id}`: Biographical details, party, UF, office, institutional e-mail and social media.
  - `GET /deputados/{id}/despesas?ano={ano}`: Spending under the Cota para o Exercício da Atividade Parlamentar (CEAP, the parliamentary activity allowance).
  - `GET /deputados/{id}/discursos`: History of floor speeches.
  - `GET /deputados/{id}/frentes`: Parliamentary caucuses (frentes parlamentares) the deputy belongs to.
  - `GET /deputados/{id}/orgaos`: Committees and boards where the deputy is a full member or alternate.
  - `GET /proposicoes?idDeputadoAutor={id}&ordem=DESC&ordenarPor=ano`: Authored bills (PL), constitutional amendments (PEC) and motions.
- **Official legislator web page**: `https://www.camara.leg.br/deputados/{id}`
- **Attendance in plenary and committees**: `https://www.camara.leg.br/deputados/{id}/presenca-plenario`

### Senado Federal (senators)
- **Open Data API (REST JSON/XML)**: `https://legis.senado.leg.br/dadosabertos/`
- **Main endpoints**:
  - `GET /senador/lista/atual.json`: Full list of sitting senators with identification and term data.
  - `GET /senador/{codigo}.json`: Registration details, phones, parliamentary bloc and alternates.
  - `GET /senador/{codigo}/autorias.json`: The senator's legislative proposals and rapporteurships.
  - `GET /senador/{codigo}/votacoes.json`: History of roll-call votes.
- **Senate Transparency Portal (CEAPS)**: `https://www.senado.leg.br/transparencia/sen/{codigo}/`
- **Senator profile page**: `https://www25.senado.leg.br/web/senadores/senador/-/perfil/{codigo}`

---

## 2. Electoral courts and assets (TSE)

### TSE DivulgaCandContas
- **Official portal**: `https://divulgacandcontas.tse.jus.br/`
- **Information available**:
  - Candidacy registration and historical coalitions
  - **Asset declarations and asset evolution** (real estate, companies, accounts, investments)
  - Campaign finance reports (donors, campaign revenue, spending with suppliers)
  - Registered government platform (for executive offices: President, Governor, Mayor)
- **REST API (DivulgaCandContas)**:
  - `GET https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/eleicoes`
  - `GET https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/{ano}/{idEleicao}/candidatos`

### TSE Open Data Portal

- **Catalog by year**: `https://dadosabertos.tse.jus.br/dataset/candidatos-{ano}`
- **National registry**: `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{ano}.zip`
- **Judgment status**: `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand_complementar/consulta_cand_complementar_{ano}.zip`
- In the CSVs, filter `DS_CARGO = PRESIDENTE` for the presidential race and join the files on `SQ_CANDIDATO`.
- Record `DT_GERACAO` and `HH_GERACAO`: the registry changes during judgment and may receive substitutions.
- For the status, prefer `DS_SITUACAO_JULGAMENTO` from the supplementary file. Values such as "AGUARDANDO JULGAMENTO" (awaiting judgment) mean a registration request, not approval.

If the REST API or the CDN denies access, use the DivulgaCandContas interface and cross-check the list against a recent TSE publication. A third-party copy or mirror may help with extraction, but it must never be presented as an authoritative source and must be checked against the official catalog.

---

## 3. Executive branch and Federal Government (CGU / Portal da Transparência)

- **Federal Government Transparency Portal (Portal da Transparência)**: `https://portaldatransparencia.gov.br/`
- **Portal da Transparência API**: `https://api.portaldatransparencia.gov.br/` (requires an API key, or scraping / web lookup)
- **Auditable information**:
  - Pay of civil servants, ministers and national secretaries
  - Sanction registries:
    - **CEIS** (Cadastro de Empresas Inidôneas e Suspensas — registry of disqualified and suspended companies)
    - **CNEP** (Cadastro Nacional de Empresas Punidas — national registry of punished companies)
    - **CEPIM** (Cadastro de Entidades Privadas Sem Fins Lucrativos Impedidas — registry of barred non-profits)
    - **CEAF** (Cadastro de Expulsões da Administração Federal — registry of expulsions from the federal administration)
  - Federal Government Payment Card (CPGF, the corporate card) and travel per diems

---

## 4. Oversight bodies and higher courts

- **TCU (Tribunal de Contas da União, the federal audit court)**:
  - `https://pesquisa.apps.tcu.gov.br/`
  - Lookup of accounts judged irregular, disqualification from public office and audit reports.
- **STF (Supremo Tribunal Federal, the supreme court)**:
  - `https://portal.stf.jus.br/processos/`
  - Police inquiries (INQ), criminal cases (AP), complaints (Rcl) and direct actions of unconstitutionality (ADI).
- **STJ (Superior Tribunal de Justiça, the superior court of justice)**:
  - `https://processo.stj.jus.br/processo/pesquisa/`
  - Cases against governors and appellate judges (foro por prerrogativa de função, special jurisdiction by office).

---

## 5. State and municipal powers

For **governors, mayors, state deputies and city councilors**:

### Legislative Assemblies (ALEs)
- Examples: `ALESP` (SP), `ALERJ` (RJ), `ALMG` (MG), `ALEPE` (PE), `ALRS` (RS).
- Each ALE keeps its own Portal da Transparência with salaries, office allowances (verbas indenizatórias) and per diems.

### City councils (Câmaras Municipais) and city halls (Prefeituras)
- Check the municipality's Portal da Transparência (`transparencia.<municipio>.<uf>.gov.br` or `camara<municipio>.<uf>.leg.br`).

---

## 6. Journalistic and investigative search strategies (dorks)

To surface scandals, news, and Polícia Federal and Ministério Público investigations with rigor and neutrality, use structured queries. Keep the search terms in Portuguese: they match the language of the sources.

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

The query groups above cover, in order: investigations and police operations; court cases; spending, salary and allowances; assets and the TSE; outcomes and court decisions (the right of reply).

---

## 7. Minimum coverage audit

This list is the exit gate of the research. Record the result in the `cobertura_pesquisa` field; do not treat a dossier as complete without going through it.

1. **Identity and period**: search civil name, electoral name, abbreviations, public nicknames and recurring spellings. Cover the current year, the five previous years and older facts that still have a current legal or political effect.
2. **Bodies and classes of fact**: check PF (Federal Police), MPF/MPE (federal/state prosecutors), CGU (federal comptroller), TCU/TCE (federal/state audit courts), STF, STJ, the local court, TSE/TRE (electoral courts) and the applicable Ethics Council. Also search spending, budget amendments (emendas), assets, campaign, conflicts of interest, fact-checked disinformation and electoral decisions.
3. **Second pass on discovered ties**: for each relevant company, funder, operator, institute, NGO or person that comes up, combine its name with the politician's name. Include only ties of public interest backed by documents or professional journalism; do not investigate personal relationships with no public nexus.
4. **Update and outcome**: for each occurrence, look for decision, dismissal, indictment, acquittal, conviction, appeal, procedural status and the defense's statement up to the cutoff date.
5. **Triangulation**: prefer an official document or portal and use professional journalism for context. A single news report may reveal a fact, but disputed claims require additional search and language proportional to the evidence.
6. **Visible record**: state the search date, period, name variations, axes and portals consulted, plus concrete limitations (secrecy, portal instability, document not found or no consolidated data).

The audit reduces omissions, but it does not authorize claiming absolute exhaustiveness. The report must say "nenhum caso localizado no recorte e nas fontes consultadas" (no case found within the scope and sources consulted), never "não existem outros casos" (no other cases exist).
