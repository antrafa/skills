# Lens: Approach

Is this the right way to solve the problem at all? The other lenses check the
diff as written; this one assumes the diff is correct and asks whether it should
exist in this shape.

**Not yours:** bugs inside the change (Correctness), project conventions
(Conformance), exploitable flaws (Security), where state lives and how to roll
back (State and rollback), test quality (Tests), module boundaries
(Architecture), whether the criteria were met (Acceptance).

## What to hunt

| Problem | Confidence when proven |
|---|---|
| The fix patches the path the request named while the defect lives upstream, in a function other callers still reach unfixed | 90 |
| The repository already has a helper, pattern or library that does this, and the change builds a second one | 90 |
| A much smaller change solves the same stated problem (a guard in the shared function instead of one per caller, a config instead of code) | 80 |
| The change works around a cause it could remove (retry over a race, catch over a null that should not arrive, sleep over an ordering problem) | 85 |
| Abstraction, option or extension point with a single use and no stated need | 80 |

## Rules

- Without "what the change is for", this lens has nothing to attack: return no
  findings and say so in `not_checked`.
- Every finding names the alternative concretely: the file, the existing helper
  or the smaller diff. "Could be simpler" with no alternative is not a finding.
- Show the evidence that the alternative works here: the other caller, the
  existing helper's signature, the reverted line the test ignores.
