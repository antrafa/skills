# Pitfalls that cost time

Read before improvising. Each item here is a mistake that looks right at the
time, passes review and only shows itself after the deploy. When a new
pitfall costs real time in a session, propose to the user adding it here,
with the symptom it produces and how to avoid it.

## `kubectl apply` does not delete what left the file

`apply` creates and updates; it does not remove. Renaming a resource in the
manifest (the `metadata.name` of a Service, ConfigMap, Secret or
VirtualService) creates the new one and leaves the old one alive in the
cluster. With routes, the orphan can keep serving: two VirtualServices for
the same host and prefix conflict, and which one serves is not something you
can rely on.

- When renaming, also deliver the `kubectl delete` of the old name, as a
  separate step and with confirmation.
- With Helm this does not happen: `helm upgrade` removes what left the
  chart. Mixing manual `apply` with resources from a release creates exactly
  this kind of leftover.

## The cluster is not git

ConfigMap and Secret edited by hand, replicas scaled to zero on purpose, an
image swapped by an emergency `set image`: the live state diverges from the
repository without leaving a trace in git. Applying the file "as is" undoes
those changes without warning.

- Before applying to an environment in use, the user runs `kubectl diff -f`
  (or `helm diff upgrade`) and reads every difference.
- A Secret flagged as changed in the diff is a manual value the apply will
  overwrite — sometimes with empty. Ask first.
- A different `replicas` may be someone's decision (shutdown, maintenance),
  not drift to fix.

## Undefined variable turns into empty text

`envsubst`, `${VAR}` in shell and most templates replace a nonexistent
variable with an empty string, without error. The manifest renders, the
apply passes, and the pod starts with `DB_URL=` or an image `registry/app:`.

- Render and read before applying; look for `: $`, `=$` and `:""` in the
  result.
- In shell, `set -u` makes the script fail on an undefined variable.
- With `envsubst`, pass the explicit list (`envsubst '$IMAGE $TAG'`) so it
  does not wipe `$` that should stay literal.

## Base64 is not protection

What is in `Secret.data` is only encoded. `get secret -o yaml`, a
`values.yaml` with a password or a committed `.env` with `*_ENCODED` expose
the credential just like plain text.

## Commit message that triggers a pipeline

Pipelines that react to a marker in the commit message (`[deploy]`,
`[skip ci]`, `[upgrade ...]`) also fire on a manual commit that repeats the
marker by chance or by copy. Before writing the message, check the `rules`
of `.gitlab-ci.yml` (or equivalent) for `$CI_COMMIT_MESSAGE`.

## Environment repository that the pipeline also changes

When the pipeline commits to the configuration repository itself (an image
tag bump, for example), editing on an old clone and applying rolls the
environment back to the previous version. Update (`git pull --ff-only`)
before editing, and again before applying.

## Corporate network and commands that never finish

Slow DNS, proxy and firewall make `git`, `curl`, `helm repo update` and
`docker pull` hang without error. Use an explicit timeout
(`timeout 30 <cmd>`, `curl -m 15`) and treat the timeout as information:
network, not a broken tool.
