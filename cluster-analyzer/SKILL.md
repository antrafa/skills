---
name: cluster-analyzer
description: 'Diagnóstico somente leitura de cluster Kubernetes, confirmando o kubeconfig e o contexto certos quando há vários ambientes ou clientes. Use when o usuário pedir para investigar um cluster, pod, deploy ou ingress de um ambiente ("pod reiniciando no cluster do cliente X", "dá uma olhada na homologação"). Do NOT use for escrever ou aplicar a correção (manifest, Helm, pipeline) nem para qualquer operação que altere o cluster.'
license: MIT
metadata:
  author: Antonio Rafael Ortega
  version: 1.0.0
  category: cloud
  product: all
  stack: all
---

# Cluster Analyzer (somente leitura)

Diagnóstico de cluster Kubernetes agindo como **observador, nunca como
operador**. É comum haver vários kubeconfigs (um por cliente ou ambiente)
ou vários contextos num mesmo arquivo — o primeiro passo é sempre descobrir
e confirmar qual usar, nunca assumir o contexto atual do `kubectl`.

## Regras de execução (valem a sessão inteira)

Este acesso é para diagnóstico. Você atua como observador do início ao fim
da conversa — mesmo que o usuário peça para "corrigir" algo durante a
análise. Se o diagnóstico apontar para uma correção, descreva o comando de
escrita num bloco separado, explique o impacto esperado e devolva a decisão
e a execução para o usuário.

**Todo comando leva `--kubeconfig <arquivo> --context <contexto>`
explícitos** (e `--namespace` quando aplicável). Nunca troque o contexto
atual do usuário (`kubectl config use-context`) nem exporte `KUBECONFIG`
global — isso evita que uma troca de contexto "vaze" para fora desta tarefa
e afete outro terminal do usuário.

**Permitido (allow-list — nada fora disto):**
- `kubectl get / describe / logs / top / events`
- `kubectl explain`, `api-resources`, `version`, `auth can-i`,
  `config get-contexts`
- `kubectl rollout status`, `kubectl rollout history` (só estes dois — são
  leitura pura, e a tabela de sintoma → causa depende deles para diagnosticar
  deploy travado)
- Flags de saída: `-o yaml`, `-o json`, `-o wide`, `--show-labels`, `--sort-by`
- `helm list`, `helm get`, `helm status`, `helm history`
- Pipe para filtro local que só lê a saída: `grep`, `jq`, `head`, `tail`,
  `sort`, `wc`

**Proibido (qualquer comando fora do allow-list, incluindo):**
`apply`, `create`, `patch`, `replace`, `edit`, `delete`, `scale`, `set`,
`label`, `annotate`, `rollout restart`/`undo`/`pause`, `cordon`, `drain`,
`uncordon`, `taint`, `exec`, `cp`, `attach`, `port-forward`, `proxy`, `run`,
`debug`, `helm install`/`upgrade`/`uninstall`/`rollback`, `kubectl config
set-*`, `--force`, `--dry-run=server`, e pipe para qualquer coisa que
execute comando (`xargs`, `sh`, `bash`, `kubectl`).

**Limites de uso:**
- `logs` sempre com `--tail=200` (ou `--since=<janela>`); aumente só se as
  200 linhas não mostrarem o erro. Log sem limite despeja milhares de linhas
  e soterra a evidência.
- `top` depende do metrics-server. Se falhar com `Metrics API not
  available`, diga isso e use `resources` no `get pod -o yaml` e o
  `Last State` do `describe` no lugar.
- Antes do primeiro `helm`, rode `command -v helm`. Sem `helm`, identifique
  o release pelos labels (`app.kubernetes.io/managed-by`, `helm.sh/chart`,
  `app.kubernetes.io/instance`) — os secrets `sh.helm.release.v1.*` guardam
  o values com senha e ficam fora da investigação.

**Segredo aparece como nome e tamanho, nunca como valor.** `get` está no
allow-list, mas o que ele devolve de sensível não entra na resposta:
- Secret: use `describe secret` (mostra chaves e tamanhos, sem valor). Para
  saber só quais chaves existem: `get secret <nome> -o jsonpath='{.data}' |
  jq 'keys'`. Base64 não é proteção — `get secret -o yaml` expõe a senha.
- Em `get configmap`, `get pod/deploy -o yaml` (bloco `env`) e `helm get
  values`/`helm get all`, qualquer valor com cara de credencial (senha,
  token, chave, connection string com usuário/senha) sai como `***`.
- Kubeconfig: inspecione só com `config get-contexts`; o arquivo bruto
  (`cat <kubeconfig>`) carrega certificados e tokens.

**Log de produção carrega dado pessoal de cidadão.** Resuma o que o log
mostra (erro, horário, frequência) e mascare CPF, e-mail e nome de pessoa
nos trechos citados.

## Passo 1 — Escolher o kubeconfig

Liste os arquivos de configuração disponíveis antes de perguntar qualquer
coisa — não peça ao usuário para lembrar o nome do arquivo de cabeça:

```bash
echo "$KUBECONFIG"; ls -p ~/.kube/ 2>/dev/null
```

Candidatos: os arquivos listados em `$KUBECONFIG`, o `~/.kube/config` e os
demais kubeconfigs em `~/.kube/` (ignore diretórios como `cache/` e
`http-cache/`).

Responda com a lista encontrada, a pergunta de qual ambiente investigar e,
**na mesma mensagem**, as hipóteses do Passo 2 — elas não dependem do
ambiente, e o usuário pode corrigir o rumo junto com a confirmação. Os nomes
de arquivo geralmente seguem `<cliente>-<ambiente>[-<plataforma>].yaml`
(ex.: `clientea-hml.yaml`, `clienteb-prd-oke.yaml`), mas **confirme o
cliente/ambiente com o usuário em vez de deduzir pelo nome** — clientes
diferentes podem ter siglas parecidas, e escolher `prd` em vez de `hml` é
exatamente o tipo de engano caro demais para arriscar. Se a lista for longa,
pergunte em texto livre em vez de tentar encaixar tudo numa pergunta de
múltipla escolha.

Depois de escolhido o arquivo, rode e informe o(s) contexto(s) contido(s)
nele (um kubeconfig pode ter mais de um):

```bash
kubectl --kubeconfig <caminho-escolhido> config get-contexts
```

Se houver mais de um contexto, confirme qual usar.

**Concluído quando:** o usuário confirmou arquivo e contexto, e você
escreveu em texto qual ambiente vai investigar — ele precisa conseguir ler
isso e perceber na hora se está errado.

## Passo 2 — Hipóteses ranqueadas

Escreva as 3 a 4 causas mais prováveis do sintoma relatado, em ordem de
probabilidade, e qual comando de leitura confirma ou descarta cada uma.
Isso transforma a sessão numa investigação dirigida (cada saída elimina
hipóteses) em vez de uma coleta de comandos "para ver o que aparece" — e
deixa o usuário reordenar se souber de algo (ex.: "teve deploy hoje de
manhã").

Exemplo para "pod reiniciando direto":

1. `OOMKilled` — limit de memória abaixo do uso real. Confirma em
   `describe pod` (`Last State: Reason: OOMKilled`, exit 137) e `top pod`.
2. Liveness probe agressiva matando a app durante o boot ou sob carga.
   Confirma nos `Events` do `describe` (`Liveness probe failed`, `Killing`)
   e no tempo de startup no `logs --previous`.
3. Dependência externa indisponível (banco, fila, serviço de auth) fazendo
   a app abortar no startup. Confirma no fim do `logs --previous`
   (stack trace de conexão, `Connection refused`, `ORA-`, timeout).
4. Deploy recente com imagem/config quebrada. Confirma em
   `rollout history deploy/<nome>` e `get deploy -o yaml` (imagem, env).

Para outros sintomas, monte a lista a partir de `references/sintomas.md`
(tabela sintoma → causa, escrita só com comandos do allow-list) e da
evidência — sem causas que nenhuma das duas sustenta.

## Passo 3 — Investigar

1. Um comando por vez. Mostre o comando antes de rodar, espere o
   resultado, interprete a saída antes do próximo passo — cada resultado
   deve influenciar a próxima pergunta de diagnóstico, exatamente como
   investigar um bug.
2. Se um comando falhar com `403 Forbidden`, isso é esperado e faz parte do
   modelo de permissão — não tente contornar, não procure credencial
   alternativa, não sugira ampliar a permissão. Reporte o que a falta de
   acesso significa para o diagnóstico e siga por outro caminho de leitura
   disponível.
3. Relate só saída de comando que você de fato rodou. Se não rodou, diga
   que não rodou.

**Concluído quando:** cada hipótese do Passo 2 está marcada como
*confirmada*, *descartada* ou *bloqueada* (403, metrics-server ausente,
evento já expirado), cada marcação apoiada no comando e no trecho de saída
que a sustenta. Se todas foram descartadas, isso também é um resultado:
diga quais foram descartadas e qual leitura sugere a próxima hipótese.

## Encerrando a análise

Resuma o que foi encontrado (sintoma, evidência coletada, qual hipótese
do Passo 2 se confirmou e quais foram descartadas) e, se houver uma
correção necessária, apresente-a em bloco separado para o usuário revisar
e aplicar — nunca aplicada por esta skill.

Antes de escrever a correção, veja quem gerencia o recurso — os labels já
vêm no `get -o yaml` / `--show-labels`:

- `app.kubernetes.io/managed-by: Helm`, `helm.sh/chart` ou anotação
  `meta.helm.sh/release-name`: a correção vai no values/chart do release (em
  geral no repositório do ambiente do cliente). Um `kubectl set`/`patch`
  direto é desfeito no próximo `helm upgrade`, e o problema volta sem
  ninguém saber por quê. Aponte o campo do values a mudar; para escrever o
  manifest/values corrigido, a skill `devops-expert` entra depois.
- Recurso sem gerenciador aparente: o comando `kubectl` de escrita
  correspondente, com o impacto esperado (ex.: "gera novo rollout").
