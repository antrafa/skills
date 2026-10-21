---
name: cluster-analyzer
description: 'Read-only diagnosis of a Kubernetes cluster, confirming the right kubeconfig and context when there are several environments or clients. Use when the user asks to investigate a cluster, pod, deploy or ingress of an environment (in Portuguese: "pod reiniciando no cluster do cliente X", "dá uma olhada na homologação"). Do NOT use for writing or applying the fix (manifest, Helm, pipeline) nor for any operation that changes the cluster.'
license: MIT
metadata:
  author: Antonio Rafael Ortega
  version: 1.0.0
  category: cloud
  product: all
  stack: all
---

# Cluster Analyzer (read-only)

Kubernetes cluster diagnosis acting as an **observer, never as an
operator**. It is common to have several kubeconfigs (one per client or
environment) or several contexts in the same file — the first step is always
to find out and confirm which one to use, never to assume `kubectl`'s
current context.

## Language

Chat replies and the final report follow the user's language, not the
language of this skill. A user writing in Portuguese ("dá uma olhada na
homologação") gets the whole analysis in Portuguese.

## Execution rules (valid for the whole session)

This access is for diagnosis. You act as an observer from the start to the
end of the conversation — even if the user asks you to "fix" something
during the analysis. If the diagnosis points to a fix, describe the write
command in a separate block, explain the expected impact and hand the
decision and the execution back to the user.

**Every command carries an explicit `--kubeconfig <file> --context <context>`**
(and `--namespace` when applicable). Never switch the user's current context
(`kubectl config use-context`) nor export a global `KUBECONFIG` — this keeps
a context switch from "leaking" outside this task and affecting another of
the user's terminals.

**Allowed (allow-list — nothing outside it):**
- `kubectl get / describe / logs / top / events`
- `kubectl explain`, `api-resources`, `version`, `auth can-i`,
  `config get-contexts`
- `kubectl rollout status`, `kubectl rollout history` (only these two — they
  are pure reads, and the symptom → cause table depends on them to diagnose
  a stuck deploy)
- Output flags: `-o yaml`, `-o json`, `-o wide`, `--show-labels`, `--sort-by`
- `helm list`, `helm get`, `helm status`, `helm history`
- Pipe to a local filter that only reads the output: `grep`, `jq`, `head`,
  `tail`, `sort`, `wc`
- This skill's scripts, which only call verbs from this list:
  `scripts/panorama.sh` and `scripts/envdiff.py`
- `curl` GET of headers only on a service URL (`curl -sk -m 15 -o
  /dev/null -D - <url>`), to tell whether the proxy or the application
  answered. No `-X`, `-d` or `--data`.

**Forbidden (any command outside the allow-list, including):**
`apply`, `create`, `patch`, `replace`, `edit`, `delete`, `scale`, `set`,
`label`, `annotate`, `rollout restart`/`undo`/`pause`, `cordon`, `drain`,
`uncordon`, `taint`, `exec`, `cp`, `attach`, `port-forward`, `proxy`, `run`,
`debug`, `helm install`/`upgrade`/`uninstall`/`rollback`, `kubectl config
set-*`, `--force`, `--dry-run=server`, and piping to anything that runs a
command (`xargs`, `sh`, `bash`, `kubectl`).

**Usage limits:**
- `logs` always with `--tail=200` (or `--since=<window>`); increase only if
  the 200 lines don't show the error. An unbounded log dumps thousands of
  lines and buries the evidence.
- `top` depends on metrics-server. If it fails with `Metrics API not
  available`, say so and use `resources` in `get pod -o yaml` and the
  `Last State` from `describe` instead.
- Before the first `helm`, run `command -v helm`. Without `helm`, identify
  the release by its labels (`app.kubernetes.io/managed-by`, `helm.sh/chart`,
  `app.kubernetes.io/instance`) — the `sh.helm.release.v1.*` secrets hold
  the values with passwords and stay out of the investigation.

**A secret shows up as name and size, never as a value.** `get` is on the
allow-list, but the sensitive things it returns stay out of the reply:
- Secret: use `describe secret` (shows keys and sizes, no value). To learn
  only which keys exist: `get secret <name> -o jsonpath='{.data}' |
  jq 'keys'`. Base64 is not protection — `get secret -o yaml` exposes the
  password.
- In `get configmap`, `get pod/deploy -o yaml` (the `env` block) and `helm
  get values`/`helm get all`, any value that looks like a credential
  (password, token, key, connection string with user/password) comes out as
  `***`.
- Kubeconfig: inspect it only with `config get-contexts`; the raw file
  (`cat <kubeconfig>`) carries certificates and tokens.

**Production logs carry citizens' personal data.** Summarize what the log
shows (error, time, frequency) and mask CPF (the Brazilian taxpayer ID),
email and person names in the quoted excerpts.

## Step 1 — Choose the kubeconfig

List the available configuration files before asking anything — don't ask
the user to remember the file name off the top of their head:

```bash
echo "$KUBECONFIG"; ls -p ~/.kube/ 2>/dev/null
```

Candidates: the files listed in `$KUBECONFIG`, `~/.kube/config` and the
other kubeconfigs in `~/.kube/` (ignore directories such as `cache/` and
`http-cache/`).

Reply with the list found, the question of which environment to
investigate and, **in the same message**, the Step 2 hypotheses — they
don't depend on the environment, and the user can correct the course along
with the confirmation. File names usually follow
`<client>-<environment>[-<platform>].yaml` (e.g. `clientea-hml.yaml`,
`clienteb-prd-oke.yaml`), but **confirm the client/environment with the
user instead of deducing it from the name** — different clients can have
similar acronyms, and picking `prd` instead of `hml` is exactly the kind of
mistake too expensive to risk. If the list is long, ask in free text instead
of trying to fit everything into a multiple-choice question.

Once the file is chosen, run and report the context(s) it contains (a
kubeconfig can have more than one):

```bash
kubectl --kubeconfig <chosen-path> config get-contexts
```

If there is more than one context, confirm which one to use.

**Done when:** the user has confirmed file and context, and you have written
in text which environment you are going to investigate — they need to be
able to read it and notice at once if it is wrong.

## Step 2 — Ranked hypotheses

Write the 3 to 4 most likely causes of the reported symptom, in order of
probability, and which read command confirms or rules out each one. This
turns the session into a directed investigation (each output eliminates
hypotheses) instead of a collection of commands "to see what shows up" — and
lets the user reorder them if they know something (e.g. "there was a deploy
this morning").

Example for "pod restarting all the time":

1. `OOMKilled` — memory limit below the real usage. Confirm in
   `describe pod` (`Last State: Reason: OOMKilled`, exit 137) and `top pod`.
2. Aggressive liveness probe killing the app during boot or under load.
   Confirm in the `describe` `Events` (`Liveness probe failed`, `Killing`)
   and in the startup time in `logs --previous`.
3. External dependency unavailable (database, queue, auth service) making
   the app abort at startup. Confirm at the end of `logs --previous`
   (connection stack trace, `Connection refused`, `ORA-`, timeout).
4. Recent deploy with a broken image/config. Confirm in
   `rollout history deploy/<name>` and `get deploy -o yaml` (image, env).

For other symptoms, build the list from `references/symptoms.md` and the
evidence — with no causes that neither of the two supports. It holds: pod
symptom → cause, **what looks like a problem but is normal** (check it
before turning a strange line into a hypothesis), where an HTTP error
originates (proxy or application) and what to compare when it works in one
environment and not in the other.

## Step 3 — Investigate

0. If the symptom doesn't point to a specific resource yet, start with the
   namespace overview, which runs the general reads in a single call:

   ```bash
   scripts/panorama.sh <kubeconfig> <context> <namespace>
   ```

   A section with `FAILED:` (403, missing CRD, metrics-server absent)
   doesn't stop the others: record what was left unread and carry on with
   the rest. When the question is "why does it work in A and not in B", run
   `scripts/envdiff.py <deployment> --a <kubeconfig> <context> <namespace>
   --b <kubeconfig> <context> <namespace>` — each side with the kubeconfig
   and context confirmed in Step 1.
1. After the overview, one command at a time. Show the command before
   running it, wait for the result, interpret the output before the next
   step — each result should shape the next diagnostic question, exactly
   like investigating a bug.
2. If a command fails with `403 Forbidden`, that is expected and part of the
   permission model — don't try to get around it, don't look for an
   alternative credential, don't suggest widening the permission. Report
   what the missing access means for the diagnosis and continue through
   another available read path.
3. Report only output from commands you actually ran. If you didn't run it,
   say you didn't run it.
4. When several workloads fail together, find what failed first before
   investigating the others: the overview events already come sorted by
   `lastTimestamp`. The database that went down at 10:02 explains the
   applications in `CrashLoopBackOff` since 10:03; investigating each
   application is chasing the cascade. Say in the report which is the
   originating failure and which are effects.

**Done when:** each Step 2 hypothesis is marked *confirmed*, *ruled out* or
*blocked* (403, metrics-server absent, event already expired), each mark
backed by the command and the output excerpt that supports it. If all were
ruled out, that is also a result: say which were ruled out and which read
suggests the next hypothesis.

## Wrapping up the analysis

Summarize what was found (symptom, evidence collected, which Step 2
hypothesis was confirmed and which were ruled out) and, if a fix is needed,
present it in a separate block for the user to review and apply — never
applied by this skill.

Before writing the fix, check who manages the resource — the labels already
come in `get -o yaml` / `--show-labels`:

- `app.kubernetes.io/managed-by: Helm`, `helm.sh/chart` or the
  `meta.helm.sh/release-name` annotation: the fix goes in the release's
  values/chart (usually in the client's environment repository). A direct
  `kubectl set`/`patch` is undone on the next `helm upgrade`, and the
  problem comes back without anyone knowing why. Point to the values field
  to change; to write the corrected manifest/values, the `devops-expert`
  skill comes in afterwards.
- Resource with no apparent manager: the corresponding `kubectl` write
  command, with the expected impact (e.g. "triggers a new rollout").
