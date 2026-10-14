# Sintoma → causa provável (somente leitura)

Tabela de apoio para montar as hipóteses do Passo 2. Cobre só o que dá para
confirmar ou descartar com os comandos do allow-list — nenhuma entrada aqui
depende de `exec`, `debug` ou qualquer verbo fora das *Regras de execução*.

| Sintoma (`kubectl get pods`) | Causas mais prováveis | Onde confirmar |
|---|---|---|
| `CrashLoopBackOff` | Aplicação crasha ao iniciar (erro de config, dependência indisponível), liveness probe matando o processo antes dele ficar pronto, falta de memória (ver `OOMKilled` no describe) | `kubectl logs --previous`, `kubectl describe pod` (seção `Last State`) |
| `ImagePullBackOff` / `ErrImagePull` | Tag de imagem errada/inexistente, registry privado sem `imagePullSecrets`, rate limit do registry | `kubectl describe pod` (evento `Failed to pull image`) |
| `Pending` | Sem node com recursos suficientes (CPU/mem request alto demais), `nodeSelector`/`affinity` sem node compatível, PVC não bindou | `kubectl describe pod` (seção `Events`, ex. `FailedScheduling`) |
| `OOMKilled` (visível em `describe` → `Last State: Terminated, Reason: OOMKilled`) | `resources.limits.memory` menor que o uso real da aplicação | `kubectl top pod` ao longo do tempo, não só um snapshot |
| Readiness nunca fica `Ready` mas o pod está `Running` | Endpoint de readiness não responde a tempo, porta errada no probe, app demora mais que `initialDelaySeconds` para subir | `kubectl describe pod` (evento de probe falhando), `kubectl logs` |
| Deploy "trava" (nunca completa rollout) | `maxUnavailable`/`maxSurge` incompatível com o número de réplicas, novo pod nunca fica `Ready` (ver linha acima), `PodDisruptionBudget` bloqueando | `kubectl rollout status`, `kubectl describe deploy` |
| Pod reiniciando sem erro aparente no log (`RESTARTS` subindo) | Kill por OOM ou liveness antes da app logar algo, app que sai com código 0 e é reiniciada pela `restartPolicy` | `kubectl describe pod` (`Last State`: `Reason` e `Exit Code`; `Events` de probe) |
| Pod `Evicted` (o pod some e outro nasce com nome novo — não conta em `RESTARTS`) | Node sob pressão de memória/disco (`MemoryPressure`/`DiskPressure`), pod sem `requests` sendo o primeiro despejado | `kubectl get pods --field-selector status.phase=Failed`, `kubectl describe node <node>` (`Conditions`) |
| Service sem tráfego chegando aos pods | `selector` do Service não bate com os `labels` do pod | `kubectl get endpoints <service>` vazio é o sinal mais direto |
| Ingress sem efeito | `ingressClassName` não corresponde ao controller do cluster, ou Service referenciado não existe no namespace do Ingress | `kubectl describe ingress`, `kubectl get svc -n <namespace>` |
| PVC preso em `Pending` | Sem `StorageClass`/`PV` compatível disponível. Com `volumeBindingMode: WaitForFirstConsumer` o `Pending` é normal até um pod usar o PVC — não é erro | `kubectl get pvc -n <namespace>`, `kubectl describe pvc`, `kubectl get storageclass` |
| Pod preso em `ContainerCreating` com `Multi-Attach error` | Dois pods em nodes diferentes montando o mesmo PVC `ReadWriteOnce` (comum em rollout com `RollingUpdate` de deploy com volume RWO) | `kubectl describe pod` (evento `FailedAttachVolume`/`Multi-Attach`) |

## Parece problema, mas é normal

A coluna da direita é o que separa o falso alarme do problema real. Sem ela,
toda linha estranha vira hipótese e a investigação se dispersa.

| Observado | Por que costuma ser normal | Vira problema quando |
|---|---|---|
| `RESTARTS` alto | O contador é da vida inteira do pod; o último restart pode ter dias (`kubectl get pods` mostra `5 (3d ago)`) | O último restart é recente ou o número sobe enquanto você observa |
| Pods `Evicted` ou `Failed` antigos na lista | Histórico que ninguém limpou; não consome recurso | Aparecem pods novos nesse estado |
| Pods `Completed` | Execução normal de `Job`/`CronJob` | Ficam em `Error`, ou o `Job` nunca chega a `Completed` |
| `Readiness probe failed` nos primeiros segundos | App ainda subindo; o pod fica `Ready` logo depois | Continua depois do `Ready`, ou o pod nunca fica `Ready` |
| Memória perto do limit em `top pod`, numa JVM | A JVM reserva heap e não devolve; uso alto e estável é o esperado | Há `OOMKilled` no `Last State` ou o uso cresce sem parar |
| Endpoints vazio ou deploy com `0/0` | Alguém escalou para zero de propósito (manutenção, desligamento) | O values/manifest no git declara réplicas > 0 e ninguém sabe do desligamento |
| HPA no mínimo de réplicas | Fora do horário de pico | Sob carga e sem escalar; ou `FailedGetResourceMetric` muito depois do deploy |
| PVC `Pending` com `WaitForFirstConsumer` | Só faz bind quando um pod usa o PVC | Há pod usando o PVC e ele continua `Pending` |
| 404 do proxy em `/app` sem barra final | A rota declara o prefixo `/app/` | `/app/` com barra também falha |

## Onde nasce o erro HTTP

Quando o sintoma é "a URL dá erro", descubra primeiro **quem respondeu**: o
proxy de entrada (Istio/Envoy, ingress-nginx) ou a aplicação. Um GET que só
imprime os cabeçalhos responde isso:

```bash
curl -sk -m 15 -o /dev/null -D - https://<host>/<caminho>/
```

| Resposta | Quem respondeu | Próxima leitura |
|---|---|---|
| 503 `no healthy upstream`, `content-type: text/plain`, sem `x-envoy-upstream-service-time` | Envoy, sem destino saudável | `get endpoints <svc>` vazio, deploy com 0 réplicas, `targetPort` errado, rota apontando para Service que não existe |
| 502/503/504 com página HTML do ingress-nginx | Ingress controller | Endpoints e readiness do backend; timeout configurado nas annotations do Ingress |
| 404 do proxy | Nenhuma rota casou | Host e prefixo declarados no Ingress/VirtualService; ver a linha da barra final acima |
| 500, 401, 302 ou 200 com `x-envoy-upstream-service-time` (ou cabeçalho próprio da app) | A aplicação | `logs` do pod no horário da chamada |

Dois objetos de rota declarando o mesmo host e prefixo é sinal de objeto
órfão: um recurso foi renomeado, o `kubectl apply` criou o novo e não apagou
o antigo, e o antigo pode estar vencendo. Liste as rotas do namespace
(`get virtualservice,ingress -o wide`) e compare hosts e prefixos.

## Funciona num ambiente e não no outro

Quase sempre a diferença é variável de ambiente ou infraestrutura (memória,
certificado, rota), não versão. Compare nesta ordem:

1. Imagem e tag de cada container — `get deploy <nome> -o wide` nos dois.
2. Variáveis de ambiente — `scripts/envdiff.py`, que lê o deploy e os
   ConfigMaps referenciados nos dois lados e mostra o que só existe num deles
   e o que difere. Valores com cara de credencial saem mascarados, e Secret
   nunca é lido: aparece só como referência.
3. `resources`, probes e réplicas — `get deploy <nome> -o yaml` nos dois.

## Lendo `describe` e `events` corretamente

`kubectl describe pod` tem duas seções que resolvem a maioria dos casos antes
de qualquer outra investigação:

- **`Last State`**: mostra `Reason` (`OOMKilled`, `Error`, `Completed`) e
  `Exit Code` da execução anterior — o exit code costuma indicar se foi crash
  da aplicação (código não-zero definido pela app) ou kill do sistema
  (137 = SIGKILL, geralmente OOM).
- **`Events`**: ordem cronológica do que o scheduler/kubelet tentou fazer.
  Leia de cima para baixo — o primeiro evento de erro geralmente é a causa
  raiz, os seguintes costumam ser repetições/consequência.

Eventos somem do cluster depois de um tempo (TTL padrão de 1 hora no kube-apiserver); se o pod já
não existe mais e o `describe` não mostra nada útil, procure em
`kubectl get events` filtrado por `--field-selector involvedObject.name=<pod>`
enquanto ainda estiver disponível.

## Relacionado

A skill `devops-expert`, se estiver disponível, documenta a mesma tabela com
a correção de manifest correspondente a cada causa (requests/limits, probes,
securityContext). Use-a depois desta análise, quando já tiver a causa
confirmada e quiser o YAML corrigido — esta skill não precisa dela para
diagnosticar.
