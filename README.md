# antrafa/skills

[![skills.sh](https://skills.sh/b/antrafa/skills)](https://skills.sh/antrafa/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![alterego check-docs](https://github.com/antrafa/skills/actions/workflows/alterego-check-docs.yml/badge.svg)](https://github.com/antrafa/skills/actions/workflows/alterego-check-docs.yml)

Agent skills for software engineers who let AI agents near real systems: safer
collaboration rules, Kubernetes and DevOps work, performance analysis,
structured thinking and persistent memory. They follow the
[Agent Skills](https://agentskills.io) format and install with the
[`skills` CLI](https://skills.sh) into Claude Code, Codex, Cursor and the other
agents it supports.

```bash
npx skills add antrafa/skills                       # pick from a menu
npx skills add antrafa/skills --skill guardrails    # or install one by name
```

---

## How these skills behave

Every skill in this repository follows the same three rules:

- **Read before write.** Diagnostic skills (`cluster-analyzer`,
  `performance-architect`) are read-only by contract. When they find a fix,
  they hand it back as a separate block for you to review and apply.
- **Confirmation where it costs.** Commits, pushes, destructive commands and
  anything visible outside the session each need their own explicit yes. A
  yes for one action does not carry over to the next.
- **Evidence over confidence.** A skill reports what it ran and what it saw.
  If something was not verified, it says so and names the command that would
  verify it.

## Skills

### Safety

| Skill | What it does | Try |
|---|---|---|
| [**guardrails**](guardrails/SKILL.md) | Per-action confirmation for commits, pushes, destructive commands and dependency changes. Finds out where state lives and what the rollback is before acting. Treats an approved plan as a contract, and sends risky changes through a red team / blue team review. Optional Claude Code hook that blocks destructive commands before they run. | `/guardrails` |

### Infrastructure and operations

| Skill | What it does | Try |
|---|---|---|
| [**cluster-analyzer**](cluster-analyzer/SKILL.md) | Read-only Kubernetes diagnosis across many kubeconfigs and contexts. Confirms the target environment first, ranks hypotheses, runs only allow-listed commands and never prints secret values. Ships a namespace snapshot and a cross-environment env diff. | "Pods in staging keep restarting, take a look" |
| [**devops-expert**](devops-expert/SKILL.md) | Writes, reviews and fixes Kubernetes manifests, Helm charts, GitLab CI pipelines, Terraform and Dockerfiles, and validates them with lint, template or plan before calling the work done. | "Review this Helm chart before I deploy it" |
| [**performance-architect**](performance-architect/SKILL.md) | Read-only analysis of latency, capacity, sizing, infrastructure cost, batch windows and scaling architecture. Delivers a technical report plus a summary for decision makers. | "Can this service handle 5x the traffic?" |

### Thinking and workflow

| Skill | What it does | Try |
|---|---|---|
| [**alterego**](alterego/SKILL.md) | A working partner that applies your criteria, voice and limits from a stored profile. Covers a guided dev pipeline, Mikado refactors, code and MR review, ADRs, incident triage and daily planning. | `/alterego daily` |
| [**doc-digest**](doc-digest/SKILL.md) | Turns a long SDD, ADR, plan, RFC or agent reply into a one-minute visual digest and surfaces the hidden risks, assumptions and trade-offs. | "Digest this plan" |
| [**lapida**](lapida/SKILL.md) | Refines a raw idea into a testable proposal in four phases (explore, challenge, refine, fit), using Jobs to Be Done, The Mom Test and assumption mapping. | "I have an idea: …" |
| [**forja**](forja/SKILL.md) | Mentorship where you write all the code. Gated tracks (AI agents, Mastra, Vercel AI SDK) unlock each step only after proof of a real run. | `/forja` |

### Memory

| Skill | What it does | Try |
|---|---|---|
| [**mentat**](mentat/SKILL.md) | A persistent knowledge vault in `~/.mentat` that carries bugs, decisions, learnings and snippets across sessions and agents, as a linked Obsidian graph with salience decay. | "What was that CORS fix?" |

### Mobile

| Skill | What it does | Try |
|---|---|---|
| [**mobilekit**](mobilekit/SKILL.md) | End-to-end workflow for React Native / Expo apps: discovery, design, implementation, store release and observability, including modernizing legacy apps. | `/mobilekit` |

### Civic data (Brazil)

| Skill | What it does | Try |
|---|---|---|
| [**dossie-politico**](dossie-politico/SKILL.md) | Neutral, auditable dossiers on Brazilian politicians and candidates built from official and journalistic sources, with HTML reports and a browsable index. | "Dossiê do deputado …" |

---

## Compatibility

| Agent | Instructions | Hooks and slash commands |
|---|---|---|
| Claude Code | yes | yes (for example the `guardrails` blocking hook) |
| Codex, Cursor and other agents supported by the `skills` CLI | yes | depends on the agent; where none exist, the written rules are the only layer |

Some skills call local tools (`kubectl`, `helm`, `glab`, `python3`). Each
skill's `SKILL.md` or `README.md` lists what it needs.

## Language

The instructions for `guardrails`, `cluster-analyzer`, `devops-expert`,
`performance-architect` and `dossie-politico` are written in Portuguese. The
other skills are written in English. Agents follow either version from prompts
in any language. `dossie-politico` only covers Brazilian public data.

## Quality

- **Evals.** Seven of the eleven skills have a suite in `evals/<skill>/` of
  behavior cases graded on real agent runs, several with trigger cases for when
  the skill should and should not activate. The suites stay out of the skill
  folders, so installing a skill does not ship fixtures written with deliberate
  vulnerabilities and fake secrets; `scripts/link-evals.sh` links each one back
  as `<skill>/evals`, where the runners expect it.
- **Self-tests for scripts.** Shell and Python helpers come with a test that
  runs without external systems. For example, the `guardrails` hook test and
  the `cluster-analyzer` scripts test run against a fake `kubectl`.
- **CI.** `alterego` checks on every change that its command list, links and
  frontmatter stay consistent.

## Install

```bash
npx skills add antrafa/skills                          # interactive selection
npx skills add antrafa/skills --skill <name>           # one skill
npx skills add antrafa/skills -g                       # all skills, global, every supported agent
```

To work from a clone instead, link the skill folder into your agent's skills
directory:

```bash
git clone https://github.com/antrafa/skills.git
ln -s "$PWD/skills/cluster-analyzer" ~/.claude/skills/cluster-analyzer
```

## Contributing

Issues and pull requests are welcome. Before opening one:

1. One skill per root-level directory, with `SKILL.md` as the entry point and
   YAML frontmatter (`name`, `description`, `license`, `metadata`).
2. The `description` says what the skill does, when to use it and, when it
   competes with a neighbor, when **not** to use it. It is the only part an
   agent reads before deciding to load the skill.
3. Keep `SKILL.md` lean. Put details in `references/`, loaded on demand, with
   paths relative to the skill directory.
4. A behavior change comes with an eval case, and a script comes with a test
   that runs without external systems.
5. Check detection with `npx skills add . --list`.
6. Write commits in [Conventional Commits](https://www.conventionalcommits.org)
   format, with one logical change per commit.

## Security

These skills run with your agent's permissions on your machine. Read a skill
before installing it, as you would any script. To report a vulnerability,
contact the maintainer privately through GitHub instead of opening a public
issue.

## License

[MIT](LICENSE) © [Antonio Rafael Ortega](https://github.com/antrafa)
