# Lens: State and Rollback

If this change is applied to an environment, what happens to the data that is
already there, and how do we go back?

**Not yours:** script bugs (Correctness), exposed secrets and permissions
(Security), conventions (Conformance).

## Where state lives

For every stateful thing the diff touches (database, volume, queue, cache,
bucket, certificate, session, uploaded files), answer: where is the data
physically, and does it survive what this change does? A named volume, a bind
mount, the node's local disk and "only inside the container" give four different
answers to "recreate it".

## What to hunt

| Problem | Confidence when proven |
|---|---|
| Change that recreates or moves a stateful workload whose data is not in durable storage (container filesystem, `emptyDir`, local disk of one node) | 95 |
| Destructive operation with no backup step before it: drop, truncate, delete, `down -v`, `helm uninstall`, volume or PVC removal | 95 |
| Migration with no way down, or one that changes data a rollback cannot restore | 90 |
| Field renamed or removed in the same release that stops writing it (old and new versions cannot run side by side) | 85 |
| Storage class, access mode, size or claim name changed on an existing volume | 90 |
| Image by `latest` or a mutable tag, so a rollback does not bring the old version back | 85 |
| Value meant for one environment applied to all of them (shared values file, default overlay) | 90 |
| Script that is not safe to run twice (creates without checking, appends without dedup) | 85 |
| Deploy with no readiness check, so traffic reaches a pod that is not ready | 80 |
| Resource limits removed, or memory limit below what the process is configured to use (JVM heap, worker count) | 80 |

## For each Critical, state the way back

The `fix` field says: what the rollback is, how long it takes, and what does not
come back (data deleted, migration without down, certificate revoked). "There is
no way back" is the most important thing this lens can report; say it plainly.

## Rules

- Read the whole manifest or chart, not just the hunk: the volume that matters
  is often declared far from the line that changed.
- Which environments does this reach? A change in a shared base or default
  values reaches every environment; name them if the repository shows them.
