# Kubernetes — Diagnóstico e Boas Práticas

## Índice
- [Comandos de inspeção](#comandos-de-inspeção)
- [Sintoma → causa provável](#sintoma--causa-provável)
- [Lendo `describe` e `events` corretamente](#lendo-describe-e-events-corretamente)
- [Manifests: requests/limits](#manifests-requestslimits)
- [Probes (liveness/readiness/startup)](#probes-livenessreadinessstartup)
- [securityContext mínimo](#securitycontext-mínimo)
- [Rede: Service, Ingress, DNS](#rede-service-ingress-dns)
- [Storage: PVC/PV](#storage-pvcpv)

## Comandos de inspeção

Sempre comece pela visão geral, depois desça para o pod específico:

```bash
kubectl get pods -n <namespace> -o wide          # estado, node, restarts
kubectl get pods -n <namespace> --sort-by=.status.startTime
kubectl describe pod <pod> -n <namespace>        # eventos, causa do estado atual
kubectl logs <pod> -n <namespace> --previous      # log da execução anterior (crash)
kubectl logs <pod> -n <namespace> -c <container>  # pod com múltiplos containers
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
kubectl top pod -n <namespace>                    # uso real de CPU/mem (requer metrics-server)
kubectl get deploy,rs,pod -n <namespace> -l app=<label>  # cadeia Deployment → ReplicaSet → Pod
kubectl rollout status deploy/<nome> -n <namespace>
kubectl rollout history deploy/<nome> -n <namespace>
```

Para investigar dentro do container sem alterar a imagem de produção, use um
container de debug efêmero em vez de instalar ferramentas na imagem real:

```bash
kubectl debug -it <pod> -n <namespace> --image=busybox --target=<container>
```

`kubectl debug` **escreve no cluster**: adiciona um container efêmero ao pod,
que fica registrado nele até o pod ser recriado. Entregue o comando para o
usuário rodar; não é inspeção somente leitura.

## Sintoma → causa provável

| Sintoma (`kubectl get pods`) | Causas mais prováveis | Onde confirmar |
|---|---|---|
| `CrashLoopBackOff` | Aplicação crasha ao iniciar (erro de config, dependência indisponível), liveness probe matando o processo antes dele ficar pronto, falta de memória (ver `OOMKilled` no describe) | `kubectl logs --previous`, `kubectl describe pod` (seção `Last State`) |
| `ImagePullBackOff` / `ErrImagePull` | Tag de imagem errada/inexistente, registry privado sem `imagePullSecrets`, rate limit do registry | `kubectl describe pod` (evento `Failed to pull image`) |
| `Pending` | Sem node com recursos suficientes (CPU/mem request alto demais), `nodeSelector`/`affinity` sem node compatível, PVC não bindou | `kubectl describe pod` (seção `Events`, ex. `FailedScheduling`) |
| `OOMKilled` (visível em `describe` → `Last State: Terminated, Reason: OOMKilled`) | `resources.limits.memory` menor que o uso real da aplicação; em JVM, heap sem teto relativo ao limit do container | Ajustar limit com base em `kubectl top pod` ao longo do tempo, não só um snapshot; em JVM, ajustar o heap junto (ver [requests/limits](#manifests-requestslimits)) |
| Readiness nunca fica `Ready` mas o pod está `Running` | Endpoint de readiness não responde a tempo, porta errada no probe, app demora mais que `initialDelaySeconds` para subir | `kubectl describe pod` (evento de probe falhando), logs da app |
| Deploy "trava" (nunca completa rollout) | `maxUnavailable`/`maxSurge` incompatível com o número de réplicas, novo pod nunca fica `Ready` (ver linha acima), `PodDisruptionBudget` bloqueando | `kubectl rollout status`, `kubectl describe deploy` |
| Pod reiniciando sem erro aparente no log | Node sob pressão de memória/disco fazendo eviction, `SIGTERM` não tratado pela app (kill forçado após `terminationGracePeriodSeconds`) | `kubectl describe pod` (seção `Reason`), `kubectl describe node <node>` (`Conditions`) |

## Lendo `describe` e `events` corretamente

`kubectl describe pod` tem duas seções que resolvem a maioria dos casos antes
de qualquer outra investigação:

- **`Last State`**: mostra `Reason` (`OOMKilled`, `Error`, `Completed`) e
  `Exit Code` da execução anterior. Código não-zero definido pela app é crash
  da aplicação. 137 é SIGKILL: só é falta de memória quando vem com
  `Reason: OOMKilled`; com `Reason: Error`, costuma ser o kubelet matando um
  processo que não encerrou dentro do `terminationGracePeriodSeconds` (ex.:
  após liveness falhar). 143 é SIGTERM tratado pela app.
- **`Events`**: ordem cronológica do que o scheduler/kubelet tentou fazer.
  Leia de cima para baixo — o primeiro evento de erro geralmente é a causa
  raiz, os seguintes costumam ser repetições/consequência.

Eventos ficam no cluster por 1h por padrão (`--event-ttl` do apiserver); se o pod já
não existe mais e o `describe` não mostra nada útil, procure em
`kubectl get events` filtrado por `--field-selector involvedObject.name=<pod>`
enquanto ainda estiver disponível, ou nos logs centralizados do cluster
(ex.: agregador de logs do ambiente), se existir.

## Manifests: requests/limits

Sempre declare `requests` de CPU e memória e `limits` de memória — sem
requests o scheduler não tem como decidir bem, e sem limit de memória um pod
pode consumir toda a memória do node e afetar vizinhos.

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "256Mi"
```

- `requests` é o que o scheduler reserva ao decidir em qual node colocar o
  pod — dimensione pelo uso normal, não pelo pico.
- `limits` de memória deve ter alguma folga sobre o uso real observado
  (`kubectl top pod` ao longo do tempo, não um único snapshot) — limit
  igual ao uso médio garante `OOMKilled` no primeiro pico.
- Limit de CPU é decisão caso a caso: ele não mata o pod, mas faz throttling
  (a aplicação é freada mesmo com o node ocioso), e o boot de JVM é onde isso
  mais aparece. Quando o time exigir limit de CPU, dimensione com folga para o
  startup.
- **JVM**: o limit de memória do container cobre heap + metaspace + threads +
  buffers nativos. Fixe o heap relativo ao limit
  (`JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75`, ou `-Xmx` explícito) e suba os
  dois juntos; aumentar só o limit deixa o heap crescer até bater nele de novo.
- Não copie `requests`/`limits` de outro serviço "porque parece razoável" —
  cada aplicação tem perfil de consumo diferente; meça antes de fixar.

## Probes (liveness/readiness/startup)

- **`readinessProbe`**: decide se o pod recebe tráfego do Service. Falha aqui
  não reinicia o pod, só o tira da lista de endpoints — é o probe certo para
  "app está temporariamente sobrecarregada, mas viva".
- **`livenessProbe`**: falha aqui mata e reinicia o container. Um liveness
  mal calibrado (timeout curto, endpoint pesado) causa reinícios em cascata
  sob carga — quando um app está lento mas funcional, isso pode ser confundido
  com `CrashLoopBackOff` de causa raiz completamente diferente.
- **`startupProbe`**: use para apps com boot lento, para o liveness só
  começar a contar depois que a app realmente inicializou — evita que o
  liveness mate o pod ainda durante o startup normal.

```yaml
readinessProbe:
  httpGet: { path: /health/ready, port: 8080 }
  initialDelaySeconds: 5
  periodSeconds: 10
livenessProbe:
  httpGet: { path: /health/live, port: 8080 }
  initialDelaySeconds: 15
  periodSeconds: 20
  failureThreshold: 3
```

Nunca aponte liveness/readiness para o mesmo endpoint de "health geral" que
depende de recursos externos (banco, fila) — se o banco cair, isso derruba
todos os pods da aplicação via liveness em vez de só marcar como not-ready.

## securityContext mínimo

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

Rode como root ou com filesystem gravável só se a aplicação exigir de forma
comprovada (ex.: grava cache local) — nesse caso, monte um `volume` específico
gravável em vez de liberar o filesystem inteiro.

## Rede: Service, Ingress, DNS

- Um Service não encontra pods → confira se o `selector` do Service bate
  exatamente com os `labels` do pod (`kubectl get endpoints <service>` vazio
  é o sinal mais direto).
- DNS interno resolve como `<service>.<namespace>.svc.cluster.local` — erros
  de resolução cruzando namespace geralmente são nome incompleto.
- Ingress sem efeito: confira se o Ingress Controller do cluster corresponde
  à `ingressClassName` declarada, e se o Service referenciado existe no mesmo
  namespace do Ingress.

## Storage: PVC/PV

- Pod em `Pending` por `FailedScheduling` relacionado a volume: o PVC não
  bindou. Cheque `kubectl get pvc -n <namespace>` — `Pending` ali indica que
  não há `StorageClass`/`PV` compatível disponível.
- Nunca aponte dois pods de escrita para o mesmo PVC com `ReadWriteOnce` em
  nodes diferentes — isso trava o segundo pod em `Pending`, não é bug do
  agendador.
