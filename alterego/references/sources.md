# Sources of evidence

Map of `evidence needed → skill that produces it`. Alterego **consumes or invokes**;
it never reimplements.

## Precedence ladder

1. **Artifact already exists** → read it and cite path, section and date. Reuse it
   if version, configuration, environment and load still represent the current
   decision. If there has been a relevant change or the validity is unknown, treat
   it as history and refresh only the affected evidence.
2. **Evidence missing or needs refreshing, skill available** → load it through the
   mechanism available in the environment; use the `Skill` tool when it exists.
3. **Unavailable** → do the minimum possible collection. Record source, moment and
   reach of what was observed; label as **hypothesis** or **assumption** whatever
   was not verified and write down the measurement that would close the gap.
4. **Never replicate** the logic.

Before invoking any expensive skill, tell the user what you are going to run and
why. They may already have the result in another folder. A skill marked *(if
installed)* may not exist in the environment: confirm before announcing it, and
fall back to the degradation column without turning the absence into a blocker.

## External facts carry a date

Library APIs, framework defaults, CLI flags and supported versions change after
the training cutoff. Whenever the recommendation or the generated code depends on
them — adopting a dependency, generating scaffolding, bumping a version, studying
a framework — the docs for the current version come **before** writing.

`context7` solves this (`resolve-library-id` to find the library, `query-docs` for
the current docs). It is a plugin/MCP, not a directory skill: detect it by the
available tool, not with `ls`.

If absent, the same three steps of *degrade, deliver, offer* below apply, with
its own installation:

```bash
# Claude Code
/plugin install context7@claude-plugins-official
# Codex, Antigravity and other harnesses — MCP server
npx -y @upstash/context7-mcp
```

If declined or unavailable, infer the version from the environment's own
evidence, in this order, and say which one you used: the project's lockfile and
manifest (`package-lock.json`, `pom.xml`, `go.sum`); the registry (`npm view <pkg>
version`, `pip index versions <pkg>`); the official repository's release notes.
With none available, state which version your knowledge is from — dated knowledge
is an assumption, and assumptions get labeled.

## Missing catalog skill: degrade, deliver, offer

Applies to any skill in the catalog at [onboarding.md](onboarding.md#catalog-and-origin)
— `mentat`, `forja`, `doc-digest` and the rest. Before announcing a skill, detect it:

```bash
# one line per harness; the first one that exists defines the skills directory
for d in ~/.claude/skills ~/.agents/skills ~/.codex/skills ~/.gemini/config/skills; do
  ls -d "$d"/<skill> 2>/dev/null
done
```

Not found? Three steps, in this order, never inverted:

1. **Say in one line** that the skill is not in the environment and that you are
   proceeding through the degradation column. A missing skill is never a blocker.
2. **Deliver the degraded result** — the requested work goes out in the same
   answer. Do not swap the deliverable for an installation invitation.
3. **Offer the installation at the end**, once per session and per skill, with the
   catalog repository. Installing is an external action: show the command and run
   it only after the "yes" for that skill — the full flow is in
   [onboarding.md](onboarding.md#installation-flow).

A recorded refusal is not repeated in the same session. A skill with no repository
mapped in the catalog is not offered: mention it only if it is already present.


## Map

| Evidence the decision needs | Skill | Artifact it usually leaves behind | Degradation without it |
|---|---|---|---|
| State of a k8s cluster, restarting pod, resources, events | `cluster-analyzer` | cluster analysis in md/html | partial [public fallback](onboarding.md#public-fallback-for-the-internal-skills); without it, read-only `kubectl get/describe/top`, marked as a one-off sample |
| Bottleneck, capacity, sizing, p95, infra cost | `performance-architect` | `docs/performance/analise-*.md`, `resumo-decisao-*.md` | no [public fallback](onboarding.md#public-fallback-for-the-internal-skills) that measures up; the user's assumption about volume, labeled as an assumption |
| How a corporate legacy system works | architecture memories in Mentat / local skills *(if installed)* | architecture notes and flows in `docs/` | direct reading of the code for the flow in question |
| Structure, dependencies and relationships of a repository | `graphify` | `graphify-out/` | `Glob` + `Grep` over the repo |
| Architecture, sequence, lifecycle diagram | `archify` *(if installed)* | standalone html with SVG | inline mermaid in the answer itself |
| Writing the Helm, pipeline, Dockerfile, Terraform for the chosen option | `devops-expert` | manifests / `.gitlab-ci.yml` | [public fallback](onboarding.md#public-fallback-for-the-internal-skills) per tool (Terraform, GitLab CI, Helm, Docker); without it, describe the change without generating the file |
| Durable history and profile: past decisions and preferences | `mentat` | `~/.mentat/entries/*.md`, `profile.md` | local fallback in `~/.alterego/` |
| Strict security check, linter and guardrails | `guardrails` | compliance / linter reports | [public fallback](onboarding.md#public-fallback-for-the-internal-skills) for the git layer (hook); the rest is already a rule of this skill; manual check of patterns and diff |
| Pedagogical structuring, ZPD and learning progression | `teach` *(if installed)* | `MISSION.md`, `lessons/*.html` | `references/playbook-study.md` inline |
| Scaffolding, standardization and architectural templates | `forja` *(if installed)* | code skeletons / templates | manual creation from local patterns |
| Investigation and deep reading of RFCs, papers and docs | `research` *(subagent, if available)* | synthesized research report | web search or direct reading of the source |
| Visual digest of SDDs, ADRs, plans and AI-generated docs | `doc-digest` *(or `/alterego digest`)* | visual digest with Mermaid and decision matrix (or `docs/digests/*.html`) | bullet summary and inline mermaid in the chat |
| Refining a raw idea into a viable, testable proposal (problem, riskiest assumption, next test) | `lapida` *(or `/alterego idea`)* | `ideas/<slug>.md` with the four phases and a go / pivot / stop recommendation | the four phases inline in the chat, without the idea file ([playbook-idea.md](playbook-idea.md#2-degraded-path-without-the-skill)) |
| Writing bar for a document an agent reads (skill, `AGENTS.md`, reference) | [`writing-for-agents`](https://github.com/mattpocock/skills) *(skill by Matt Pocock, if installed)* | the reviewed document itself | diagnosis levels of [playbook-skill.md](playbook-skill.md) inline |
| Guided-development Dev Pipeline (conception, plan, worktree, tdd, review, evidence, delivery) | [`superpowers`](https://github.com/obra/superpowers) *(plugin; path varies by harness, see [playbook-dev.md](playbook-dev.md))* | plans in `docs/superpowers/plans/`, worktree, green suite, review verdict | conduction in the chat with the same seven gates |
| Current docs or API of an external library, framework, SDK or CLI | `context7` *(plugin/MCP)* | answer with the docs for the current version | infer through the [version ladder](#external-facts-carry-a-date) and label as dated knowledge |
| Updating a client's version or environment | environment memories in Mentat / local skills *(if installed)* | diff in the environment repo | list the points to change, without applying |

## What the persona does without delegating

MR/PR impact analysis **is not delegated**: it is an internal capability, described
in [mr-flow.md](mr-flow.md) and [playbook-review.md](playbook-review.md). Do not
look for a partner skill for it.

## Golden rule of invocation

Invoking an analysis skill **is not** letting it make the decision. Its result
enters Phase 2 as evidence and remains subject to Phase 3's critique. A skill's
report is not revealed truth: it has assumptions too, and they get labeled too.

## How this table grows

New skill = **one line**. Fill in the four columns. If you cannot write the
degradation column, the skill probably does not produce decision evidence — and
does not belong in this table.
