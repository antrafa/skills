# Lens: Correctness

Does the change do what it claims, in every path it can take, including the ones
nobody tested?

**Not yours:** project conventions (Conformance), exploitable flaws (Security),
where state lives and how to roll back (State and rollback), test quality (Tests),
module boundaries (Architecture), whether the criteria were met (Acceptance).

## What to hunt

| Problem | Confidence when proven |
|---|---|
| Inverted condition, off-by-one, wrong operator, wrong variable | 90 |
| Null, empty or missing value reaching code that assumes it is there | 85 |
| Error swallowed: empty `catch`, `\|\| true`, ignored exit code, result discarded | 90 |
| Resource opened without a guaranteed close (connection, file, stream, lock) | 85 |
| Shared mutable state reached by concurrent requests (singleton field, global, cache without a lock) | 90 |
| Locks taken in different orders on two paths | 85 |
| Slow I/O inside an open transaction | 80 |
| Query or remote call inside a loop over a collection that grows (N+1) | 85 |
| Unbounded query or list with no limit or pagination | 80 |
| Retry of an operation that is not idempotent | 85 |
| Write that should be atomic spread over steps with no transaction | 85 |
| A changed signature, field or enum with a caller that was not updated | 90 |

## Scripts and pipelines

Shell and CI code breaks in its own ways:

| Problem | Confidence when proven |
|---|---|
| Script without `set -e` (or equivalent) where a failed step must stop the rest | 85 |
| Unquoted variable that can hold a space or be empty (`rm -rf $DIR/`) | 90 |
| Command that behaves differently on the target OS (GNU vs BSD `sed`, `readlink -f`) | 75 |
| Path or host hardcoded that differs between environments | 85 |
| Step whose failure is hidden by a pipe without `pipefail` | 80 |

## Rules

- Trace the path first: a Critical names the input, state or sequence that
  reaches the line and what goes wrong then. With no path shown, it is a Note.
- A caller not updated counts only after you searched for callers (`grep`) and
  found one.
- Style and naming are not correctness. Leave them out.
