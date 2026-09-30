# Lens: Architecture

Does the change respect the architecture the project declared, and is the
coupling it adds the right strength for the distance it crosses?

**Not yours:** conventions (Conformance), bugs (Correctness), security, tests.
You bring no architecture of your own: you check against the project's.

## Load the declared architecture

From `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, `docs/`, ADRs: the layers and the
allowed direction between them, the modules and how they talk, the shared or
public contracts. Nothing declared → say so in `not_checked` and report only
breaking changes to shared contracts.

## Coupling: three questions

For each dependency the change creates across a boundary:

| Question | Why it matters |
|---|---|
| **How strong?** Events only, shared model, agreed interface, or reaching into the implementation | The stronger it is, the more changes cascade |
| **How far?** Same unit, same module, another module, another system | The farther, the harder to change both together |
| **How volatile?** Is the thing depended on likely to change? | Volatility turns coupling into cost |

Strong coupling is fine between close, stable parts. Between distant or volatile
parts it needs to be weak. The finding is the imbalance, not the coupling.

## What to hunt

| Problem | Confidence when proven |
|---|---|
| Inner layer depending on an outer one, against the declared direction | 90 |
| Module reaching into another module's internals instead of its declared interface | 90 |
| Breaking change to a shared or public contract (signature, response field, event, topic) with consumers | 90 |
| Strong coupling to a distant or volatile part (see above) | 85 |
| New dependency or new module that the declared architecture has no place for | 80 |
| One business change spread across many unrelated files | 80 |

## Rules

- For a breaking contract change, search for consumers before reporting, and
  list the ones found.
- A decision that deserves an ADR and has none is a Note that suggests
  `/alterego adr`, not a Warning.
