# Insumos da análise

Só o **objetivo** é obrigatório. Todo o resto é opcional e pulável: o usuário
raramente tem tudo em mãos, e uma análise com metade dos dados e as lacunas
declaradas vale mais que uma análise travada esperando dado que não vai
chegar. Quando um insumo falta, a conclusão que dependia dele entra no
relatório como **hipótese não verificada**, junto da medição que a
resolveria.

| Insumo | Para que serve | Como o usuário fornece | Se faltar |
|---|---|---|---|
| **Objetivo** (tipo + número + prazo) | Define o que é "bom". Sem ele não há análise, há opinião | "Aguentar 6M/dia com p95 < 300 ms até março" / "cortar 30% do custo mantendo o SLO" | Pergunte. É a única pergunta que bloqueia |
| Escopo | Quais serviços entram, quais não; o que é dependência externa | Nomes dos serviços/repos, diagrama, ou "é esse repo aqui" | Assuma o repo indicado e declare o recorte |
| Repositórios | Caminho crítico de ponta a ponta, transação, pools, clientes HTTP, DDL | Caminho do repositório | Análise fica sem causa raiz de código; só sintomas |
| Manifests / Helm / compose | Réplicas, `requests`/`limits`, HPA, probes, JVM flags, shutdown | Caminho ou colar | Dimensionamento vira hipótese |
| Cluster (read-only) | Uso real vs declarado, restarts, OOM, throttling, eventos, nós | kubeconfig + namespace (ver `coleta-cluster.md`) | Sem uso real; declare |
| Métricas / APM / dashboards | p95/p99 por endpoint, saturação de pool, GC, erros, RPS real | Colar, exportar, ou dar acesso de leitura | Fator de pico vira premissa da tabela; sem breakdown de latência |
| Logs (janela de pico, 24 h) | Volume atual por hora, rajadas, erros reais em produção, restarts | Arquivo ou `kubectl logs` na allow-list | Volume atual vira declarado, não medido |
| Banco | DDL, tamanho das tabelas, `EXPLAIN` do caminho crítico, top queries, tipo de PK, índices, partições | Colar ou apontar os arquivos de migração | Banco vira caixa-preta na tabela de gargalos |
| Volumetria de negócio | Volume hoje e no alvo, distribuição no dia, anexos, retenção | Números, mesmo aproximados | Defaults de `volumetria.md`, marcados como premissa |
| Restrições | Orçamento, prazo, tecnologias vetadas ou obrigatórias, contratos com clientes/fabricantes, janelas de manutenção, licenças | Texto livre | Proposta pode sugerir o que não pode ser feito; pergunte se suspeitar |
| Público dos relatórios | Quem lê o técnico, quem lê o gerencial, que decisão cada um toma | "Time de dev + coordenação e diretoria" | Assuma time técnico + gestor não técnico |

Essa lista vai ao usuário **em uma mensagem só**, na Fase 0.
