#!/bin/bash
# Panorama somente leitura de um namespace, numa chamada só.
# Uso: scripts/panorama.sh <kubeconfig> <contexto> <namespace>
# Cada seção roda sozinha: se uma falhar (403, CRD inexistente, metrics-server
# ausente), o erro aparece no lugar dela e as outras seguem. Exit 0 sempre que
# os argumentos estiverem certos; o que falhou está na saída.

if [ $# -ne 3 ]; then
  echo "uso: $0 <kubeconfig> <contexto> <namespace>" >&2
  exit 2
fi
K=(kubectl --kubeconfig "$1" --context "$2" -n "$3")

secao() {
  local titulo=$1; shift
  echo "== $titulo"
  local saida
  if saida=$("${K[@]}" "$@" 2>&1); then
    echo "${saida:-(vazio)}"
  else
    echo "FALHOU: $(echo "$saida" | tail -n 1)"
  fi
  echo
}

secao "Pods" get pods -o wide
secao "Workloads" get deploy,statefulset,daemonset -o wide
secao "Services e endpoints" get svc,endpoints -o wide
secao "Rotas (Ingress)" get ingress -o wide
secao "Rotas (Istio VirtualService)" get virtualservice -o wide
secao "HPA" get hpa
secao "PVC" get pvc
secao "Consumo (top)" top pod
echo "== Eventos recentes (últimos 30)"
if saida=$("${K[@]}" get events --sort-by=.lastTimestamp 2>&1); then
  echo "$saida" | tail -n 30
else
  echo "FALHOU: $(echo "$saida" | tail -n 1)"
fi
