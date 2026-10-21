# Analysis inputs

Only the **goal** is mandatory. Everything else is optional and skippable: the
user rarely has everything at hand, and an analysis with half the data and the
gaps declared is worth more than an analysis stuck waiting for data that will
not arrive. When an input is missing, the conclusion that depended on it goes
into the report as an **unverified hypothesis**, together with the measurement
that would resolve it.

Present this table to the user in their language.

| Input | What it is for | How the user provides it | If missing |
|---|---|---|---|
| **Goal** (type + number + deadline) | Defines what "good" is. Without it there is no analysis, only opinion | "Handle 6M/day with p95 < 300 ms by March" / "cut 30% of the cost keeping the SLO" | Ask. It is the only question that blocks |
| Scope | Which services are in, which are out; what is an external dependency | Service/repo names, a diagram, or "it's this repo here" | Assume the indicated repo and declare the cut |
| Repositories | Critical path end to end, transaction, pools, HTTP clients, DDL | Repository path | The analysis has no code root cause; only symptoms |
| Manifests / Helm / compose | Replicas, `requests`/`limits`, HPA, probes, JVM flags, shutdown | Path or paste | Sizing becomes a hypothesis |
| Cluster (read-only) | Real vs declared usage, restarts, OOM, throttling, events, nodes | kubeconfig + namespace (see `cluster-collection.md`) | No real usage; declare it |
| Metrics / APM / dashboards | p95/p99 per endpoint, pool saturation, GC, errors, real RPS | Paste, export, or grant read access | Peak factor becomes a table assumption; no latency breakdown |
| Logs (peak window, 24 h) | Current volume per hour, bursts, real production errors, restarts | File or `kubectl logs` within the allow-list | Current volume becomes declared, not measured |
| Database | DDL, table sizes, `EXPLAIN` of the critical path, top queries, PK type, indexes, partitions | Paste or point to the migration files | The database becomes a black box in the bottleneck table |
| Business volume | Volume today and at target, distribution over the day, attachments, retention | Numbers, even approximate | Defaults from `volume-sizing.md`, marked as assumptions |
| Constraints | Budget, deadline, vetoed or mandatory technologies, contracts with customers/vendors, maintenance windows, licenses | Free text | The proposal may suggest what cannot be done; ask if you suspect it |
| Report audience | Who reads the technical one, who reads the managerial one, what decision each makes | "Dev team + coordination and board" | Assume technical team + non-technical manager |

This list goes to the user **in a single message**, in Phase 0.
