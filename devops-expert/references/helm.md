# Helm — Charts e Boas Práticas

## Índice
- [Estrutura de um chart](#estrutura-de-um-chart)
- [values.yaml por ambiente](#valuesyaml-por-ambiente)
- [Templates e helpers](#templates-e-helpers)
- [Validação antes de aplicar](#validação-antes-de-aplicar)
- [Hooks](#hooks)
- [Versionamento: chart vs app](#versionamento-chart-vs-app)
- [Armadilhas comuns](#armadilhas-comuns)

## Estrutura de um chart

```
meu-chart/
├── Chart.yaml           # metadados: name, version, appVersion
├── values.yaml          # valores padrão
├── values-hml.yaml      # overrides por ambiente (opcional)
├── values-pro.yaml
├── charts/              # subcharts/dependências
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── _helpers.tpl     # funções/templates nomeados reutilizáveis
│   └── NOTES.txt        # mensagem exibida após install/upgrade
└── .helmignore
```

## values.yaml por ambiente

Prefira um `values.yaml` só com os padrões comuns e um arquivo por ambiente
com apenas o que difere — nunca duplique o arquivo inteiro por ambiente
(isso garante que uma mudança estrutural feita num ambiente seja esquecida
nos outros):

```bash
helm upgrade --install meu-app ./meu-chart \
  -f values.yaml \
  -f values-hml.yaml \
  --namespace meu-namespace
```

Segredos (senhas, tokens, chaves) não vão em `values.yaml` versionado no
git — use `Secret` do Kubernetes referenciado via `existingSecret`, ou uma
ferramenta de secret management do ambiente (Vault, Sealed Secrets, SOPS).
Um `values.yaml` com senha em texto plano no repositório é o tipo de erro
que só aparece quando já vazou.

## Templates e helpers

`_helpers.tpl` centraliza nomes e labels repetidos — evita que cada
`template` recalcule o mesmo nome de forma ligeiramente diferente:

```yaml
{{/* _helpers.tpl */}}
{{- define "meu-chart.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "meu-chart.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
{{- end -}}
```

Uso em `deployment.yaml`:

```yaml
metadata:
  name: {{ include "meu-chart.fullname" . }}
  labels:
    {{- include "meu-chart.labels" . | nindent 4 }}
```

Valores obrigatórios sem default devem falhar cedo e com mensagem clara, não
silenciosamente virar string vazia no manifest:

```yaml
image: "{{ required "values.image.repository é obrigatório" .Values.image.repository }}:{{ .Values.image.tag }}"
```

## Validação antes de aplicar

Nunca rode `helm upgrade --install` direto num ambiente compartilhado sem
antes validar a renderização:

```bash
helm lint ./meu-chart                                   # erros de sintaxe/schema
helm template meu-app ./meu-chart -f values-hml.yaml     # renderiza sem aplicar — leia o YAML de saída
helm upgrade --install meu-app ./meu-chart -f values-hml.yaml --dry-run --debug
helm diff upgrade meu-app ./meu-chart -f values-hml.yaml  # requer plugin helm-diff; mostra o que muda de fato
```

`helm template` é a ferramenta mais subestimada aqui — ela expõe erros de
indentação e de lógica condicional (`if`/`with`/`range`) que só aparecem
depois de renderizado, sem precisar de cluster nenhum.

## Hooks

Hooks (`pre-install`, `pre-upgrade`, `post-upgrade`, etc.) rodam jobs fora do
ciclo normal de release — típico para migração de banco antes do deploy da
nova versão:

```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation
```

Um hook que falha por padrão trava o `upgrade` inteiro — isso é intencional
(não aplicar a versão nova se a migração falhou), não trate como bug do Helm.

## Versionamento: chart vs app

`Chart.yaml` tem dois campos que não devem ser confundidos:

- `version`: versão do chart em si (muda quando o template/estrutura muda).
- `appVersion`: versão da aplicação empacotada (a tag da imagem, tipicamente).

Subir a versão da imagem da aplicação sem tocar em nenhum template do chart
ainda assim deve incrementar `version` do chart — é o que identifica que
existe uma nova release para instalar via `helm upgrade`.

## Armadilhas comuns

- **Copiar bloco de outro componente sem adaptar o nome**: ao copiar um
  `template` de outro chart como referência, sempre adapte labels/nome de
  container/`selector` para o componente atual — usar por engano o nome de
  outro componente quebra o `Service`/`selector` silenciosamente, sem erro
  no `helm upgrade`.
- **`--force` no `helm upgrade`**: recria recursos em vez de atualizar in
  place, pode causar downtime desnecessário — use só quando um erro de
  imutabilidade (ex.: mudança de `selector` de um Service) exigir.
- **Não revisar `helm diff` antes de `upgrade` em produção**: sem isso, uma
  mudança não intencional em `values.yaml` (ex.: réplica ou recurso
  reduzido por engano) só aparece depois do deploy.
