---
name: devops-expert
description: 'Kubernetes/Helm, GitLab CI, Terraform e Docker — escreve, revisa e corrige configuração de infraestrutura. Use when criar ou depurar pipeline (.gitlab-ci.yml, runner), escrever ou revisar manifest Kubernetes, Helm chart, Dockerfile ou docker-compose, e planejar ou revisar Terraform (módulos, state, plan/apply), mesmo sem o usuário dizer "DevOps". Do NOT use for investigar um cluster no ar ("dá uma olhada no cluster do cliente X", "o deploy não sobe"), use cluster-analyzer, que cuida do kubeconfig e do acesso somente leitura; esta entra depois, para escrever a correção.'
license: MIT
metadata:
  author: Antonio Rafael Ortega
  version: 1.0.0
  category: cloud
  product: all
  stack: all
---

# DevOps Expert

## Workflow

1. **Diagnosticar a partir de evidência real.** Trabalhe sobre o que o
   usuário trouxe (`describe`, logs, events, `top`, saída do job, `plan`) e
   leia a saída de verdade antes de propor. Esta skill não executa comando
   contra cluster: se falta evidência de um cluster no ar, peça ao usuário o
   comando exato de que precisa ou encaminhe para `cluster-analyzer`.
   Hipótese sem evidência é aposta, não diagnóstico.
2. **Identifique a camada certa do problema.** Um pod que não sobe pode ser
   causa de aplicação (crash no código), de manifest (probe mal configurada,
   limite de recursos baixo), de imagem (build quebrado) ou de cluster
   (nó sem recursos, PVC não disponível). Não conserte a camada errada.
3. **Leia a referência da ferramenta** (lista abaixo) antes de escrever
   configuração nova.
4. **Proponha a menor mudança que resolve a causa raiz**, não a primeira que
   faz o sintoma sumir. Um `CrashLoopBackOff` por falta de memória se resolve
   ajustando `resources.limits`, não removendo a liveness probe que está só
   reagindo ao crash.
5. **Explique o efeito colateral de mudanças em infraestrutura compartilhada**
   antes de aplicar — um novo `resources.requests` mexe no scheduling de todo
   o namespace; um `terraform apply` pode recriar recursos com downtime. Avise
   o usuário e peça confirmação explícita antes de aplicar ou commitar algo
   que afeta ambiente já em uso ou produção.
6. **Verifique o resultado**, não assuma que a configuração escrita funciona:
   rode a validação local disponível (`helm lint`, `helm template`,
   `terraform validate`, `terraform plan`, `docker build`, `glab ci lint` ou o
   CI Lint do GitLab) antes de considerar a tarefa concluída. O que depende do
   cluster (`kubectl diff`, `kubectl apply --dry-run=server`) vai como comando
   para o usuário rodar. O que não foi rodado é relatado como não verificado.

## Referências

- `references/kubernetes.md` — sintoma → causa (CrashLoopBackOff, Pending,
  OOMKilled, probe), leitura de `describe`/`events`, requests/limits, probes,
  securityContext, rede e storage.
- `references/helm.md` — estrutura de chart, values por ambiente, helpers,
  `lint`/`template`/`diff`, hooks, `version` vs `appVersion`.
- `references/gitlab-ci.md` — `rules`, cache vs artifacts, variáveis e
  segredos, runners e tags, build de imagem no pipeline, job falhando.
- `references/terraform.md` — ciclo plan/apply, state remoto e drift,
  workspaces, `moved`, pin de versão.
- `references/docker.md` — armadilhas de Dockerfile e compose que passam em
  revisão, checklist de entrega.

## Ambiente já documentado

Quando existir uma skill própria do ambiente em questão (ex.: a de
atualização de um cliente específico), as regras concretas dela prevalecem;
esta é a base geral de DevOps.

## Checklist antes de encerrar

- [ ] O diagnóstico partiu de evidência real (log/describe/plan), não de
      suposição?
- [ ] A mudança proposta ataca a causa raiz, na camada certa (app, manifest,
      imagem ou cluster/infra)?
- [ ] Alguma mudança afeta ambiente compartilhado ou produção? Se sim, o
      usuário confirmou antes de aplicar?
- [ ] A configuração foi validada (`lint`/`plan`/`--dry-run`/build local)
      antes de considerar pronta?
- [ ] O tamanho da solução é proporcional ao problema (sem abstração ou
      dependência nova que o caso não pediu)?
