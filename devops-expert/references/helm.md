# Helm — Charts and Good Practices

## Contents
- [Chart structure](#chart-structure)
- [values.yaml per environment](#valuesyaml-per-environment)
- [Templates and helpers](#templates-and-helpers)
- [Validation before applying](#validation-before-applying)
- [Hooks](#hooks)
- [Versioning: chart vs app](#versioning-chart-vs-app)
- [Common pitfalls](#common-pitfalls)

## Chart structure

```
meu-chart/
├── Chart.yaml           # metadata: name, version, appVersion
├── values.yaml          # default values
├── values-hml.yaml      # per-environment overrides (optional)
├── values-pro.yaml
├── charts/              # subcharts/dependencies
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── _helpers.tpl     # reusable named functions/templates
│   └── NOTES.txt        # message shown after install/upgrade
└── .helmignore
```

## values.yaml per environment

Prefer a `values.yaml` with only the common defaults and one file per
environment with only what differs — never duplicate the whole file per
environment (that guarantees a structural change made in one environment is
forgotten in the others):

```bash
helm upgrade --install meu-app ./meu-chart \
  -f values.yaml \
  -f values-hml.yaml \
  --namespace meu-namespace
```

Secrets (passwords, tokens, keys) do not go in a `values.yaml` versioned in
git — use a Kubernetes `Secret` referenced via `existingSecret`, or the
environment's secret management tool (Vault, Sealed Secrets, SOPS). A
`values.yaml` with a plain-text password in the repository is the kind of
mistake that only shows up once it has already leaked.

## Templates and helpers

`_helpers.tpl` centralizes repeated names and labels — it keeps each
`template` from computing the same name in a slightly different way:

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

Usage in `deployment.yaml`:

```yaml
metadata:
  name: {{ include "meu-chart.fullname" . }}
  labels:
    {{- include "meu-chart.labels" . | nindent 4 }}
```

Required values without a default must fail early and with a clear message,
not silently turn into an empty string in the manifest:

```yaml
image: "{{ required "values.image.repository is required" .Values.image.repository }}:{{ .Values.image.tag }}"
```

## Validation before applying

Never run `helm upgrade --install` straight against a shared environment
without first validating the rendering:

```bash
helm lint ./meu-chart                                   # syntax/schema errors
helm template meu-app ./meu-chart -f values-hml.yaml     # renders without applying — read the output YAML
helm upgrade --install meu-app ./meu-chart -f values-hml.yaml --dry-run --debug
helm diff upgrade meu-app ./meu-chart -f values-hml.yaml  # requires the helm-diff plugin; shows what actually changes
```

`helm template` is the most underrated tool here — it exposes indentation
and conditional logic errors (`if`/`with`/`range`) that only appear after
rendering, without needing any cluster.

## Hooks

Hooks (`pre-install`, `pre-upgrade`, `post-upgrade`, etc.) run jobs outside
the normal release cycle — typical for a database migration before deploying
the new version:

```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation
```

A failing hook blocks the whole `upgrade` by default — this is intentional
(do not apply the new version if the migration failed), do not treat it as a
Helm bug.

## Versioning: chart vs app

`Chart.yaml` has two fields that must not be confused:

- `version`: the version of the chart itself (changes when the
  template/structure changes).
- `appVersion`: the version of the packaged application (typically the image
  tag).

Bumping the application's image version without touching any chart template
must still increment the chart's `version` — that is what signals there is a
new release to install via `helm upgrade`.

## Common pitfalls

- **Copying a block from another component without adapting the name**: when
  copying a `template` from another chart as reference, always adapt
  labels/container name/`selector` to the current component — using another
  component's name by mistake silently breaks the `Service`/`selector`, with
  no error in `helm upgrade`.
- **`--force` on `helm upgrade`**: recreates resources instead of updating in
  place, can cause unnecessary downtime — use it only when an immutability
  error (e.g. a change to a Service's `selector`) demands it.
- **ConfigMap or Secret changed and pods with the old config**: changing the
  content does not restart the Deployment. Annotate the pod template with the
  hash,
  `checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}`,
  so the `upgrade` restarts when the config changes.
- **Not reviewing `helm diff` before `upgrade` in production**: without it,
  an unintended change in `values.yaml` (e.g. replicas or resources reduced
  by mistake) only shows up after the deploy.
