---
name: dossie-politico
description: "Produz dossiês cidadãos, neutros e auditáveis sobre políticos, agentes públicos, candidatos e pré-candidatos brasileiros a partir de fontes oficiais e jornalísticas confiáveis. Use para investigar trajetória, atividade pública, remuneração, gastos, patrimônio eleitoral, processos e controvérsias, ou para comparar nomes de uma eleição, gerando relatórios HTML e um índice navegável em ~/.dossie-politico/."
---

# Dossiê Político — Transparência Cidadã

Crie um recurso de consulta pública acessível, factual e apartidário. Consolide dados cadastrais, trajetória, remuneração e gastos públicos, atividade legislativa ou administrativa, evolução patrimonial declarada e uma seção de escândalos, polêmicas, processos e fatos verificados. Não recomende voto, não atribua intenção e não transforme ausência de dados em conclusão favorável ou desfavorável.

Cada relatório deve funcionar como um **raio-X do candidato ou agente público**: a leitura inicial consolida identidade, trajetória, atuação, propostas, remuneração, uso de dinheiro público, patrimônio, escândalos, polêmicas, processos, posição da defesa e lacunas; as seções seguintes permitem aprofundar cada afirmação por links auditáveis. Grave o HTML em **`~/.dossie-politico/<nome_do_politico>.html`**, atualize **`~/.dossie-politico/index.html`** e, ao terminar uma análise solicitada pelo usuário, **abra o índice geral no navegador**.

---

## Estrutura de Arquivos da Skill

- `scripts/run_dossier.py`: Orquestrador principal da extração, geração e atualização do índice (suporta perfis parlamentares e governos com `--governo`).
- `scripts/fetch_governo.py`: Coleta indicadores macroeconômicos oficiais no Banco Central (BCB SGS) para mandatos presidenciais com presets (FHC, Lula, Dilma, Temer, Bolsonaro).
- `scripts/fetch_camara.py`: Coleta na API da Câmara, incluindo a agregação da cota parlamentar (CEAP) por ano, categoria e fornecedor.
- `scripts/fetch_senado.py`: Coleta automatizada na API do Senado Federal.
- `scripts/fetch_tse_transparency.py`: Consultas eleitorais do TSE e links de busca nos portais oficiais.
- `scripts/remuneracao_oficial.py`: Único lugar onde ficam subsídio, verbas e a norma que os fixa.
- `scripts/generate_dossier_html.py`: Motor de renderização dos relatórios individuais (.html), dados estruturados (.json) e catálogo (`index.json` / `index.html`).
- `scripts/generate_dossiers_batch.py`: Gera vários relatórios individuais a partir de uma lista JSON e abre o índice uma única vez ao final.
- `references/sources-guide.md`: Guia de endpoints oficiais, portais e dorks de busca.
- `references/dossier-schema.md`: Esquema JSON formal do dossiê (suporta `perfil_politico` e `governo_presidencial`).
- `references/legal-journalism-ethics.md`: Escopo de quem pode ser objeto de dossiê, rigor jurídico, neutralidade e contraditório.
- `examples/exemplo_deputado.json`, `examples/exemplo_senador.json` e `examples/exemplo_governo_presidencial.json`: Payloads completos de referência, no formato exigido hoje.
- `tests/`: Regressões executáveis com `python3 -m unittest discover -s tests`.

---

## Referências obrigatórias conforme a tarefa

- Leia [legal-journalism-ethics.md](references/legal-journalism-ethics.md) **antes de aceitar o alvo** (a seção 0 define quem pode e quem não pode ser objeto de dossiê) e sempre que houver processos, investigações, acusações ou controvérsias.
- Leia [sources-guide.md](references/sources-guide.md) para escolher fontes oficiais, pesquisar eleições ou cobrir cargos fora do Congresso Nacional.
- Leia [dossier-schema.md](references/dossier-schema.md) antes de montar ou alterar o payload entregue ao gerador HTML.

## Fluxo de trabalho

### 1. Defina a pessoa e o recorte

Identifique nome civil e eleitoral, cargo ou ocupação atual, mandatos anteriores, partido, UF e período analisado. Registre uma **data de corte** visível no relatório.

Em pesquisas eleitorais com vários nomes, estabeleça primeiro o universo usando a Justiça Eleitoral e fontes primárias. Classifique cada pessoa sem misturar os estados:

- **candidatura registrada**: consta do sistema oficial do TSE, mencionando se está aguardando julgamento, deferida, indeferida com recurso etc.;
- **candidatura anunciada**: anunciada pelo partido ou pela pessoa, mas ainda sem registro oficial localizado;
- **pré-candidatura**: declarada como pré-candidato ou formalizada pelo partido antes das convenções/registro;
- **nome cogitado**: aparece apenas em articulações, pesquisas ou reportagens.

Se a eleição ainda não tiver lista oficial definitiva, diga isso no título e no resumo. Não use pesquisas de intenção de voto como prova de candidatura.

### 2. Colete e cruze dados oficiais

Use os coletores quando o cargo for compatível:

1. **Se Deputado Federal**:
   ```bash
   python3 scripts/fetch_camara.py "<Nome do Político>"
   ```
   Quando o nome tiver mais de uma correspondência, o script recusa a escolha e devolve a lista de IDs (`status: ambiguous`). Confirme qual é a pessoa e repita com `--id <id>`; nunca aceite o primeiro resultado sem conferir partido e UF.
   *Extrai: ID, biografia, gabinete, e-mail institucional, redes sociais, remuneração base, projetos de lei recentes, comissões, frentes parlamentares e a cota parlamentar agregada por ano, categoria e fornecedor.*
   A agregação da CEAP percorre várias páginas da API (alguns segundos). Use `--sem-despesas` só quando quiser apenas o cadastro. Ex-deputados são localizados nas legislaturas anteriores, com aviso no stderr.

2. **Se Senador da República**:
   ```bash
   python3 scripts/fetch_senado.py "<Nome do Senador>"
   ```
   Em caso de homônimos, o script devolve os códigos e você repete com `--codigo <codigo>`. A busca cobre apenas senadores em exercício; ex-senadores exigem o roteiro de [sources-guide.md](references/sources-guide.md).
   *Extrai: Código parlamentar, dados de identificação, mandato, suplentes, bloco, matérias legislativas e canais de transparência de despesas.*

3. **Se Mandato Presidencial / Governo**:
   ```bash
   python3 scripts/fetch_governo.py "<preset_ou_nome>"
   ```
   Presets disponíveis: `fhc`, `lula`, `dilma`, `temer`, `bolsonaro`. Para mandatos customizados, utilize `--inicio DD/MM/AAAA` e `--fim DD/MM/AAAA`.
   *Extrai: Séries históricas do Banco Central (BCB SGS) com inflação acumulada e média (IPCA), taxas Selic (inicial, final e média), cotação PTAX do Dólar e variação percentual, Dívida Bruta (% PIB), evolução do PIB anual e consolidação de cofres públicos.*

4. **Demais cargos**: consulte [sources-guide.md](references/sources-guide.md) e os portais do órgão ou ente federativo.

5. **Histórico Eleitoral e Bens (TSE DivulgaCandContas)**:
   - Consulte o histórico de declarações de bens no TSE (ano a ano) e o patrimônio declarado mais recente. Não há coletor automático: os valores são digitados por você e precisam ser conferidos duas vezes contra o portal.
   - Para cargos sem coletor (Executivo, Legislativo estadual e municipal), preencha `despesas_discriminadas` manualmente a partir do portal de transparência do órgão, seguindo o formato do esquema.

6. **Antes de montar o payload, leia um exemplo completo**:
   - Para parlamentares da Câmara: `examples/exemplo_deputado.json`
   - Para senadores: `examples/exemplo_senador.json`
   - Para mandatos de governos presidenciais: `examples/exemplo_governo_presidencial.json` (inclui `indicadores_economicos`, `cofres_publicos`, `promessas_campanha` e `projetos_de_lei_e_reformas`).
   Eles mostram o formato exigido hoje, incluindo `cobertura_pesquisa`, `resumo_cidadao_ia`, os quatro campos de evidência por caso e o padrão de fonte sem URL localizada.

Não preencha lacunas com valores-padrão tratados como fatos. Registre “não localizado”, o período pesquisado e onde a busca foi feita. Para ocupantes do Executivo ou ex-mandatários, substitua métricas parlamentares inaplicáveis por realizações, atos de governo ou indicadores compatíveis, sempre atribuídos a fontes.

### 3. Pesquise fatos de interesse público

Execute busca sistemática de notícias, investigações e fatos notórios respeitando as diretrizes de [legal-journalism-ethics.md](references/legal-journalism-ethics.md):

Antes de considerar a pesquisa encerrada, execute a **auditoria mínima de cobertura** de [sources-guide.md](references/sources-guide.md). Ela é uma etapa obrigatória, não uma sugestão: use variações do nome, faça uma segunda passagem com os nomes de empresas, financiadores, operadores e entidades relevantes descobertos durante a primeira busca e registre o recorte pesquisado em `cobertura_pesquisa`.

1. **Consultas de Investigação e Processos**:
   - Pesquise operações da Polícia Federal, inquéritos no Ministério Público, processos no STF/STJ/TJs e representações em Conselhos de Ética.
   - Utilize as queries estruturadas (Dorks) descritas em [sources-guide.md](references/sources-guide.md).
2. **Para cada fato relevante identificado**:
   - Defina um **Título Claro e Objetivo**.
   - Registre o **Ano / Data** aproximada do fato.
   - Classifique a **Categoria** (ex: *Operação Policial*, *Investigação MP/STF*, *Uso de Verba Indenizatória*, *Processo Eleitoral*, *Controvérsia Ética*).
   - Defina o **Status Atual**:
     - `Condenado` ou `Denunciado` (Badge Vermelho)
     - `Em Investigação` ou `Em Apuração` (Badge Amarelo)
     - `Arquivado`, `Absolvido` ou `Inocentado` (Badge Verde)
     - `Notícia de Interesse Público` (Badge Azul)
   - Escreva um **Resumo dos Fatos** conciso e neutro baseado em fatos auditáveis.
   - Classifique a **força da evidência** conforme [legal-journalism-ethics.md](references/legal-journalism-ethics.md), deixando explícitos o que está e o que não está comprovado.
   - Registre a **Posição da Defesa / Desfecho Judicial** (garantia obrigatória do contraditório).
   - Anexe a fonte primária quando pública e ao menos uma fonte jornalística profissional quando ela acrescentar contexto.
   - **Cite apenas URLs que você abriu ou que voltaram da busca.** Não reconstrua endereço de reportagem por padrão de site. O gerador verifica cada URL por HTTP e marca no relatório as que não resolvem; se a checagem acusar links quebrados, corrija antes de entregar em vez de deixar a marcação no dossiê.

Atualize o desfecho de cada caso até a data de corte. Se não localizar manifestação da defesa depois de uma busca explícita, informe isso sem presumir silêncio deliberado. “Nenhum caso localizado” significa apenas que nada foi encontrado no recorte e nas fontes consultadas. Não atribua “grau de veracidade” à pessoa; classifique cada alegação ou evento e não use porcentagens ou notas arbitrárias.

Não conclua o dossiê enquanto os eixos da auditoria de cobertura não tiverem sido verificados ou marcados, com justificativa, como inaplicáveis. A descoberta tardia de uma pessoa ou entidade ligada a um caso exige nova busca cruzada antes da geração do relatório.

### 4. Escreva o raio-X consolidado por IA

Preencha `resumo_cidadao_ia` conforme o esquema. A síntese deve ter linguagem simples e, em aproximadamente **300 a 600 palavras**, cobrir proporcionalmente:

- quem é, cargo, partido e situação eleitoral ou funcional;
- trajetória e principais áreas de atuação;
- uso de dinheiro público, remuneração e patrimônio, quando aplicáveis;
- entregas, proposições ou decisões públicas mais relevantes;
- **todos os escândalos, processos, investigações e polêmicas materiais catalogados**, sempre com status atual, força da evidência, o que não está comprovado e contraditório;
- lacunas materiais ou dados ainda não localizados.

O resumo é uma **compilação da IA baseada nos dados e fontes do próprio dossiê**, não uma apuração autônoma nem uma avaliação de caráter. Não introduza fatos ou inferências que não estejam documentados nas seções detalhadas. Destaque de três a seis pontos-chave e exponha limitações de forma visível.

O gerador exibe automaticamente, dentro do consolidado, uma lista compacta de **todos** os itens de `controversias_e_noticias`, incluindo status, grau de evidência, comprovado/não comprovado e defesa. Não remova essa lista nem selecione apenas casos convenientes. Quando não houver casos catalogados, preserve o aviso de que isso vale somente para o recorte e as fontes consultadas.

### 5. Gere o relatório e atualize o índice

1. Monte o payload de acordo com [dossier-schema.md](references/dossier-schema.md).
2. Prefira o orquestrador, que abre o índice ao concluir:
   - **Para parlamentares e candidatos:**
     ```bash
     python3 scripts/run_dossier.py "<Nome do Político>" --extra-json /tmp/politico_extra.json
     ```
   - **Para mandatos presidenciais e governos:**
     ```bash
     python3 scripts/run_dossier.py --governo bolsonaro --extra-json /tmp/governo_extra.json
     ```
     O orquestrador consulta automaticamente as séries do BCB SGS via `fetch_governo.py`, mescla os dados complementares de `--extra-json`, gera `<slug>.html` e salva os dados brutos estruturados em `<slug>.json` em `~/.dossie-politico/`.
   
   O `--extra-json` é obrigatório na prática: o payload precisa trazer `cobertura_pesquisa`, e o orquestrador recusa a execução antes de qualquer chamada de rede se ela estiver ausente. Use `--id` / `--codigo` para desambiguar homônimos e `--json-only` para inspecionar o payload consolidado sem gerar HTML nem tocar no índice.
   Para renderizar um payload completo diretamente, use `python3 scripts/generate_dossier_html.py /tmp/politico_full.json`; esse comando também salva `<slug>.html` e `<slug>.json`, atualiza `index.json` e abre o índice.
   Para vários nomes, forneça uma lista de payloads completos sem agregá-los em uma única página:
   ```bash
   python3 scripts/generate_dossiers_batch.py /tmp/politicos.json
   ```
3. Verifique a existência do relatório (`<slug>.html`), dos dados estruturados (`<slug>.json`), de `index.html` e de `index.json`, conferindo que a entrada aparece no catálogo com `tipo_dossie`, `periodo_mandato` e `resumo_indicadores`.
   Leia também o resumo da verificação de fontes impresso pelo gerador (`Verificação das fontes citadas: ...`). Fonte `quebrado` ou `indisponivel` significa link que não resolve: troque a URL e gere de novo. `--no-check-links` existe só para ambiente sem rede.
4. Confirme que **`~/.dossie-politico/index.html` foi aberto no navegador**. A opção `--no-open-index` existe apenas para testes automatizados ou ambientes sem interface; não a use ao entregar uma análise solicitada por uma pessoa.

Se houver vários nomes, conclua todos os relatórios, atualize o catálogo a cada geração e abra o índice uma vez, depois do último.

### 6. Entregue os resultados

Apresente de forma concisa:

1. Links locais clicáveis para cada relatório e para o índice geral, usando caminhos absolutos.
2. Data de corte e, quando eleitoral, o status exato de cada nome.
3. Destaques principais:
   - **Identificação**: Cargo, Partido, UF, Mandato.
   - **Remuneração & Gastos**: Salário base oficial e benefícios.
   - **Atuação Parlamentar**: Quantidade de proposições e temas de destaque.
   - **Patrimônio**: Último valor declarado no TSE.
   - **Investigações & Notícias**: Síntese dos principais tópicos com seus respectivos desfechos.
4. Lacunas relevantes e a advertência de que a síntese da IA deve ser conferida nas fontes vinculadas.

### 7. Retificação

Se a pessoa retratada apontar erro, ou se o dossiê tiver sido gerado fora do escopo da seção 0 de [legal-journalism-ethics.md](references/legal-journalism-ethics.md), retire-o do catálogo:

```bash
python3 scripts/generate_dossier_html.py --remove <Nome_Do_Arquivo>.html --apagar-html
```

Sem `--apagar-html` o relatório continua no disco e apenas sai do índice. Corrigir e regerar é preferível a remover: o rodapé passa a listar as revisões anteriores, o que mostra ao leitor que o documento mudou.

O trabalho só está concluído quando os arquivos existem, o catálogo os referencia e o índice foi aberto para navegação.
