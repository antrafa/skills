# Terraform — Infraestrutura como Código

## Índice
- [Estrutura de um módulo](#estrutura-de-um-módulo)
- [Ciclo init/plan/apply/destroy](#ciclo-initplanapplydestroy)
- [Gestão de state](#gestão-de-state)
- [Variáveis e workspaces](#variáveis-e-workspaces)
- [Boas práticas](#boas-práticas)
- [Armadilhas comuns](#armadilhas-comuns)

## Estrutura de um módulo

```
meu-modulo/
├── main.tf          # recursos
├── variables.tf      # inputs (com description e type sempre)
├── outputs.tf        # outputs consumidos por quem usa o módulo
├── versions.tf        # required_providers e required_version
└── README.md
```

Um módulo reutilizável não deve ter valores fixos que dependem do ambiente
(nome de projeto, região, tamanho de instância) — esses valores entram via
`variables.tf` e são passados por quem instancia o módulo.

## Ciclo init/plan/apply/destroy

```bash
terraform init                 # baixa providers/módulos, configura backend
terraform validate             # valida sintaxe/tipos, sem acessar a infra
terraform plan -out=tfplan     # mostra o que vai mudar, sem aplicar
terraform apply tfplan         # aplica exatamente o plan revisado
terraform destroy              # remove os recursos gerenciados
```

**Nunca rode `terraform apply` sem revisar o `plan` correspondente
primeiro** — aplicar `tfplan` salvo (em vez de rodar `apply` direto)
garante que o que foi revisado é exatamente o que será aplicado, sem uma
janela onde o estado remoto mudou entre o plan e o apply.

Leia a saída do `plan` pelos símbolos:
- `+` cria, `-` destrói, `~` atualiza in-place, `-/+` destrói e recria.
- `-/+` é o mais perigoso: o recurso antigo é destruído e o dado dele se
  perde (ex.: banco recriado do zero); sem `create_before_destroy`, há também
  downtime. Pare e confirme antes de aplicar isso em ambiente com dado real.

## Gestão de state

O state (`terraform.tfstate`) é a fonte de verdade de quais recursos reais
correspondem a quais blocos do código — e contém, em texto plano, qualquer
valor sensível gerenciado (senhas geradas, chaves).

- **Sempre use backend remoto** (S3 com `use_lockfile = true` — lock nativo
  desde o Terraform 1.11; o lock via DynamoDB foi descontinuado —, Azure
  Storage, GCS, HCP Terraform) com locking habilitado — state local em disco de uma máquina não
  escala para mais de uma pessoa e não tem lock, gerando corrupção quando
  dois `apply` rodam ao mesmo tempo.
- **Nunca versione `.tfstate` no git** — ele carrega segredos e gera conflito
  de merge impossível de resolver manualmente.
- **Drift** (infra real diferente do state) acontece quando alguém muda um
  recurso manualmente pelo console/CLI do provedor. Detecte com
  `terraform plan` regular — se aparecer mudança que ninguém fez no código,
  é drift, não bug do Terraform. Corrija a causa (acesso manual ao ambiente),
  não só o state.
- `terraform state list` / `terraform state show <recurso>` inspecionam o
  state sem precisar abrir o arquivo bruto.

## Variáveis e workspaces

```hcl
variable "ambiente" {
  description = "Nome do ambiente (hml, pro)"
  type        = string
}
```

```bash
terraform plan -var="ambiente=hml" -var-file="hml.tfvars"
```

Workspaces (`terraform workspace new hml`) isolam state por ambiente dentro
do mesmo código — útil quando a diferença entre ambientes é só valor de
variável. Quando a topologia difere estruturalmente entre ambientes (não só
valores), prefira diretórios/módulos separados a forçar tudo num workspace
só; misturar os dois modelos confunde qual state pertence a qual ambiente.

## Boas práticas

- Nunca hardcode segredo em `.tf`/`.tfvars` versionado — use variável de
  ambiente (`TF_VAR_*`), secret manager do provedor, ou um `.tfvars` fora do
  controle de versão.
- Fixe a versão do provider (`required_providers` com `version = "~> 5.0"`)
  — um `apply` num pipeline meses depois, sem fixação, pode puxar uma versão
  de provider com mudança de comportamento.
- Nomeie recursos por função, não por valor atual (ex.: `aws_instance.api`,
  não `aws_instance.t3_medium`) — o nome sobrevive a uma mudança de tipo de
  instância, e renomear depois exige `moved` (ver abaixo).

## Armadilhas comuns

- **Renomear um `resource` block em vez de usar `moved`**: renomear
  `resource "aws_instance" "old" {}` para `"new"` sem um bloco `moved` faz o
  Terraform entender como destruir o antigo e criar um novo — use
  `moved { from = aws_instance.old to = aws_instance.new }` para preservar o
  recurso real.
- **`terraform apply` direto em CI sem `plan` salvo revisável**: pipelines
  de produção devem gerar o `plan` como artifact e exigir aprovação manual
  antes do `apply` — mesmo padrão de "nunca aplicar sem confirmação" usado
  em mudança de cluster.
- **Módulo de terceiros sem pin de versão** (`source = "git::..."` sem
  `ref=`): o módulo pode mudar de comportamento entre execuções sem nenhuma
  mudança no seu próprio código.
