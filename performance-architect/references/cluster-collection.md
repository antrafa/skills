# Evidence Collection in a Kubernetes Cluster (read-only)

Use this file when the user offers access to the cluster. It is optional: if
they have no access or do not want to grant it, continue the analysis
without this source and mark the conclusions that depended on it as
hypotheses.

## Contents
- [Access: kubeconfig and allow-list](#access-kubeconfig-and-allow-list)
- [What to collect, in this order](#what-to-collect-in-this-order)
- [How to read each output](#how-to-read-each-output)
- [When a command fails](#when-a-command-fails)

## Access: kubeconfig and allow-list

This skill does not require `cluster-analyzer` to collect cluster evidence
— the minimum below is self-sufficient. **If the `cluster-analyzer` skill is
also available**, prefer its full protocol (execution rules and step 1): it
details the customer/environment confirmation and the read allow-list
better, and avoids keeping the same safety rule in two places.

Do not reproduce the allow-list here or build your own. It was once written
in duplicate in both files, and two copies of a safety rule drift apart —
the one that drifts is the one that will authorize a `rollout restart` in an
environment with real traffic. One copy only, and it lives in the skill
whose reason to exist is precisely read-only access.

**If `cluster-analyzer` is not available** (this skill alone), the rule does
not fall away for lack of a source — it closes. This minimum applies, and
nothing beyond it: `kubectl get`, `describe`, `logs`, `top`, `events`,
`explain`, `auth can-i`, `rollout status`, `rollout history`, and
`helm list`, `get`, `status`, `history`. Any other verb, including the ones
that look harmless (`exec`, `port-forward`, `debug`, `cp`), stays out. Tell
the user, in one line, that you are operating with the minimum because
`cluster-analyzer` is missing — never fill the gap with an improvised
allow-list.

What still applies here, and does not depend on enumerating any command:

- Before the first command, discover the available kubeconfigs
  (`$KUBECONFIG`, `~/.kube/config` and other files in `~/.kube/`), present
  the candidates to the user and ask which environment to investigate — do
  not guess from the file name (`hml` and `prd` side by side is the most
  expensive mistake possible here). If the file has more than one context,
  confirm which one to use with `config get-contexts` before going on.
- Explicit `--kubeconfig` and `--context` on **every** command. Never
  `use-context`, never a global `KUBECONFIG` — a context switch leaks into
  the user's other terminals.
- Never `cat` the kubeconfig: it carries a certificate and a token.
- Before the first command, confirm in text which environment is being
  read, so the user notices right away if it is the wrong one.

## What to collect, in this order

One command at a time. Show the command, wait for the output, interpret it
before the next one — each result decides what the next question is. Do not
chain several commands at once.

```bash
# 1. Topology: how many replicas actually exist, and where
kubectl get deploy,sts,hpa -n <ns> -o wide

# 2. Declared sizing: requests, limits, probes, grace period
kubectl get deploy/<name> -n <ns> -o yaml

# 3. Real vs declared usage (requires metrics-server)
kubectl top pod -n <ns>
kubectl top node

# 4. HPA state: which metric it scales on, and whether it is at the ceiling
kubectl describe hpa/<name> -n <ns>

# 5. Restart history and reason (memory? probe?)
kubectl get pods -n <ns> -o wide
kubectl describe pod <pod> -n <ns>

# 6. Recent namespace events, newest to oldest
kubectl get events -n <ns> --sort-by='.lastTimestamp'

# 7. Log of the previous run, when there was a restart
kubectl logs <pod> -n <ns> --previous --tail=200

# 8. If installed by Helm: which values are actually applied
helm get values <release> -n <ns>
```

If possible, collect `top pod` **at peak time** — a 24h average hides
exactly what is being investigated.

## How to read each output

| What to look at | Problem signal | What it means for performance |
|---|---|---|
| Deployment `replicas` | 1 replica | no slack; every deploy is downtime and there is no horizontal scaling |
| `resources.requests` vs `top pod` | usage far above the request | wrong scheduling: the pod competes for CPU nobody reserved |
| `resources.limits.cpu` | low limit with usage close to it | CPU throttling — shows up as stepped latency, not as high CPU |
| `resources.limits.memory` | equal or close to the JVM heap | `OOMKilled` waiting for the peak (metaspace, stacks and direct buffers live outside the heap) |
| `describe pod` → `Last State` | `OOMKilled`, exit 137 | not enough memory under real load |
| `describe pod` → `Events` | `Liveness probe failed`, `Killing` | probe killing the application under load or at boot |
| `describe hpa` | the metric is CPU | CPU is a poor proxy for a service that waits on I/O; RPS or queue depth are better |
| `describe hpa` | `desired = max` | it is at the ceiling: it scaled everything it could and it was not enough |
| `get pods` → `Pending` | pod not scheduled | HPA ceiling higher than the cluster can allocate |
| `terminationGracePeriodSeconds` | missing or very short | rolling update drops in-flight requests — at hundreds of req/s, a deploy becomes an incident |
| `readinessProbe` | missing | traffic arrives before the application is ready; an error spike on every deploy |
| accumulated `RESTARTS` | growing at peak | the problem is load, not initial configuration |

A throttling metric, when there is Prometheus, is the direct confirmation:
`rate(container_cpu_cfs_throttled_seconds_total[5m])` > 0 means
`limits.cpu` is holding the application back.

## When a command fails

- `403 Forbidden` is expected and part of the permission model. Do not try
  to work around it, do not look for alternative credentials, do not
  suggest widening permissions. Report what the missing access means for
  the analysis and continue through another read path.
- A missing `metrics-server` breaks `top`. Without it there is no real
  usage — say so and treat the sizing as a hypothesis.
- **Never fill in a command's output from memory.** If it did not run, say
  it did not run. Invented output is the worst possible defect in this
  analysis.
