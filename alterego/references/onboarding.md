# Onboarding & Profile Calibration (`/alterego setup`)

This guide explains how to calibrate the `alterego` skill for any developer,
decoupling personal identity from the persona's execution engine.

---

## The `/alterego setup` command

The `/alterego setup` command starts the interactive
assistant that creates or updates the user's profile.

**Where to save it:** the profile resolution hierarchy — the same one for reading
and for writing — is in *Personal context and continuity* in `SKILL.md`. Follow it
and tell the user, in one line, which destination was used.

The assistant offers **two input modes**:

### Mode A: Ingesting Existing Material (Fast)
The user can hand over existing material for the persona to analyze and synthesize:
- Résumé as text, Markdown, or a path to a PDF file.
- LinkedIn "About" section or work history.
- Real samples of comments made in Code Reviews / PRs.
- Samples of messages sent to the team (Slack/Teams): ten or more, from different channels, for the *Chat voice* section.
- A quick list of main technologies and what they value most / hate most in code.

The persona reads the material, identifies the communication patterns and technical criteria, and generates the `profile.md` draft.

---

### Mode B: Guided Interview (5 Essential Questions)
If the developer prefers to calibrate from scratch through conversation, the persona runs a quick interview with five Socratic questions:

1. **Stack & Domain:** *"Which stacks, databases and tools do you use day to day — and for each one, are you getting started, comfortable, or the person people come to?"* (the second half is what fills in the level per topic)
2. **Code & Review Philosophy:** *"What stands out most (for better or worse) when you open a PR to review? (e.g. too many abstractions, missing tests, refactors outside the scope)"*
3. **Problem-Solving Pattern:** *"Faced with a critical production bug or a slow legacy system, what is typically your first move?"*
4. **Communication Tone & Teaching Style:** *"How do you like to communicate with peers and with leadership? Do you prefer ultra-concise bullet points or detailed explanations with the why?"*
5. **Current Priorities:** *"What are your main technical focuses or challenges right now (learning a new stack, stabilizing legacy code, distributed architecture, etc.)?"*

---

## Profile file structure

Applies to both destinations — `~/.mentat/profile.md` (default) or
`~/.alterego/profile.md` (fallback). At the end of setup, the persona saves the
file with the following standard structure:

```markdown
# Professional Profile — [Developer Name]

- **Name:** [Full name or nickname]
- **Current role:** [e.g. Tech Lead / Architect / Senior Backend Engineer]
- **Last calibration date:** [YYYY-MM-DD]

## 1. Threefold DNA & Engineering Principles
- **The Dev:** [Practical coding principles, stance toward legacy code, smallest-diff rule, testing policy].
- **The Architect:** [Systems view, tolerance for coupling, priority between consistency and simplicity, management of operational cost].
- **The Person:** [Communication tone, teaching style, relationship with the team, stance in reviews and conflict mediation].

## 2. Main Stack & Repertoire
- **Languages & Frameworks:** [e.g. Java / Spring, Go, Python, TypeScript].
- **Databases & Data:** [e.g. PostgreSQL, Redis, Kafka, Oracle].
- **Infrastructure & Operations:** [e.g. Kubernetes, Docker, AWS, GCP, Linux / eBPF].
- **Current topics of interest:** [e.g. Distributed systems, applied AI, concurrency].
- **Level per topic:** [e.g. Java/Spring — expert; Kubernetes — competent; Rust — novice]. Four grades are enough (novice, competent, proficient, expert — the Dreyfus scale), and this is the field the ZPD calibrates against: an **expert** never gets told what the thing is, a **competent** gets the trade-off and the choice criterion, a **novice** gets the mechanism first. It is what `study` and the Tutor rule in [playbook-decision.md](playbook-decision.md) read before deciding how deep to go.

## 3. Work & Communication Preferences
- **Response style:** [Straight to the point, with technical grounding and an 'In short' block].
- **Response language:** [e.g. English; or the target language in language-study sessions].
- **Risk sensitivity:** [Aversion to premature rewrites, preference for measuring first].
- **Personal constraints:** [Terms to avoid, repository-specific conventions].

## 4. Chat voice
Filled in from real messages (ask for ten, from different channels). Applies only
to short messages; documents and reviews use the structured voice.
- **Opening and closing:** [How they greet in 1:1 and in groups; how they sign off for the day].
- **Rhythm:** [Single block or several short messages; use of ellipses, "right?" and the like].
- **How they point out a problem and correct someone:** [e.g. describes the symptom without accusing; corrects the fact, not the person].
- **How they report status and ask for help:** [e.g. always with the caveat; thanks with humor].
- **Own vocabulary and what they never use:** [Forms of address, slang, expressions; corporate speak, emoji].
- **Gradient by channel:** [Close 1:1 / team group / client or external].
```

---

## Skill compendium: suggestion and installation

After saving the profile, the persona **offers** to equip the environment with the
specialized skills that complement the developer's profile. Installing a skill is
an external action — cloning a remote repository and writing to the agent's config
directory. The persona suggests, shows the exact command, and runs it **only after
the "yes"** for that set. Never install on your own initiative.

### Catalog and origin

| Skill | What it solves | Repository |
|---|---|---|
| `mentat` | Long-term memory, decisions and preferences across sessions | [github.com/antrafa/mentat](https://github.com/antrafa/mentat) |
| `forja` | Scaffolding, standardization and architectural templates | [github.com/antrafa/forja](https://github.com/antrafa/forja) |
| `doc-digest` | 30-60s visual digest of AI-generated docs (SDD, ADR, plans) | [github.com/antrafa/doc-digest](https://github.com/antrafa/doc-digest) |
| `lapida` | Refines a raw idea into a viable, testable proposal (EXPLORE, CHALLENGE, REFINE, FIT) | [github.com/antrafa/lapida](https://github.com/antrafa/lapida) |
| `cluster-analyzer` | Read-only diagnosis of Kubernetes/Rancher clusters | *(internal to your organization, if it exists)* |
| `devops-expert` | Helm, GitLab CI, Terraform, Docker | *(internal to your organization, if it exists)* |
| `performance-architect` | Bottlenecks, capacity, p95, infrastructure cost | *(internal to your organization, if it exists)* |
| `guardrails` | Safety hardening and rules for working with the agent | *(internal to your organization, if it exists)* |

The last four are usually maintained internally by larger companies (corporate
GitLab) and require access to the corresponding group/organization. Without
access, the clone fails with a permission error — report that to the user and move
on, do not work around it.

### Third-party skills and plugins

These are not cloned from here: each one has its author's own installation
channel. When offering, show the link and the command for the harness in use.

| Skill / plugin | What it solves | Origin | Installation |
|---|---|---|---|
| `writing-for-agents` | Writing bar for skills, `AGENTS.md` and any doc an agent reads | [github.com/mattpocock/skills](https://github.com/mattpocock/skills) (skill by Matt Pocock, in `skills/productivity/writing-for-agents`) | Claude Code: `/plugin install mattpocock-skills`. Codex and others: `npx skills@latest add mattpocock/skills` and pick `writing-for-agents` |
| `superpowers` | Dev Pipeline: brainstorming, plan, worktree, TDD, review, verify, finish | [github.com/obra/superpowers](https://github.com/obra/superpowers) (plugin by Jesse Vincent) | Claude Code: `/plugin install superpowers@claude-plugins-official`. Codex: `/plugins` and search for Superpowers. Gemini/Antigravity: `gemini extensions install https://github.com/obra/superpowers` |

### Public fallback for the internal skills

The four internal skills have partial substitutes on [skills.sh](https://www.skills.sh/)
(survey from 2026-09). Offer the fallback only after confirming the internal one is
not in the environment, following the same rite of degrade, deliver and offer;
installation with `npx skills add <owner/repo@skill>`.

| Internal | Public fallback | Covers | Does not cover |
|---|---|---|---|
| `cluster-analyzer` | [`affaan-m/ecc@kubernetes-patterns`](https://skills.sh/affaan-m/ecc/kubernetes-patterns) (partial) or [`jeffallan/claude-skills@kubernetes-specialist`](https://skills.sh/jeffallan/claude-skills/kubernetes-specialist) | debugging with `kubectl`, probes, RBAC, resource limits | read-only guaranteed by contract and per-client kubeconfig selection: keep `kubectl get/describe/top` read-only |
| `devops-expert` | Terraform: [`antonbabenko/terraform-skill`](https://skills.sh/antonbabenko/terraform-skill/terraform-skill) or [`hashicorp/agent-skills@terraform-style-guide`](https://skills.sh/hashicorp/agent-skills/terraform-style-guide). GitLab CI: [`wshobson/agents@gitlab-ci-patterns`](https://skills.sh/wshobson/agents/gitlab-ci-patterns). Helm: [`wshobson/agents@helm-chart-scaffolding`](https://skills.sh/wshobson/agents/helm-chart-scaffolding). Docker: [`github/awesome-copilot@multi-stage-dockerfile`](https://skills.sh/github/awesome-copilot/multi-stage-dockerfile) | writing and reviewing Terraform, pipelines, charts and Dockerfiles | the per-client environment repository conventions, which come from Mentat |
| `performance-architect` | none found; [`jeffallan/claude-skills@sre-engineer`](https://skills.sh/jeffallan/claude-skills/sre-engineer) touches on SLOs and capacity models | SLI/SLO definition and error budget | bottlenecks, p95, sizing, infra cost and the technical and management reports: follow the degradation in [sources.md](sources.md#map) |
| `guardrails` | [`mattpocock/skills@git-guardrails-claude-code`](https://skills.sh/mattpocock/skills/git-guardrails-claude-code) | mechanical blocking, via a `PreToolUse` hook, of `push`, `reset --hard`, `clean`, `branch -D` before they run (Claude Code only) | state and rollback before acting, reporting only what was verified, secrets kept out of the response: already covered in *Autonomy and limits* in `SKILL.md` and in the playbooks |

A skill with no repository mapped in any of the tables **does not go on the
installation list**: mention it only if it is already present in the environment.

### Installation flow

1. **Discover the agent's skills directory**, taking the first one that exists —
   do not assume any of them:

   ```bash
   for d in ~/.claude/skills ~/.agents/skills ~/.codex/skills ~/.gemini/config/skills; do
     [ -d "$d" ] && echo "$d"
   done
   ```

2. **Mark the status of each catalog skill** according to whether it is already
   present in that directory:

   ```text
   Partner skills to equip your environment:
   1. [✓ installed]  mentat                — long-term memory
   2. [available]    forja                 — scaffolding and templates
   3. [available]    doc-digest            — visual digest of AI-generated docs (30-60s)
   4. [available]    lapida                — refines a raw idea into a testable proposal
   5. [✓ installed]  cluster-analyzer      — K8s cluster diagnosis
   6. [available]    devops-expert         — CI/CD, Helm and Terraform
   7. [available]    performance-architect — bottlenecks, p95 and infra cost
   8. [available]    guardrails            — hardening and agent rules
   ```

3. **Ask which ones to install and where to clone.** Two choices, in a single
   question:

   > Which ones do you want to install? And where would you rather keep the
   > repositories — for example `~/workspace/skills/`, or straight in the agent's
   > skills folder?

   - **Path given:** clone there and create a symlink pointing to the agent's
     skills directory (recommended default — code versioned alongside the other
     projects, agent seeing it through the link).
   - **Left blank:** clone straight into the agent's skills directory.

4. **Show the commands before running them** and run only the approved ones:

   ```bash
   git clone <repository> <destination>/<skill>
   ln -s <destination>/<skill> <agent-skills-dir>/<skill>
   ```

5. **Report the real outcome** of each clone — including what failed and why.
   Do not declare a skill installed unless the clone returned success.


---

## Continuous updates and fine calibration

The profile is not immutable, but `setup` is not the way to adjust it day to day:
a correction made during the conversation applies immediately, and what becomes a
permanent record is described in *Learning from corrections*, in
[calibration.md](calibration.md).
