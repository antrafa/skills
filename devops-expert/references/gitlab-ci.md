# GitLab CI — Pipelines

## Índice
- [Anatomia de um .gitlab-ci.yml](#anatomia-de-um-gitlab-ciyml)
- [rules vs only/except](#rules-vs-onlyexcept)
- [cache vs artifacts](#cache-vs-artifacts)
- [Variáveis e segredos](#variáveis-e-segredos)
- [Runners e tags](#runners-e-tags)
- [Padrão de pipeline build → test → deploy](#padrão-de-pipeline-build--test--deploy)
- [Job falhando: causas comuns](#job-falhando-causas-comuns)

## Anatomia de um .gitlab-ci.yml

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: docker:24
  services: [docker:24-dind]
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

test:
  stage: test
  image: node:20
  script:
    - npm ci --cache .npm --prefer-offline
    - npm test
  cache:
    key:
      files: [package-lock.json]
    paths: [.npm/]

deploy:
  stage: deploy
  image: alpine/k8s:1.35.8   # versão fixa, próxima da do cluster; nunca latest
  script:
    - kubectl set image deploy/meu-app app="$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" -n meu-namespace
    - kubectl rollout status deploy/meu-app -n meu-namespace --timeout=5m
  environment:
    name: producao
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
```

O cache do `test` guarda `.npm/`, não `node_modules/`: o `npm ci` apaga
`node_modules/` antes de instalar, então cachear essa pasta não acelera nada.

`stages` define a ordem; jobs no mesmo stage rodam em paralelo. O pipeline
só avança para o próximo stage quando todos os jobs do atual passam (salvo
job com `allow_failure: true`).

## rules vs only/except

`only`/`except` não recebe mais evolução no GitLab; `rules` é o recomendado
e permite condições compostas:

```yaml
rules:
  - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    when: always
  - if: '$CI_COMMIT_BRANCH == "main"'
    when: on_success
  - when: never   # fallback explícito: não rode em nenhum outro caso
```

A ordem importa — `rules` avalia de cima para baixo e para na primeira que
casar. Esqueça o `when: never` final e o job pode rodar em situações que
você não previu (ex.: em toda tag, todo branch).

## cache vs artifacts

São conceitos diferentes e a confusão entre eles é a causa mais comum de
pipeline lento ou de job que não encontra arquivo esperado:

- **`cache`**: acelera execuções futuras (ex.: `node_modules/`,
  `.m2/repository`). Não é garantido entre jobs/pipelines — trate como
  otimização, nunca como transporte de artefato necessário para o próximo
  stage.
- **`artifacts`**: arquivos gerados por um job que **precisam** estar
  disponíveis para jobs seguintes do mesmo pipeline (ex.: binário compilado,
  relatório de teste, imagem buildada como tarball). São passados
  explicitamente entre stages.

```yaml
build:
  script: [make build]
  artifacts:
    paths: [dist/]
    expire_in: 1 day

deploy:
  script: [./deploy.sh dist/]   # depende do artifact do job anterior
```

Se um job do stage seguinte precisa de um arquivo gerado antes, isso é
`artifacts`, nunca `cache` — cache pode não existir na máquina do runner que
pegou o próximo job.

## Variáveis e segredos

- Variáveis sensíveis (tokens, senhas, chaves) vão em **CI/CD Variables**
  do projeto/grupo no GitLab (Settings → CI/CD → Variables), marcadas como
  **Protected** (só disponíveis em branches/tags protegidas) e **Masked**
  (ocultas no log) — nunca hardcoded no `.gitlab-ci.yml`.
- Variável marcada `Protected` não fica disponível em branches não
  protegidas — se um job falha por variável "vazia" só em MR de feature
  branch, essa é a causa mais comum.
- Para o registry **do próprio projeto**, use as variáveis predefinidas
  `$CI_REGISTRY`, `$CI_REGISTRY_USER`, `$CI_REGISTRY_PASSWORD` (derivadas do
  `$CI_JOB_TOKEN`) e `$CI_REGISTRY_IMAGE` — não precisa cadastrar variável
  nenhuma, e o token expira com o job. Só crie uma CI/CD Variable
  protected/masked quando o destino é externo ao projeto (registry de
  terceiro, cluster, cloud). Uma senha de registry hardcoded no
  `.gitlab-ci.yml` já está no histórico do git: além de remover, oriente a
  **rotacionar** a credencial.

## Runners e tags

Jobs só rodam em runners cuja `tags` bate com a `tags:` declarada no job:

```yaml
deploy:
  tags: [kubernetes, producao]
```

Um job preso em "pending" indefinidamente quase sempre é tag sem runner
correspondente disponível — confira em Settings → CI/CD → Runners quais tags
cada runner aceita antes de investigar qualquer outra causa.

## Padrão de pipeline build → test → deploy

1. **build**: compila/empacota e publica o artefato versionado (imagem
   Docker com tag imutável, ex. SHA do commit — nunca `latest` para deploy
   rastreável).
2. **test**: roda testes contra o artefato gerado no build, não recompila.
3. **deploy**: aplica o artefato já testado no ambiente-alvo. Deploy em
   produção deve ser `when: manual` a menos que o time tenha decidido
   explicitamente por deploy contínuo automático.

Reaproveitar o mesmo artefato do build em todos os stages seguintes (via
`artifacts` ou tag de imagem fixa) garante que o que foi testado é
exatamente o que vai para produção — rebuildar em cada stage abre brecha
para diferença entre o que foi testado e o que foi implantado.

Use `needs:` para declarar a dependência real entre jobs (`deploy` precisa
de `package`, não de "todo o stage anterior") — além de deixar o grafo
explícito, permite que jobs independentes rodem sem esperar o stage
inteiro.

### Build de imagem Docker dentro do pipeline

- O job que roda `docker build` precisa de uma imagem com o binário docker
  (`docker:24`) e do serviço `docker:24-dind` — `bitnami/kubectl` e imagens
  de linguagem não têm docker. Misturar `docker build` e `kubectl` no mesmo
  job é sinal de que faltou um stage `package`.
- Com dind, declare `DOCKER_TLS_CERTDIR: "/certs"` (padrão documentado pelo
  GitLab) — sem isso, a conexão entre o job e o daemon falha de forma
  intermitente e confusa. O runner precisa estar em modo privileged; se
  não puder, a alternativa é kaniko ou buildah.
- **`kubectl set image` com a mesma tag não faz nada.** Se a imagem é
  sempre `:latest`, o valor do campo não muda, o Deployment não vê
  alteração e não faz rollout — o pipeline "passa" e produção continua
  com a versão antiga. Publique com tag por commit
  (`$CI_COMMIT_SHORT_SHA`) e feche o job com `kubectl rollout status` para
  que falhe se o pod novo não subir.

## Job falhando: causas comuns

| Sintoma | Causa provável |
|---|---|
| Job preso em "pending" | Nenhum runner com a `tag` do job disponível/online |
| Variável aparentemente vazia só em branch não-main | Variável marcada `Protected` no projeto |
| `node_modules`/dependências "desaparecem" entre jobs | Usou `cache` para algo que devia ser `artifacts` |
| Job passa localmente mas falha no runner | Imagem base diferente da usada localmente, ou dependência de estado do ambiente local não declarada no `script` |
| Pipeline dispara em todo commit, inclusive tags/MRs não esperados | Falta de `rules` explícito com fallback `when: never` |
| Deploy aplica versão errada | Artefato reconstruído no job de deploy em vez de reutilizar o artefato já testado |
| Deploy "passa" mas produção continua na versão antiga | `kubectl set image` com tag repetida (`:latest`) não altera o Deployment; falta tag por commit + `rollout status` |
| `docker build` falha com "Cannot connect to the Docker daemon" | Job sem serviço dind, imagem sem binário docker, ou `DOCKER_TLS_CERTDIR` ausente |
