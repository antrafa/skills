# Kubernetes — Diagnosis and Good Practices

## Contents
- [Inspection commands](#inspection-commands)
- [Symptom → likely cause](#symptom--likely-cause)
- [Reading `describe` and `events` correctly](#reading-describe-and-events-correctly)
- [Manifests: requests/limits](#manifests-requestslimits)
- [Probes (liveness/readiness/startup)](#probes-livenessreadinessstartup)
- [Minimal securityContext](#minimal-securitycontext)
- [Networking: Service, Ingress, DNS](#networking-service-ingress-dns)
- [Storage: PVC/PV](#storage-pvcpv)

## Inspection commands

Always start from the overview, then drill down to the specific pod:

```bash
kubectl get pods -n <namespace> -o wide          # state, node, restarts
kubectl get pods -n <namespace> --sort-by=.status.startTime
kubectl describe pod <pod> -n <namespace>        # events, cause of the current state
kubectl logs <pod> -n <namespace> --previous      # log of the previous run (crash)
kubectl logs <pod> -n <namespace> -c <container>  # pod with multiple containers
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
kubectl top pod -n <namespace>                    # real CPU/mem usage (requires metrics-server)
kubectl get deploy,rs,pod -n <namespace> -l app=<label>  # Deployment → ReplicaSet → Pod chain
kubectl rollout status deploy/<nome> -n <namespace>
kubectl rollout history deploy/<nome> -n <namespace>
```

To investigate inside the container without changing the production image,
use an ephemeral debug container instead of installing tools in the real
image:

```bash
kubectl debug -it <pod> -n <namespace> --image=busybox --target=<container>
```

`kubectl debug` **writes to the cluster**: it adds an ephemeral container to
the pod, which stays registered on it until the pod is recreated. Hand the
command to the user to run; it is not read-only inspection.

## Symptom → likely cause

| Symptom (`kubectl get pods`) | Most likely causes | Where to confirm |
|---|---|---|
| `CrashLoopBackOff` | Application crashes on start (config error, dependency unavailable), liveness probe killing the process before it is ready, lack of memory (see `OOMKilled` in describe) | `kubectl logs --previous`, `kubectl describe pod` (`Last State` section) |
| `ImagePullBackOff` / `ErrImagePull` | Wrong/nonexistent image tag, private registry without `imagePullSecrets`, registry rate limit | `kubectl describe pod` (`Failed to pull image` event) |
| `Pending` | No node with enough resources (CPU/mem request too high), `nodeSelector`/`affinity` with no compatible node, PVC did not bind | `kubectl describe pod` (`Events` section, e.g. `FailedScheduling`) |
| `OOMKilled` (visible in `describe` → `Last State: Terminated, Reason: OOMKilled`) | `resources.limits.memory` lower than the application's real usage; on the JVM, heap without a ceiling relative to the container limit | Adjust the limit based on `kubectl top pod` over time, not just one snapshot; on the JVM, adjust the heap with it (see [requests/limits](#manifests-requestslimits)) |
| Readiness never becomes `Ready` but the pod is `Running` | Readiness endpoint does not respond in time, wrong port in the probe, app takes longer than `initialDelaySeconds` to come up | `kubectl describe pod` (probe failing event), app logs |
| Deploy "hangs" (rollout never completes) | `maxUnavailable`/`maxSurge` incompatible with the number of replicas, new pod never becomes `Ready` (see row above), `PodDisruptionBudget` blocking | `kubectl rollout status`, `kubectl describe deploy` |
| Pod restarting with no apparent error in the log | Node under memory/disk pressure causing eviction, `SIGTERM` not handled by the app (forced kill after `terminationGracePeriodSeconds`) | `kubectl describe pod` (`Reason` section), `kubectl describe node <node>` (`Conditions`) |

## Reading `describe` and `events` correctly

`kubectl describe pod` has two sections that settle most cases before any
other investigation:

- **`Last State`**: shows the `Reason` (`OOMKilled`, `Error`, `Completed`)
  and `Exit Code` of the previous run. A non-zero code defined by the app is
  an application crash. 137 is SIGKILL: it is only lack of memory when it
  comes with `Reason: OOMKilled`; with `Reason: Error`, it is usually the
  kubelet killing a process that did not exit within
  `terminationGracePeriodSeconds` (e.g. after liveness fails). 143 is SIGTERM
  handled by the app.
- **`Events`**: chronological order of what the scheduler/kubelet tried to
  do. Read top to bottom — the first error event is usually the root cause,
  the following ones are usually repetitions/consequences.

Events stay in the cluster for 1h by default (the apiserver's
`--event-ttl`); if the pod no longer exists and `describe` shows nothing
useful, look in `kubectl get events` filtered by
`--field-selector involvedObject.name=<pod>` while it is still available, or
in the cluster's centralized logs (e.g. the environment's log aggregator), if
there is one.

## Manifests: requests/limits

Always declare CPU and memory `requests` and memory `limits` — without
requests the scheduler cannot decide well, and without a memory limit a pod
can consume all of the node's memory and affect its neighbours.

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "256Mi"
```

- `requests` is what the scheduler reserves when deciding which node to
  place the pod on — size it by normal usage, not by peak.
- The memory `limits` must have some headroom over the observed real usage
  (`kubectl top pod` over time, not a single snapshot) — a limit equal to the
  average usage guarantees `OOMKilled` on the first peak.
- A CPU limit is a case-by-case decision: it does not kill the pod, but it
  causes throttling (the application is slowed down even with the node idle),
  and JVM boot is where this shows the most. When the team requires a CPU
  limit, size it with headroom for startup.
- **JVM**: the container memory limit covers heap + metaspace + threads +
  native buffers. Pin the heap relative to the limit
  (`JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75`, or an explicit `-Xmx`) and
  raise both together; raising only the limit lets the heap grow until it
  hits it again.
- Do not copy `requests`/`limits` from another service "because it looks
  reasonable" — each application has a different consumption profile;
  measure before pinning.

## Probes (liveness/readiness/startup)

- **`readinessProbe`**: decides whether the pod receives traffic from the
  Service. A failure here does not restart the pod, it only removes it from
  the list of endpoints — it is the right probe for "the app is temporarily
  overloaded, but alive".
- **`livenessProbe`**: a failure here kills and restarts the container. A
  badly calibrated liveness (short timeout, heavy endpoint) causes cascading
  restarts under load — when an app is slow but functional, this can be
  mistaken for a `CrashLoopBackOff` with a completely different root cause.
- **`startupProbe`**: use it for apps with slow boot, so liveness only starts
  counting after the app has really initialized — keeps liveness from killing
  the pod during normal startup.

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

Never point liveness/readiness at the same "general health" endpoint that
depends on external resources (database, queue) — if the database goes down,
this takes down every pod of the application via liveness instead of only
marking them not-ready.

## Minimal securityContext

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

Run as root or with a writable filesystem only if the application provably
requires it (e.g. it writes a local cache) — in that case, mount a specific
writable `volume` instead of opening up the whole filesystem.

## Networking: Service, Ingress, DNS

- A Service does not find pods → check that the Service's `selector` matches
  the pod's `labels` exactly (an empty `kubectl get endpoints <service>` is
  the most direct sign).
- Internal DNS resolves as `<service>.<namespace>.svc.cluster.local` —
  resolution errors across namespaces are usually an incomplete name.
- Ingress with no effect: check that the cluster's Ingress Controller
  matches the declared `ingressClassName`, and that the referenced Service
  exists in the same namespace as the Ingress.

## Storage: PVC/PV

- Pod in `Pending` due to a volume-related `FailedScheduling`: the PVC did
  not bind. Check `kubectl get pvc -n <namespace>` — `Pending` there means
  there is no compatible `StorageClass`/`PV` available.
- Never point two writing pods at the same `ReadWriteOnce` PVC on different
  nodes — that locks the second pod in `Pending`, it is not a scheduler bug.
