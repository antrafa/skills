# Docker — Pitfalls and Checklist

The basics (multi-stage, layer order for caching, `.dockerignore`, non-root
`USER`, `alpine`/`slim` base) you already know — no tutorial needed here.
This file covers only what usually slips through a Dockerfile review and
what to check before calling an image ready.

## Pitfalls that slip through

| Symptom / finding | Real cause | What to do |
|---|---|---|
| Build only works with the host's `node_modules/` present | `ENV NODE_ENV=production` declared **before** `npm install`/`npm ci` makes npm skip devDependencies, so `tsc`/the bundler is never installed; the build "passes" because `COPY . .` brought in the local `node_modules/` — and breaks as soon as a `.dockerignore` excludes the folder | Only set `NODE_ENV=production` in the runtime stage; install devDeps in the build stage and run `npm prune --omit=dev` (or `npm ci --omit=dev` in a clean stage) before copying to runtime |
| Token/password "removed" from the Dockerfile but still visible in `docker history` | Any `ARG`/`ENV` used during the build is recorded in the layer, even if deleted later; images already published keep the value | Build secrets only via `RUN --mount=type=secret,id=...` (BuildKit) or an `.npmrc` mounted at build time. **Rotate** the leaked secret — changing the Dockerfile does not undo the exposure |
| Large image despite `rm -rf /var/lib/apt/lists/*` | The cleanup is in a `RUN` separate from the install — the space was already recorded in the previous layer and the removal frees nothing | Install and cleanup in the same `RUN`, chained with `&&` |
| `docker compose up` works, but the pod in the cluster fails with `exec format error` | Image built for the local machine's architecture (`arm64` on a Mac) and the cluster is `amd64` | `docker build --platform linux/amd64` (or buildx multi-arch) — and in CI, make sure the runner builds for the cluster's architecture |
| `depends_on` in compose does not wait for the database to be ready | `depends_on` only waits for the container to start, not for the service to accept connections | `healthcheck` on the service + `condition: service_healthy`, or connection retry in the application itself |
| Debug tools (`curl`, `vim`, `netcat`) in the final image "just in case" | They increase attack surface and size for no reason | Debugging in production is done with `kubectl debug` (ephemeral container), not with a tool baked into the image — see `kubernetes.md` |
| Pod takes the whole `terminationGracePeriodSeconds` to stop and the app does not close connections | `ENTRYPOINT`/`CMD` in shell form (`CMD node app.js`) or an `sh -c` script without `exec`: PID 1 is the shell, which does not forward SIGTERM to the app | Exec form (`CMD ["node", "app.js"]`), or `exec` on the last line of the entry script |
| `alpine` base breaks a native dependency (`bcrypt`, `sharp`, drivers) | musl vs glibc | Use `-slim` (Debian) in both stages instead of forcing alpine; the size difference is not worth the risk |

## Checklist before delivering a Dockerfile

- [ ] Multi-stage: the final stage contains no compiler, devDependencies or
      source — only the artifact and the runtime dependencies.
- [ ] Layer order: dependency manifest (`package*.json`, `pom.xml`,
      `requirements.txt`) copied and installed **before** `COPY . .`.
- [ ] `npm ci` (with a committed lockfile) instead of `npm install`; if there
      is no lockfile, tell the user instead of silently switching.
- [ ] `.dockerignore` delivered with at least `node_modules`, `.git`,
      `dist`/`target`, `.env*`.
- [ ] No `ARG`/`ENV` with a secret; if there was one, the rotation warning is
      in the reply.
- [ ] Non-root `USER` in the final stage; if it needs to write to disk, a
      specific volume, not a fully writable filesystem.
- [ ] How to validate, for the user to run (Docker is rarely available where
      the skill runs): `docker build`, `docker image ls` (size),
      `docker history <img> | grep -i <secret>` (must come back empty),
      rebuild after `touch src/x.ts` (only the compile stage should re-run).
