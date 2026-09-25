# Docker — Armadilhas e Checklist

O básico (multi-stage, ordem de camadas para cache, `.dockerignore`,
`USER` não-root, base `alpine`/`slim`) você já sabe — não precisa de
tutorial aqui. Este arquivo cobre só o que costuma passar despercebido
numa revisão de Dockerfile e o que checar antes de dar uma imagem como
pronta.

## Armadilhas que passam despercebidas

| Sintoma / achado | Causa real | O que fazer |
|---|---|---|
| Build só funciona com `node_modules/` do host presente | `ENV NODE_ENV=production` declarado **antes** do `npm install`/`npm ci` faz o npm pular devDependencies, então `tsc`/bundler nunca é instalado; o build "passa" porque `COPY . .` trouxe o `node_modules/` local — e quebra assim que um `.dockerignore` excluir a pasta | Só defina `NODE_ENV=production` no estágio de runtime; instale devDeps no estágio de build e faça `npm prune --omit=dev` (ou `npm ci --omit=dev` num estágio limpo) antes de copiar para o runtime |
| Token/senha "removida" do Dockerfile mas ainda visível em `docker history` | Qualquer `ARG`/`ENV` usado durante o build fica gravado na camada, mesmo que apagado depois; imagens já publicadas continuam com o valor | Segredo de build só via `RUN --mount=type=secret,id=...` (BuildKit) ou `.npmrc` montado no build. **Rotacione** o segredo já vazado — trocar o Dockerfile não desfaz a exposição |
| Imagem grande apesar de `rm -rf /var/lib/apt/lists/*` | A limpeza está num `RUN` separado da instalação — o espaço já foi gravado na camada anterior e a remoção não libera nada | Instalação e limpeza no mesmo `RUN`, encadeadas com `&&` |
| `docker compose up` funciona, mas o pod no cluster falha com `exec format error` | Imagem buildada para a arquitetura da máquina local (`arm64` num Mac) e o cluster é `amd64` | `docker build --platform linux/amd64` (ou buildx multi-arch) — e no CI, garanta que o runner builda para a arquitetura do cluster |
| `depends_on` no compose não espera o banco ficar pronto | `depends_on` espera só o container iniciar, não o serviço aceitar conexão | `healthcheck` no serviço + `condition: service_healthy`, ou retry de conexão na própria aplicação |
| Ferramentas de debug (`curl`, `vim`, `netcat`) na imagem final "por garantia" | Aumentam superfície de ataque e tamanho sem necessidade | Debug em produção é com `kubectl debug` (container efêmero), não com ferramenta embutida na imagem — ver `kubernetes.md` |
| Base `alpine` quebra dependência nativa (`bcrypt`, `sharp`, drivers) | musl vs glibc | Use `-slim` (Debian) nos dois estágios em vez de forçar alpine; a diferença de tamanho não compensa o risco |

## Checklist antes de entregar um Dockerfile

- [ ] Multi-stage: o estágio final não contém compilador, devDependencies
      nem fonte — só o artefato e as dependências de runtime.
- [ ] Ordem de camadas: manifesto de dependências (`package*.json`,
      `pom.xml`, `requirements.txt`) copiado e instalado **antes** do
      `COPY . .`.
- [ ] `npm ci` (com lockfile commitado) em vez de `npm install`; se não há
      lockfile, diga isso ao usuário em vez de trocar silenciosamente.
- [ ] `.dockerignore` entregue com pelo menos `node_modules`, `.git`,
      `dist`/`target`, `.env*`.
- [ ] Nenhum `ARG`/`ENV` com segredo; se houve, o aviso de rotação está
      na resposta.
- [ ] `USER` não-root no estágio final; se precisa gravar em disco, um
      volume específico, não filesystem inteiro gravável.
- [ ] Como validar, para o usuário rodar (Docker raramente está disponível
      onde a skill roda): `docker build`, `docker image ls` (tamanho),
      `docker history <img> | grep -i <segredo>` (deve vir vazio), rebuild
      após `touch src/x.ts` (só o estágio de compilação deve reexecutar).
