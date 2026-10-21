# Symptom → likely cause (read-only)

Support table for building the Step 2 hypotheses. It covers only what can be
confirmed or ruled out with the allow-list commands — no entry here depends
on `exec`, `debug` or any verb outside the *Execution rules*.

| Symptom (`kubectl get pods`) | Most likely causes | Where to confirm |
|---|---|---|
| `CrashLoopBackOff` | Application crashes on start (config error, dependency unavailable), liveness probe killing the process before it is ready, out of memory (see `OOMKilled` in describe) | `kubectl logs --previous`, `kubectl describe pod` (`Last State` section) |
| `ImagePullBackOff` / `ErrImagePull` | Wrong/nonexistent image tag, private registry without `imagePullSecrets`, registry rate limit | `kubectl describe pod` (`Failed to pull image` event) |
| `Pending` | No node with enough resources (CPU/mem request too high), `nodeSelector`/`affinity` with no compatible node, PVC didn't bind | `kubectl describe pod` (`Events` section, e.g. `FailedScheduling`) |
| `OOMKilled` (visible in `describe` → `Last State: Terminated, Reason: OOMKilled`) | `resources.limits.memory` lower than the application's real usage | `kubectl top pod` over time, not just one snapshot |
| Readiness never becomes `Ready` but the pod is `Running` | Readiness endpoint doesn't answer in time, wrong port in the probe, app takes longer than `initialDelaySeconds` to start | `kubectl describe pod` (probe failing event), `kubectl logs` |
| Deploy "stuck" (rollout never completes) | `maxUnavailable`/`maxSurge` incompatible with the replica count, new pod never becomes `Ready` (see row above), `PodDisruptionBudget` blocking | `kubectl rollout status`, `kubectl describe deploy` |
| Pod restarting with no apparent error in the log (`RESTARTS` going up) | OOM or liveness kill before the app logs anything, app that exits with code 0 and is restarted by the `restartPolicy` | `kubectl describe pod` (`Last State`: `Reason` and `Exit Code`; probe `Events`) |
| Pod `Evicted` (the pod disappears and another is born with a new name — doesn't count in `RESTARTS`) | Node under memory/disk pressure (`MemoryPressure`/`DiskPressure`), pod without `requests` being the first evicted | `kubectl get pods --field-selector status.phase=Failed`, `kubectl describe node <node>` (`Conditions`) |
| Service with no traffic reaching the pods | The Service `selector` doesn't match the pod `labels` | An empty `kubectl get endpoints <service>` is the most direct sign |
| Ingress with no effect | `ingressClassName` doesn't match the cluster's controller, or the referenced Service doesn't exist in the Ingress namespace | `kubectl describe ingress`, `kubectl get svc -n <namespace>` |
| PVC stuck in `Pending` | No compatible `StorageClass`/`PV` available. With `volumeBindingMode: WaitForFirstConsumer` `Pending` is normal until a pod uses the PVC — not an error | `kubectl get pvc -n <namespace>`, `kubectl describe pvc`, `kubectl get storageclass` |
| Pod stuck in `ContainerCreating` with `Multi-Attach error` | Two pods on different nodes mounting the same `ReadWriteOnce` PVC (common in a `RollingUpdate` rollout of a deploy with an RWO volume) | `kubectl describe pod` (`FailedAttachVolume`/`Multi-Attach` event) |

## Looks like a problem, but is normal

The right-hand column is what separates the false alarm from the real
problem. Without it, every strange line becomes a hypothesis and the
investigation scatters.

| Observed | Why it is usually normal | Becomes a problem when |
|---|---|---|
| High `RESTARTS` | The counter covers the pod's whole life; the last restart may be days old (`kubectl get pods` shows `5 (3d ago)`) | The last restart is recent or the number goes up while you watch |
| Old `Evicted` or `Failed` pods in the list | History nobody cleaned up; consumes no resources | New pods show up in that state |
| `Completed` pods | Normal run of a `Job`/`CronJob` | They stay in `Error`, or the `Job` never reaches `Completed` |
| `Readiness probe failed` in the first seconds | App still starting; the pod becomes `Ready` shortly after | It continues after `Ready`, or the pod never becomes `Ready` |
| Memory near the limit in `top pod`, on a JVM | The JVM reserves heap and doesn't give it back; high, stable usage is expected | There is `OOMKilled` in `Last State` or usage grows without stopping |
| Empty endpoints or a deploy at `0/0` | Someone scaled to zero on purpose (maintenance, shutdown) | The values/manifest in git declares replicas > 0 and nobody knows about the shutdown |
| HPA at minimum replicas | Off-peak hours | Under load and not scaling; or `FailedGetResourceMetric` long after the deploy |
| PVC `Pending` with `WaitForFirstConsumer` | It only binds when a pod uses the PVC | A pod is using the PVC and it stays `Pending` |
| Proxy 404 on `/app` without a trailing slash | The route declares the prefix `/app/` | `/app/` with the slash also fails |

## Where the HTTP error originates

When the symptom is "the URL returns an error", first find out **who
answered**: the entry proxy (Istio/Envoy, ingress-nginx) or the application.
A GET that only prints the headers answers that:

```bash
curl -sk -m 15 -o /dev/null -D - https://<host>/<path>/
```

| Response | Who answered | Next read |
|---|---|---|
| 503 `no healthy upstream`, `content-type: text/plain`, no `x-envoy-upstream-service-time` | Envoy, with no healthy destination | Empty `get endpoints <svc>`, deploy with 0 replicas, wrong `targetPort`, route pointing to a Service that doesn't exist |
| 502/503/504 with an ingress-nginx HTML page | Ingress controller | Backend endpoints and readiness; timeout configured in the Ingress annotations |
| Proxy 404 | No route matched | Host and prefix declared in the Ingress/VirtualService; see the trailing-slash row above |
| 500, 401, 302 or 200 with `x-envoy-upstream-service-time` (or the app's own header) | The application | Pod `logs` at the time of the call |

Two route objects declaring the same host and prefix is a sign of an orphan
object: a resource was renamed, `kubectl apply` created the new one and
didn't delete the old one, and the old one may be winning. List the
namespace's routes (`get virtualservice,ingress -o wide`) and compare hosts
and prefixes.

## Works in one environment and not in the other

The difference is almost always an environment variable or infrastructure
(memory, certificate, route), not the version. Compare in this order:

1. Image and tag of each container — `get deploy <name> -o wide` on both.
2. Environment variables — `scripts/envdiff.py`, which reads the deploy and
   the referenced ConfigMaps on both sides and shows what exists on only one
   of them and what differs. Credential-like values come out masked, and a
   Secret is never read: it shows up only as a reference.
3. `resources`, probes and replicas — `get deploy <name> -o yaml` on both.

## Reading `describe` and `events` correctly

`kubectl describe pod` has two sections that solve most cases before any
other investigation:

- **`Last State`**: shows the `Reason` (`OOMKilled`, `Error`, `Completed`)
  and `Exit Code` of the previous run — the exit code usually tells whether
  it was an application crash (non-zero code defined by the app) or a system
  kill (137 = SIGKILL, usually OOM).
- **`Events`**: chronological order of what the scheduler/kubelet tried to
  do. Read top to bottom — the first error event is usually the root cause,
  the following ones tend to be repetitions/consequences.

Events disappear from the cluster after a while (default TTL of 1 hour in
kube-apiserver); if the pod no longer exists and `describe` shows nothing
useful, look in `kubectl get events` filtered by
`--field-selector involvedObject.name=<pod>` while it is still available.

## Related

The `devops-expert` skill, if available, documents the same table with the
manifest fix matching each cause (requests/limits, probes, securityContext).
Use it after this analysis, once you have the confirmed cause and want the
corrected YAML — this skill doesn't need it to diagnose.
