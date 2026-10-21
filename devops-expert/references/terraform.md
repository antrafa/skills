# Terraform — Infrastructure as Code

## Contents
- [Module structure](#module-structure)
- [init/plan/apply/destroy cycle](#initplanapplydestroy-cycle)
- [State management](#state-management)
- [Variables and workspaces](#variables-and-workspaces)
- [Good practices](#good-practices)
- [Common pitfalls](#common-pitfalls)

## Module structure

```
meu-modulo/
├── main.tf          # resources
├── variables.tf      # inputs (always with description and type)
├── outputs.tf        # outputs consumed by whoever uses the module
├── versions.tf        # required_providers and required_version
└── README.md
```

A reusable module must not have fixed values that depend on the environment
(project name, region, instance size) — those values come in via
`variables.tf` and are passed by whoever instantiates the module.

## init/plan/apply/destroy cycle

```bash
terraform init                 # downloads providers/modules, configures the backend
terraform validate             # validates syntax/types, without touching the infra
terraform plan -out=tfplan     # shows what will change, without applying
terraform apply tfplan         # applies exactly the reviewed plan
terraform destroy              # removes the managed resources
```

**Never run `terraform apply` without first reviewing the corresponding
`plan`** — applying the saved `tfplan` (instead of running `apply` directly)
guarantees that what was reviewed is exactly what will be applied, with no
window where the remote state changed between the plan and the apply.

Read the `plan` output by its symbols:
- `+` creates, `-` destroys, `~` updates in place, `-/+` destroys and
  recreates.
- `-/+` is the most dangerous: the old resource is destroyed and its data is
  lost (e.g. a database recreated from scratch); without
  `create_before_destroy`, there is also downtime. Stop and confirm before
  applying this to an environment with real data.
- The `plan` states the reason for the recreation: the line marked
  `# forces replacement` is the attribute that forces the replacement (name,
  zone, key). Changing that attribute back, or using `moved`, usually avoids
  the recreation.
- A resource that cannot be recreated (database, bucket with data) gets
  `lifecycle { prevent_destroy = true }`: the `plan` fails instead of
  destroying.

## State management

The state (`terraform.tfstate`) is the source of truth for which real
resources correspond to which blocks of code — and it contains, in plain
text, any sensitive value it manages (generated passwords, keys).

- **Always use a remote backend** (S3 with `use_lockfile = true` — native
  locking since Terraform 1.11; DynamoDB locking was deprecated —, Azure
  Storage, GCS, HCP Terraform) with locking enabled — local state on one
  machine's disk does not scale beyond one person and has no lock, causing
  corruption when two `apply` runs happen at the same time.
- **Never version `.tfstate` in git** — it carries secrets and creates merge
  conflicts impossible to resolve by hand.
- **Drift** (real infra different from the state) happens when someone
  changes a resource manually through the provider's console/CLI. Detect it
  with a regular `terraform plan` — if a change appears that nobody made in
  the code, it is drift, not a Terraform bug. Fix the cause (manual access to
  the environment), not just the state.
- `terraform state list` / `terraform state show <resource>` inspect the
  state without opening the raw file.
- `sensitive = true` on a variable and output only hides the value from the
  `plan` output and the log: in the state it remains in plain text. Protect
  the backend (access, encryption), not just the code.
- Do not propose `terraform state rm`, `state mv` or `import` as a shortcut
  unless the user asks: editing the state by hand misaligns code and infra
  without leaving a trace in the `plan`. Prefer `moved` and `import` blocks in
  the code, which go through review.

## Variables and workspaces

```hcl
variable "ambiente" {
  description = "Environment name (hml, pro)"
  type        = string
}
```

```bash
terraform plan -var="ambiente=hml" -var-file="hml.tfvars"
```

Workspaces (`terraform workspace new hml`) isolate state per environment
within the same code — useful when the difference between environments is
only variable values. When the topology differs structurally between
environments (not just values), prefer separate directories/modules to
forcing everything into a single workspace; mixing the two models confuses
which state belongs to which environment.

## Good practices

- Never hardcode a secret in a versioned `.tf`/`.tfvars` — use an
  environment variable (`TF_VAR_*`), the provider's secret manager, or a
  `.tfvars` outside version control.
- Pin the provider version (`required_providers` with `version = "~> 5.0"`)
  — an `apply` in a pipeline months later, without pinning, can pull a
  provider version with a behaviour change.
- Name resources by function, not by current value (e.g. `aws_instance.api`,
  not `aws_instance.t3_medium`) — the name survives an instance type change,
  and renaming later requires `moved` (see below).

## Common pitfalls

- **Renaming a `resource` block instead of using `moved`**: renaming
  `resource "aws_instance" "old" {}` to `"new"` without a `moved` block makes
  Terraform read it as destroying the old one and creating a new one — use
  `moved { from = aws_instance.old to = aws_instance.new }` to preserve the
  real resource.
- **`terraform apply` straight in CI without a reviewable saved `plan`**:
  production pipelines must generate the `plan` as an artifact and require
  manual approval before the `apply` — the same "never apply without
  confirmation" pattern used for cluster changes.
- **Third-party module without a version pin** (`source = "git::..."`
  without `ref=`): the module can change behaviour between runs without any
  change in your own code.
