# Dossiê Político — Citizen Transparency

A skill for [Claude Code](https://claude.com/claude-code) that produces **neutral, auditable citizen dossiers** on Brazilian politicians, public officials, candidates and pre-candidates, from official and trustworthy journalistic sources.

Each report works as an **X-ray of the politician**: identity, career, pay and public spending, legislative activity, declared assets and a section on scandals, controversies, lawsuits and verified facts — always with an auditable source, without recommending a vote and without turning missing data into a favorable or unfavorable conclusion.

The result is a self-contained HTML file saved to `~/.dossie-politico/<nome_do_politico>.html`, listed in a browsable index at `~/.dossie-politico/index.html`. The skill replies in the user's language; the dossiers it generates are in Brazilian Portuguese, for Brazilian readers.

## Why it exists

Pay, spending and legislative activity data are already public, but they are scattered across different portals (Câmara dos Deputados, Senado Federal, TSE — the Superior Electoral Court) and rarely cross-checked against the news on lawsuits and controversies. This skill automates the collection and consolidation, keeping every claim traceable to its original source.

## Installation

Copy or symlink this directory into `~/.claude/skills/`:

```bash
ln -s "$(pwd)" ~/.claude/skills/dossie-politico
```

Requires Python 3 (standard library only — no external dependencies).

## Usage

Invoke the skill by asking Claude Code to investigate a politician, for example:

> "Faça um dossiê do deputado federal Fulano de Tal"

The skill follows the workflow described in [SKILL.md](SKILL.md): it defines the subject, collects official data, researches facts of public interest, writes a consolidated summary and generates the report.

### Running the scripts directly

Collect data on a federal deputy (accepts `--id` to disambiguate namesakes, `--sem-despesas` to skip the parliamentary allowance aggregation):

```bash
python3 scripts/fetch_camara.py "<Nome do Deputado>"
```

Collect data on a senator (accepts `--codigo` to disambiguate namesakes):

```bash
python3 scripts/fetch_senado.py "<Nome do Senador>"
```

Full orchestration — collection, HTML generation and index update. The payload in `--extra-json` must include `cobertura_pesquisa` (see [dossier-schema.md](references/dossier-schema.md)):

```bash
python3 scripts/run_dossier.py "<Nome do Político>" --extra-json /caminho/politico_full.json
```

Render a complete payload directly, without the automatic collection:

```bash
python3 scripts/generate_dossier_html.py /caminho/politico_full.json
```

Generate several dossiers from a list of payloads, opening the index only at the end:

```bash
python3 scripts/generate_dossiers_batch.py /caminho/politicos.json
```

Correct or remove a report from the catalog:

```bash
python3 scripts/generate_dossier_html.py --remove <Nome_Do_Arquivo>.html --apagar-html
```

## Layout

| Path | Description |
|---|---|
| `SKILL.md` | Skill definition and full workflow for the agent |
| `scripts/run_dossier.py` | Main orchestrator for extraction, generation and index update |
| `scripts/fetch_camara.py` | Collects from the Câmara API, including the parliamentary allowance (CEAP) by year, category and supplier |
| `scripts/fetch_senado.py` | Automated collection from the Senado Federal API |
| `scripts/fetch_governo.py` | Macroeconomic indicators from the Banco Central (BCB SGS) for presidential terms |
| `scripts/fetch_tse_transparency.py` | TSE electoral lookups and search links on official portals |
| `scripts/remuneracao_oficial.py` | Single source for salary (subsídio), allowances and the norm that sets them |
| `scripts/generate_dossier_html.py` | Rendering engine for the individual reports and `index.html` |
| `scripts/generate_dossiers_batch.py` | Generates several reports from a JSON list, opening the index once |
| `references/sources-guide.md` | Guide to official endpoints, portals and search dorks |
| `references/dossier-schema.md` | Formal JSON schema of the dossier |
| `references/legal-journalism-ethics.md` | Scope of who may be the subject of a dossier, legal rigor, neutrality and the right of reply |
| `examples/` | Complete reference payloads (`exemplo_deputado.json`, `exemplo_senador.json`, `exemplo_governo_presidencial.json`) |
| `tests/` | Runnable regressions |

## Data sources

- [Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/api/v2/) (Chamber of Deputies open data)
- [Dados Abertos do Senado Federal](https://legis.senado.leg.br/dadosabertos/) (Federal Senate open data)
- [DivulgaCandContas — TSE](https://divulgacandcontas.tse.jus.br/) (candidates, assets and campaign finance)
- [SGS — Banco Central do Brasil](https://www3.bcb.gov.br/sgspub) (economic time series, for presidential terms)

Offices outside the Congresso Nacional (Executive, state and municipal Legislative) have no automatic collector; filling them follows the manual procedure described in [sources-guide.md](references/sources-guide.md).

## Principles

- **Neutrality**: does not recommend a vote, does not attribute intent, does not turn missing data into a conclusion.
- **Auditability**: every relevant claim points to a verifiable primary or journalistic source; URLs are checked over HTTP before delivery.
- **Right of reply**: every controversy records the defense's position or the court outcome, when found.
- **Correction without erasure**: corrections prefer regenerating the report (keeping the revision history in the footer) over simply removing the content.

See the full detail in [legal-journalism-ethics.md](references/legal-journalism-ethics.md).

## Tests

```bash
python3 -m unittest discover -s tests
```

## Legal notice

The generated reports are automated compilations of public data and news, with a summary written by AI from those same sources. They are not independent journalistic investigation, accusation or character assessment. Always check the claims against the linked sources before making any decision based on them.
