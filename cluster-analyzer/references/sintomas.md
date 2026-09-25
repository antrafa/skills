# Sintoma → causa provável (somente leitura)

Tabela de apoio para montar as hipóteses do Passo 3. Cobre só o que dá para
confirmar ou descartar com os comandos do allow-list — nenhuma entrada aqui
depende de `exec`, `debug` ou qualquer verbo fora do Passo 2.

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
