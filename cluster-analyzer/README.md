# Cluster Analyzer (`cluster-analyzer`)

Read-only Kubernetes diagnosis for setups with many kubeconfigs and contexts
(one per client or environment). The agent confirms which file and context to
use before running anything, ranks hypotheses, and only runs commands from an
explicit allow-list. Fixes come back as a separate block for you to apply.

## Prerequisites

| What | Needed for | Required |
|---|---|---|
| `kubectl` on `PATH` | every step | yes |
| One kubeconfig per environment (`~/.kube/*`, `$KUBECONFIG`) with read access (`get`, `describe`, `logs`) | every step | yes |
| `metrics-server` in the cluster | `kubectl top` | no — the skill falls back to `describe` and `resources` |
| `helm` on `PATH` | identifying Helm releases | no — falls back to resource labels |
| `python3` (stdlib only) | `scripts/envdiff.py` | only for environment comparison |
| `curl` | telling proxy errors from application errors | only for HTTP symptoms |

A read-only token is enough and is the recommended setup: a `403` is treated
as an expected limit, never as something to work around.

## Scripts

Both scripts take the kubeconfig and context explicitly and never change the
current context. Each one also runs on its own, without the agent.

- `scripts/panorama.sh <kubeconfig> <context> <namespace>` — pods,
  workloads, services and endpoints, routes, HPA, PVC, `top` and recent
  events in one call. A section that fails prints `FAILED:` and the rest
  keeps going.
- `scripts/envdiff.py <deployment> --a <kubeconfig> <context> <namespace>
  --b <kubeconfig> <context> <namespace>` — images and environment variables
  of one Deployment in two environments, resolving referenced ConfigMaps.
  Secrets are never read, only referenced, and credential-like values are
  masked.

`scripts/test-scripts.sh` checks both against a fake `kubectl`, no cluster
needed.
