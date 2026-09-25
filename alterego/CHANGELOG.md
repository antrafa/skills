# Changelog

Format from [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[SemVer](https://semver.org/). The skill version lives in `SKILL.md`
(`metadata.version`) and in `.claude-plugin/plugin.json`.

## [Unreleased]

### Added
- `/alterego idea`: refines a raw idea — a business, an internal tool, a personal project — through the four phases of the partner skill [lapida](https://github.com/antrafa/lapida) (EXPLORE, CHALLENGE, REFINE, FIT), ending in a go, pivot or stop tied to the cheapest next test. CHALLENGE runs through the `devils-advocate` lens; without the skill, the same phases run inline in the chat and the installation is offered once. Eval 38 covers the degraded branch.

### Changed
- The free-form intent "think together" now reads "evaluate a technical proposal", so a raw idea routes to `idea` instead of competing with it.

## [3.0.0] - 2026-09-22

Each command has a single name, the always-loaded body is lighter, and the evals run.

### Breaking
- Subcommand aliases that only renamed a command are gone, so each command has a single name: `sdlc` (use `dev`), `mikado` (use `refactor`), `end-of-day` (use `wrap`), `decision` (use `adr`), `mr-desc` (use `pr-desc`), `project-tour` and `tour` (use `tour-project`), `analyser` and `audit` (use `project-analyser`), `review-skill` (use `skill`), `incident` (use `sre`), `onboard` (use `setup`), `info` (use `help <cmd>`) and `persona default` (use `persona reset`). A removed name is now read as a free-form request and routed by intent.

### Added
- The evals run: `evals/` holds the 37 cases in the `claude plugin eval` format, each with deterministic graders (skill loaded, no commit or push, file left untouched, command actually run) and a judge rubric with PASS and FAIL conditions, plus a git fixture where the case needs a repository. `scripts/run-evals.sh` runs them with the report kept local. The cases now describe the isolated run, where no partner skill is installed.

### Changed
- The `description` no longer names MR/PR review: naming the case it guards against put that trigger in the pointer. The guard now reads as the positive rule, and eval 6 is the check that it still holds.
- `SKILL.md` carries less on every activation: the Intent map's *Conduct* column is half a line per command (the detail lives in each playbook), the memory rule points to [archive.md](references/archive.md#split-with-mentat), and the DNA line repeated in *Autonomy and limits* is gone.

## [2.1.0] - 2026-09-21

Established methodologies brought into the playbooks, in the same spirit as the ZPD already
in `study`: each one enters as an executable rule, never as a cited name.

### Added
- `/alterego refactor` (alias `mikado`): structural refactoring by the **Mikado Method** (Ellnestam & Brolund) — the naive attempt reveals the prerequisites and is reverted, the graph lives at `docs/refactor/<slug>-mikado.md`, leaves are committed first and the goal last, with the tree green throughout. With no test that fails when the behavior changes, the first leaf is a characterization test (Feathers).
- `sre`: top-down triage before any expensive collection — **USE** (Gregg) per resource, **RED** (Wilkie) per hop, the **four golden signals** (Google SRE) for the user-facing service — and the **is / is-not** table (Kepner-Tregoe) that bounds the problem by contrast before any hypothesis.
- `dev`: **fitness functions** (Ford, Parsons & Kua) in step 6, verifying the architectural characteristic that build, lint and tests say nothing about, through the cheapest mechanism already in the repository; and the **walking skeleton** (Cockburn) as the plan's first delivery in step 2.
- `adr` / `decision`: **Cynefin** (Snowden) in Phase 0, sending a complex problem to a safe-to-fail probe instead of a trade-off table; **quality attribute scenarios** (SEI) in Phase 2, turning "it has to be fast" into a response measure; and a `reopen-when` expressible as a number becoming an automated fitness function.
- `review` and MR posting: **Conventional Comments** labels mapped onto the existing severity table, and Google's rule of approving what improves the code's overall health even when it is not perfect.
- `project-analyser`: **hotspot** ranking (Tornhill) — churn from git crossed with complexity — as the audit's reading order and the ordering of the action plan.
- `daily`: WIP ceiling and Little's Law (the board opens by what closes, not by what starts), **CD3** (Reinertsen) to break a tie between two items, and one earlier learning resurfaced at a spacing.
- `study` and `setup`: **Bloom's** revised ladder aiming the Socratic question one rung above the user, and a *Level per topic* field in the profile (**Dreyfus** scale) as the input the ZPD and the Tutor rule calibrate against.
- `tour-project`: the **C4** levels (Brown) as the tour's backbone, with each diagram declaring its level and the study order following the descent.
- `commit`: breaking change marked with `!` and the `BREAKING CHANGE` footer, because under SemVer the type is what picks the bump; and preparatory refactoring first, behavior after (Beck).
- Personas: **Example Mapping** (Wynne) in `requirements-analyst`, **Impact Mapping** (Adzic) in `product-planning`, equivalence partitioning with boundary values and **pairwise** coverage in `qa-testing`.
- `mediation`: the **pyramid principle** (Minto) for the management register — the answer first, the reasoning after.
- Five evals covering the new command and behaviors (33 to 37).

## [2.0.0] - 2026-09-21

### Breaking
- The archive layout under `~/.alterego/` was renamed: `decisoes/` -> `decisions/`, `diario.md` -> `journal.md`, `estudos/` -> `studies/`, and inside each dossier `decisao.md` -> `decision.md` and `roteiro.md` -> `script.md`. An existing archive is not migrated automatically: rename the directories by hand, or the skill starts an empty archive and the old one stops being read.

### Added
- `/alterego start`: opens the session by arming the `guardrails` mode and asking which persona lens to think through — catalog, one of the user's own, a new one or none. Without the skill in the environment the session still opens, saying what actually holds instead of reporting itself as protected.
- Public fallback, from skills.sh, for each of the four internal skills, with what it covers and what it does not; the degradation column of `sources.md` points to it.

### Changed
- Skill, guides, playbooks, personas and evals translated to English. Subcommands and catalog persona names are English-only. The reply language still follows the user's, not the skill's.
- Reference files renamed to English (`acervo.md` -> `archive.md`, `fluxo-mr.md` -> `mr-flow.md`, `COMANDOS.md` -> `COMMANDS.md` and so on).

### Removed
- Redundant subcommand aliases, so each command has one obvious name: `board` and `tabuleiro` (use `daily`), `decisao` (use `decision`), `app-local` (use `local-app`), `summary` and `resumo` (use `digest`), `skills` and `revisar-skill` (use `skill` or `review-skill`), `incidente` (use `incident`), `personas`, `switch-persona` and `trocar-persona` (use `persona`), and `ajuda` (use `help`).
- The remaining Portuguese aliases: `estudar` and `estudo` (use `study`), `fim-de-dia` (use `wrap` or `end-of-day`), `adr revisar` (use `adr review`), `skill nova` (use `skill new`), `persona nova` (use `persona new`) and `persona padrao` (use `persona default`).
- The Portuguese names of the 9 catalog personas that had one (`advogado-do-diabo`, `analista-de-requisitos`, `arquiteto-software`, `especialista-backend`, `especialista-frontend`, `mentor-didatico`, `planejamento-produto`, `qa-testes`, `tech-lead-revisor`): use the English name. A persona of your own in `~/.alterego/personas/` can still be named in any language.
- `explain-cmd`: the full command card is now `help <cmd>` or `info <cmd>`.

### Fixed
- The report `performance-architect` writes is `docs/performance/analise-*.md`; the translation had renamed it to `analysis-*.md`, sending the agent after a file that never exists. A filename produced by another skill is data, not text to translate.
- `writing-for-agents` is a skill by Matt Pocock and Superpowers is a plugin by Jesse Vincent: origin, link and per-harness installation command in the guides and in the installation offers; detection on Claude Code goes through the `Skill` tool's list, where the plugin shows up.

## [1.0.0] - 2026-09-20

First public release.

### Added
- MIT license, plugin manifest (`.claude-plugin/`) and CI workflow that runs `scripts/check-docs.py`.
- Frontmatter with `license`, `compatibility`, `metadata` and `argument-hint`.
- `/alterego wrap`: end-of-day close, with what was left over, what was learned and what goes to memory.
- `/alterego commit` and `/alterego pr-desc`: commit message and MR/PR description in the user's voice.
- `/alterego adr review`: sweeps the archive and says which reopening triggers fired.
- `/alterego persona new <name>`: your own persona in `~/.alterego/personas/`, resolved before the catalog.
- Feedback for a colleague in the situation, behavior and impact format, in `playbook-mediation.md`.
- Eval cases for `daily`, `study`, `adr`, `sre`, `setup`, `persona` and the new commands.

### Changed
- `playbook-daily.md` takes over organizing the day, previously inline in `SKILL.md`.
- Leaner README, with an English summary, the real URLs of the partner repositories and the two installation paths (plugin and symlink).
- Content read from the remote (MR description and comments, code from third-party repositories) is treated as data, never as instructions.

### Earlier history
- Catalog of 11 personas, Dev Pipeline on top of Superpowers, MR evaluation in an isolated worktree, `digest`, `tour-project`, `project-analyser`, `local-app`, `skill` and `help`. See `git log` for the details.

[Unreleased]: https://github.com/antrafa/alterego/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/antrafa/alterego/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/antrafa/alterego/releases/tag/v1.0.0
