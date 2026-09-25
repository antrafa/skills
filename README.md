# Antrafa Skills

[![skills.sh](https://skills.sh/b/antrafa/skills)](https://skills.sh/antrafa/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Personal collection of modular AI Agent Skills, designed for autonomous coding agents (Claude Code, Codex, Antigravity, Cursor, and others) and compatible with [skills.sh](https://skills.sh).

Each skill is an independent, self-contained unit with its own `SKILL.md`, references, playbooks, scripts, and evaluation suites.

---

## Skills

### Thinking & Ideation

- [**alterego**](alterego/SKILL.md) — Cognitive clone and daily journey partner that thinks alongside the developer, reproducing senior dev and architect criteria across planning, architecture decisions, code reviews, and verified deliveries.
- [**mentat**](mentat/SKILL.md) — Persistent knowledge vault at `~/.mentat` that carries bugs, architectural decisions, learnings, and snippets across agent sessions as a linked Obsidian graph.
- [**lapida**](lapida/SKILL.md) — Refines a raw idea into a viable, testable proposal through four structured phases (`EXPLORE`, `CHALLENGE`, `REFINE`, `FIT`) using Jobs to Be Done, The Mom Test, Assumption Mapping, and Riskiest Assumption Tests.

### Creation & Execution

- [**forja**](forja/SKILL.md) — Technical mentor where the student writes all the code. Gated learning tracks (AI agents, Mastra, Vercel AI SDK) where progress is unlocked strictly upon proof of execution, logged in `~/.forja`.

### Knowledge & Documents

- [**doc-digest**](doc-digest/SKILL.md) — Produces a one-minute visual synthesis of dense technical documents (SDD, ADR, RFC, PR/MR, implementation plans) and surfaces hidden risks, assumptions, and architectural trade-offs.

### Specialized

- [**dossie-politico**](dossie-politico/SKILL.md) — Produz dossiês cidadãos, neutros e auditáveis sobre políticos, candidatos e mandatos presidenciais brasileiros a partir de dados públicos oficiais (TSE, Câmara, Senado, BCB), gerando relatórios HTML e índice navegável em `~/.dossie-politico/`.
- [**mobilekit**](mobilekit/SKILL.md) — Phase-driven workflow for building and modernizing React Native / Expo mobile apps, from product discovery and design systems to platform implementation, store release, and observability.

---

## Installation

You can install skills using the [`skills` CLI](https://skills.sh):

### Install a specific skill

To install an individual skill directly into your agent configuration:

```bash
# Cognitive partner
npx skills add antrafa/skills --skill alterego

# Knowledge graph vault
npx skills add antrafa/skills --skill mentat

# Idea refinement
npx skills add antrafa/skills --skill lapida

# Technical mentorship
npx skills add antrafa/skills --skill forja

# Document synthesis & risk analysis
npx skills add antrafa/skills --skill doc-digest

# Brazilian political transparency dossiers
npx skills add antrafa/skills --skill dossie-politico

# Mobile development workflow (React Native / Expo)
npx skills add antrafa/skills --skill mobilekit
```

### Install all skills (or select interactively)

To install all skills or pick interactively from a selection menu:

```bash
npx skills add antrafa/skills
```

To install globally for all supported agents on your machine:

```bash
npx skills add antrafa/skills -g
```

---

## Repository Structure

The monorepo follows a flat structure where each skill is an autonomous directory:

```text
antrafa/skills
├── README.md
├── LICENSE
├── .gitignore
│
├── alterego/
│   ├── SKILL.md
│   ├── references/
│   ├── evals/
│   └── scripts/
│
├── mentat/
│   ├── SKILL.md
│   ├── references/
│   ├── evals/
│   └── scripts/
│
├── forja/
│   ├── SKILL.md
│   ├── tracks/
│   └── hooks/
│
├── doc-digest/
│   ├── SKILL.md
│   ├── references/
│   ├── evals/
│   └── scripts/
│
├── lapida/
│   ├── SKILL.md
│   ├── references/
│   └── evals/
│
├── dossie-politico/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   ├── examples/
│   └── tests/
│
└── mobilekit/
    ├── SKILL.md
    ├── workflow/
    ├── prompts/
    └── docs/
```

---

## Development

### Adding or editing skills

1. Each skill lives in its own root-level directory.
2. The skill entry point is `SKILL.md` with valid YAML frontmatter (`name`, `description`, `license`, `metadata`).
3. All internal references (to `references/`, `scripts/`, `prompts/`) must be relative to the skill's own directory.
4. Validate detection with:
   ```bash
   npx skills add . --list
   ```

---

## License

[MIT](LICENSE) © [Antonio Rafael Ortega](https://github.com/antrafa)
