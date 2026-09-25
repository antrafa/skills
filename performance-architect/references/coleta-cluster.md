# Coleta de Evidência em Cluster Kubernetes (somente leitura)

Use este arquivo quando o usuário oferecer acesso ao cluster. É opcional: se
ele não tiver acesso ou não quiser dar, siga a análise sem esta fonte e
marque as conclusões que dependiam dela como hipótese.

## Índice
- [Acesso: kubeconfig e allow-list](#acesso-kubeconfig-e-allow-list)
- [O que coletar, nesta ordem](#o-que-coletar-nesta-ordem)
- [Como ler cada saída](#como-ler-cada-saída)
- [Quando um comando falha](#quando-um-comando-falha)

## Acesso: kubeconfig e allow-list

Esta skill não exige a `cluster-analyzer` para coletar evidência de cluster
— o mínimo abaixo já é autossuficiente. **Se a skill `cluster-analyzer`
também estiver disponível**, prefira o protocolo completo dela (regras de
execução e passo 1): ela detalha melhor a confirmação de cliente/ambiente e a allow-list de
leitura, e evita manter a mesma regra de segurança em dois lugares.

Não reproduza a allow-list aqui nem monte uma própria. Ela já esteve escrita
em duplicado nos dois arquivos, e duas cópias de uma regra de segurança
divergem — a que divergir é a que vai autorizar um `rollout restart` num
ambiente com tráfego real. Uma cópia só, e ela vive na skill cuja razão de
existir é justamente o acesso somente leitura.

**Se a `cluster-analyzer` não estiver disponível** (esta skill sozinha), a regra não cai por falta de fonte — ela fecha. Vale este mínimo, e
nada além dele: `kubectl get`, `describe`, `logs`, `top`, `events`, `explain`,
`auth can-i`, `rollout status`, `rollout history`, e `helm list`, `get`,
`status`, `history`. Qualquer outro verbo, inclusive os que parecem inofensivos
(`exec`, `port-forward`, `debug`, `cp`), fica de fora. Diga ao usuário que está
operando com o mínimo por falta da `cluster-analyzer`, em uma linha — nunca preencha a
lacuna com uma allow-list improvisada.

O que continua valendo aqui, e não depende de enumerar comando nenhum:

- Antes do primeiro comando, descubra os kubeconfigs disponíveis
  (`$KUBECONFIG`, `~/.kube/config` e outros arquivos em `~/.kube/`),
  apresente os candidatos ao usuário e pergunte qual ambiente investigar — não adivinhe
  pelo nome do arquivo (`hml` e `prd` lado a lado é o erro mais caro
  possível aqui). Se o arquivo tiver mais de um contexto, confirme qual usar
  com `config get-contexts` antes de prosseguir.
- `--kubeconfig` e `--context` explícitos em **todo** comando. Nunca
  `use-context`, nunca `KUBECONFIG` global — troca de contexto vaza para os
  outros terminais do usuário.
- Nunca `cat` no kubeconfig: ele carrega certificado e token.
- Antes do primeiro comando, confirme em texto qual ambiente está sendo lido,
  para o usuário perceber na hora se está errado.

## O que coletar, nesta ordem

Um comando por vez. Mostre o comando, espere a saída, interprete antes do
próximo — cada resultado decide qual é a pergunta seguinte. Não encadeie
vários comandos de uma vez.

```bash
# 1. Topologia: quantas réplicas existem de fato, e onde
kubectl get deploy,sts,hpa -n <ns> -o wide

# 2. Dimensionamento declarado: requests, limits, probes, grace period
kubectl get deploy/<nome> -n <ns> -o yaml

# 3. Uso real vs declarado (exige metrics-server)
kubectl top pod -n <ns>
kubectl top node

# 4. Estado do HPA: por qual métrica escala, e se está no teto
kubectl describe hpa/<nome> -n <ns>

# 5. Histórico de restart e motivo (memória? probe?)
kubectl get pods -n <ns> -o wide
kubectl describe pod <pod> -n <ns>

# 6. Eventos recentes do namespace, do mais novo para o mais velho
kubectl get events -n <ns> --sort-by='.lastTimestamp'

# 7. Log da execução anterior, quando houve restart
kubectl logs <pod> -n <ns> --previous --tail=200

# 8. Se instalado por Helm: quais values estão realmente aplicados
helm get values <release> -n <ns>
```

Se possível, colete `top pod` **no horário de pico** — média de 24h esconde
exatamente o que se está investigando.

## Como ler cada saída

| O que olhar | Sinal de problema | O que significa para performance |
|---|---|---|
| `replicas` do Deployment | 1 réplica | nenhuma folga; todo deploy é indisponibilidade e não há escala horizontal |
| `resources.requests` vs `top pod` | uso muito acima do request | scheduling errado: o pod concorre por CPU que ninguém reservou |
| `resources.limits.cpu` | limite baixo e uso próximo dele | CPU throttling — aparece como latência em degraus, não como CPU alta |
| `resources.limits.memory` | igual ou próximo do heap da JVM | `OOMKilled` esperando o pico (metaspace, stacks e buffers diretos ficam fora do heap) |
| `describe pod` → `Last State` | `OOMKilled`, exit 137 | memória insuficiente sob carga real |
| `describe pod` → `Events` | `Liveness probe failed`, `Killing` | probe matando a aplicação sob carga ou no boot |
| `describe hpa` | métrica é CPU | CPU representa mal serviço que espera I/O; RPS ou profundidade de fila representam melhor |
| `describe hpa` | `desired = max` | está no teto: escalou tudo o que podia e não bastou |
| `get pods` → `Pending` | pod não agendado | teto do HPA maior do que o cluster consegue alocar |
| `terminationGracePeriodSeconds` | ausente ou muito curto | rolling update descarta requisições em voo — em centenas de req/s, um deploy vira incidente |
| `readinessProbe` | ausente | tráfego chega antes de a aplicação estar pronta; pico de erro a cada deploy |
| `RESTARTS` acumulados | crescendo no pico | o problema é de carga, não de configuração inicial |

Métrica de throttling, quando houver Prometheus, é a confirmação direta:
`rate(container_cpu_cfs_throttled_seconds_total[5m])` > 0 significa que o
`limits.cpu` está segurando a aplicação.

## Quando um comando falha

- `403 Forbidden` é esperado e faz parte do modelo de permissão. Não tente
  contornar, não procure credencial alternativa, não sugira ampliar
  permissão. Reporte o que a falta de acesso significa para a análise e siga
  por outro caminho de leitura.
- `metrics-server` ausente derruba o `top`. Sem ele, não há uso real — diga
  isso e trate o dimensionamento como hipótese.
- **Nunca preencha de memória a saída de um comando.** Se não rodou, diga que
  não rodou. Saída inventada é o pior defeito possível nesta análise.
