# Dossiê Político — Transparência Cidadã

Skill para [Claude Code](https://claude.com/claude-code) que produz **dossiês cidadãos, neutros e auditáveis** sobre políticos, agentes públicos, candidatos e pré-candidatos brasileiros, a partir de fontes oficiais e jornalísticas confiáveis.

Cada relatório funciona como um **raio-X do político**: identidade, trajetória, remuneração e gastos públicos, atividade legislativa, patrimônio declarado e uma seção de escândalos, polêmicas, processos e fatos verificados — sempre com fonte auditável, sem recomendar voto e sem transformar ausência de dado em conclusão favorável ou desfavorável.

O resultado é um HTML autossuficiente salvo em `~/.dossie-politico/<nome_do_politico>.html`, listado em um índice navegável `~/.dossie-politico/index.html`.

## Por que existe

Dados de remuneração, gastos e atividade parlamentar já são públicos, mas estão espalhados em portais diferentes (Câmara, Senado, TSE) e raramente cruzados com o noticiário de processos e controvérsias. Esta skill automatiza a coleta e a consolidação, mantendo cada afirmação rastreável até a fonte original.

## Instalação

Copie ou faça symlink deste diretório para dentro de `~/.claude/skills/`:

```bash
ln -s "$(pwd)" ~/.claude/skills/dossie-politico
```

Requer Python 3 (biblioteca padrão apenas — sem dependências externas).

## Uso

Invoque a skill pedindo ao Claude Code para investigar um político, por exemplo:

> "Faça um dossiê do deputado federal Fulano de Tal"

A skill segue o fluxo descrito em [SKILL.md](SKILL.md): define o alvo, coleta dados oficiais, pesquisa fatos de interesse público, escreve um resumo consolidado e gera o relatório.

### Uso direto dos scripts

Coleta de dados de um deputado federal (aceita `--id` para desambiguar homônimos, `--sem-despesas` para pular a agregação da cota parlamentar):

```bash
python3 scripts/fetch_camara.py "<Nome do Deputado>"
```

Coleta de dados de um senador (aceita `--codigo` para desambiguar homônimos):

```bash
python3 scripts/fetch_senado.py "<Nome do Senador>"
```

Orquestração completa — coleta, geração do HTML e atualização do índice. O payload em `--extra-json` precisa incluir `cobertura_pesquisa` (ver [dossier-schema.md](references/dossier-schema.md)):

```bash
python3 scripts/run_dossier.py "<Nome do Político>" --extra-json /caminho/politico_full.json
```

Renderizar um payload completo diretamente, sem passar pela coleta automática:

```bash
python3 scripts/generate_dossier_html.py /caminho/politico_full.json
```

Gerar vários dossiês de uma lista de payloads, abrindo o índice apenas ao final:

```bash
python3 scripts/generate_dossiers_batch.py /caminho/politicos.json
```

Retificar ou remover um relatório do catálogo:

```bash
python3 scripts/generate_dossier_html.py --remove <Nome_Do_Arquivo>.html --apagar-html
```

## Estrutura

| Caminho | Descrição |
|---|---|
| `SKILL.md` | Definição da skill e fluxo de trabalho completo para o agente |
| `scripts/run_dossier.py` | Orquestrador principal da extração, geração e atualização do índice |
| `scripts/fetch_camara.py` | Coleta na API da Câmara, incluindo a cota parlamentar (CEAP) por ano, categoria e fornecedor |
| `scripts/fetch_senado.py` | Coleta automatizada na API do Senado Federal |
| `scripts/fetch_tse_transparency.py` | Consultas eleitorais do TSE e links de busca nos portais oficiais |
| `scripts/remuneracao_oficial.py` | Fonte única de subsídio, verbas e norma que os fixa |
| `scripts/generate_dossier_html.py` | Motor de renderização dos relatórios individuais e do `index.html` |
| `scripts/generate_dossiers_batch.py` | Gera vários relatórios a partir de uma lista JSON, abrindo o índice uma única vez |
| `references/sources-guide.md` | Guia de endpoints oficiais, portais e dorks de busca |
| `references/dossier-schema.md` | Esquema JSON formal do dossiê |
| `references/legal-journalism-ethics.md` | Escopo de quem pode ser objeto de dossiê, rigor jurídico, neutralidade e contraditório |
| `examples/` | Payloads completos de referência (`exemplo_deputado.json`, `exemplo_senador.json`) |
| `tests/` | Regressões executáveis |

## Fontes de dados

- [Dados Abertos da Câmara dos Deputados](https://dadosabertos.camara.leg.br/api/v2/)
- [Dados Abertos do Senado Federal](https://legis.senado.leg.br/dadosabertos/)
- [DivulgaCandContas — TSE](https://divulgacandcontas.tse.jus.br/)

Cargos fora do Congresso Nacional (Executivo, Legislativo estadual e municipal) não têm coletor automático; o preenchimento segue o roteiro manual descrito em [sources-guide.md](references/sources-guide.md).

## Princípios

- **Neutralidade**: não recomenda voto, não atribui intenção, não converte ausência de dado em conclusão.
- **Auditabilidade**: toda afirmação relevante aponta para uma fonte primária ou jornalística verificável; URLs são checadas por HTTP antes da entrega.
- **Contraditório**: toda controvérsia registra a posição da defesa ou o desfecho judicial, quando localizados.
- **Correção sem apagamento**: retificações preferem regerar o relatório (mantendo histórico de revisões no rodapé) a simplesmente remover o conteúdo.

Veja o detalhamento completo em [legal-journalism-ethics.md](references/legal-journalism-ethics.md).

## Testes

```bash
python3 -m unittest discover -s tests
```

## Aviso legal

Os relatórios gerados são compilações automatizadas de dados públicos e notícias, com resumo redigido por IA a partir dessas mesmas fontes. Não constituem apuração jornalística autônoma, acusação ou avaliação de caráter. Sempre confira as afirmações nas fontes vinculadas antes de tomar qualquer decisão com base nelas.
