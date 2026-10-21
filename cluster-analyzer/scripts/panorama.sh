#!/bin/bash
# Read-only overview of a namespace, in a single call.
# Usage: scripts/panorama.sh <kubeconfig> <context> <namespace>
# Each section runs on its own: if one fails (403, missing CRD, metrics-server
# absent), the error shows up in its place and the others carry on. Exit 0
# whenever the arguments are right; what failed is in the output.

if [ $# -ne 3 ]; then
  echo "usage: $0 <kubeconfig> <context> <namespace>" >&2
  exit 2
fi
K=(kubectl --kubeconfig "$1" --context "$2" -n "$3")

secao() {
  local titulo=$1; shift
  echo "== $titulo"
  local saida
  if saida=$("${K[@]}" "$@" 2>&1); then
    echo "${saida:-(empty)}"
  else
    echo "FAILED: $(echo "$saida" | tail -n 1)"
  fi
  echo
}

secao "Pods" get pods -o wide
secao "Workloads" get deploy,statefulset,daemonset -o wide
secao "Services and endpoints" get svc,endpoints -o wide
secao "Routes (Ingress)" get ingress -o wide
secao "Routes (Istio VirtualService)" get virtualservice -o wide
secao "HPA" get hpa
secao "PVC" get pvc
secao "Usage (top)" top pod
echo "== Recent events (last 30)"
if saida=$("${K[@]}" get events --sort-by=.lastTimestamp 2>&1); then
  echo "$saida" | tail -n 30
else
  echo "FAILED: $(echo "$saida" | tail -n 1)"
fi
