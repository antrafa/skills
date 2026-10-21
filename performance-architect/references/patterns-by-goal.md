# Patterns by Goal

Patterns for the goals that are **not** high-volume ingestion — for that
one, use `ingestion-architecture.md`. Same format: each pattern comes with
**the number that justifies it** and **the cost it brings**. A pattern
adopted without the number is fashion; adopted without the cost, it is debt.

## Index
- [Read-heavy](#read-heavy)
- [Critical-path latency](#critical-path-latency)
- [Cost and right-sizing](#cost-and-right-sizing)
- [Batch and processing window](#batch-and-processing-window)
- [Resilience under load](#resilience-under-load)
- [Cross-cutting anti-patterns](#cross-cutting-anti-patterns)

## Read-heavy

The question that comes first: **how often does the data change, and how much
delay does the reader tolerate?** The answer defines cacheability — and data
that only changes at night is the biggest opportunity a read system can have.

Adoption order, by gain/risk:

1. **`EXPLAIN` of the heavy pages' queries** before anything else. A seq scan
   on a large table with a selective filter is a missing index; an existing
   index that is not used is an incompatible predicate (function on the
   column, different type, `LIKE '%x'`). Cost: each index costs on every
   write — justify it with the real query.
2. **ORM N+1.** A page that fires 200 queries of 1 ms takes 200 ms in round
   trips alone. Evidence: SQL log with count per request. Fix: fetch join,
   batched `IN`, or direct projection. Cost: low.
3. **Pagination** of what loads everything. Justified when the list grows
   without a ceiling; **not** justified when it is 200 rows by index (a read
   of ms) — rejecting pagination with that argument is a valid answer.
4. **Cache**, in layers, from cheapest to most expensive:
   - HTTP (`Cache-Control`, ETag, CDN) for an identical response to many
     users — the biggest gain per effort on a public portal;
   - application (local per replica, short TTL) for repeated reads with
     tolerable freshness;
   - distributed (Redis) only when the predictable hit ratio is high (> 80%)
     and the replicas need to share, or when the data is expensive to
     recompute.
   Costs: invalidation (the hard part); **stampede** on mass expiry
   (mitigate with TTL jitter and request coalescing); memory; one more
   component when it is distributed. Caching before the `EXPLAIN` hides the
   bad query until the first mass miss.
5. **Materialization / precomputation** through the load that already exists
   (nightly, per event): aggregated history, counters, denormalized views.
   Justified when the computation is expensive and the data changes at a
   known pace. Cost: derived data to keep consistent.
6. **Text search** with the right technique: trigram/GIN index for partial
   `LIKE` and person names; a search engine (Elasticsearch/OpenSearch) only
   when there is relevance, facets or volume the database does not index
   well — high operational cost, requires a number.
7. **Read replica** when heavy reads compete with writes on the same instance
   and this shows up in the write p95. Cost: replication lag (the reader may
   see stale data), license, one more instance.
8. **Horizontal scaling of the portal by RPS** for the event peak
   (publication, enrollment), with HPA on requests/s and not on CPU; and the
   **event peak is the design number**, not the daily average
   (`volume-sizing.md`, factor 20x+).

## Critical-path latency

Without a **per-step breakdown** you do not optimize latency — you optimize a
guess. First measure, always: a timer per step (distributed tracing if
available; a manual timer per external call if not).

| Pattern | Justified when | Cost |
|---|---|---|
| Take out of the synchronous path what is not mandatory before responding (notify, index, audit, compute derivatives) | the breakdown shows the largest share is work whose result the client does not wait for | intermediate state; async processing needs an SLO and idempotency |
| Parallelize independent calls | N serial calls to independent dependencies; latency = sum becomes latency = max | code complexity; thread pool/async; individual timeouts |
| Explicit timeout on every external client + circuit breaker | any network dependency on the path — a missing timeout is unavailability, not slowness | decide the fallback (fast error, partial response, cached data) |
| HTTP connection pool with keep-alive | client that opens a new socket per request (TCP/TLS handshake on every call; accumulated TIME_WAIT) | configuration; pool size sized by Little |
| Reduce payload / serialization | (de)serialization time relevant in the profile; response with fields the client discards | API contract |
| Warm-up and cold start | high latency on the first requests after deploy/scale-up (JIT, cold cache, empty pool) | readiness that only opens after warm-up; `minReplicas` |
| Index / execution plan | critical-path query with a bad plan in the `EXPLAIN` | cost on every write |

**Tail amplification** (`goals-and-methods.md`): with 10 dependencies in
series, each one's p99 becomes ~p90 of the total. Reducing the number of hops
on the critical path is usually worth more than speeding up each hop.

## Cost and right-sizing

Non-negotiable rule: **SLO measured before and after**. A cut without
latency and error measurement is a bet with production, and the bill for the
bet arrives as an incident.

Order, by safety:

1. **Baseline.** Current cost per service/environment (invoice, console) and
   current SLI (p95, errors). Without both, there is no way to prove the gain
   or to detect the degradation.
2. **`requests` vs real usage.** Collect `top pod` at several times including
   the peak (or 2 weeks of metrics, if available). `requests` above the
   **usage p95 + margin** is wasted reservation that keeps the scheduler from
   packing more pods per node. `requests` **below** the p95 is the trap: the
   pod competes for unreserved CPU, and memory below usage becomes eviction.
   Typical gain: density per node, which turns into one node fewer.
3. **`limits` and runtime.** JVM heap (or equivalent) consistent with
   `limits.memory`, with headroom for metaspace/stacks/buffers. Low
   `limits.cpu` saves zero and causes throttling — in general it is better not
   to limit CPU and to limit memory.
4. **Idle replicas.** A service with 3 replicas at 5% each, with no peak that
   justifies it, can have `minReplicas: 2` (never 1 in production: N+1). An
   HPA with a high `min` "just to be safe" is a permanent cost for an
   unmeasured fear.
5. **Non-production environments** running 24 h × 7: shutting them down
   outside working hours is often the largest saving with the lowest risk.
6. **Storage, logs and metrics.** DEBUG log retention, high-cardinality
   metrics, orphan volumes, old snapshots. Cheap to cut, zero functional
   risk.
7. **Purchasing**: reserved instances / savings plan for the constant base;
   spot for interruption-tolerant batch. A financial decision — take the
   number to whoever decides.

Hidden cost of right-sizing: the time of whoever does it and the continuous
measurement afterwards. Record in the plan the metric that **reverts** the
cut (p95 went up, throttling appeared, `OOMKilled`).

## Batch and processing window

Start with the math: `required records/s = volume ÷ seconds in the window`,
with next year's volume. Then measure what the job does today: current
records/s, and **where the time is spent** (read, transform, write, wait).

| Pattern | Justified when | Cost |
|---|---|---|
| Parallelism **by partition** (date, customer, ID range) | serial job that does not reach the required records/s and the data is partitionable without dependencies between partitions | coordination; guarantee two workers do not take the same partition |
| Batched writes (batch insert/update) and commit per batch | row-by-row writes with commit per row — changes the order of magnitude | batch too large = long transaction, locks and expensive rollback; find the size by measurement (hundreds to a few thousand) |
| Read by cursor/streaming, not `findAll()` in memory | job that loads the whole table into heap | code |
| Indexes for the job's read | `EXPLAIN` of the job's query with the real volume shows a full scan | cost on every OLTP write; consider a temporary index or partition |
| Checkpoint and idempotent restart | a job that, failing at hour 5, starts over from zero | control table; write idempotency |
| Separate from OLTP (read replica, window, instance) | job competing with the day's traffic (visible in the OLTP p95 during the job) | infrastructure |
| Disable constraints/indexes during a bulk load | initial load or full reprocessing, never the daily job | risk of invalid data; window |

**Not** justified: Kafka, microservices or a rewrite because of a slow job.
In 9 out of 10 cases it is commit per row, `findAll()` or a bad `EXPLAIN`.

## Resilience under load

Decide **beforehand** what the system does when it cannot keep up. The
acceptable failure mode is to reject explicitly; the unacceptable one is to
accept and lose.

| Pattern | What it prevents | Cost |
|---|---|---|
| Timeout on **every** external client (connect and read) | thread stuck forever; ingestion that "stops accepting" with no error | choose the value: lower than the timeout of whoever calls you |
| Explicit backpressure (`429`/`503` + `Retry-After`; bounded queue; `RejectedExecutionHandler` that rejects or runs in the caller) | in-memory queue growing until `OOMKilled`; accepting what cannot be processed | the client needs to handle rejection (automated clients usually resend) |
| Bulkhead (separate pools per dependency/function) | a slow webhook exhausting the pool ingestion uses | more pools to size |
| Retry with exponential backoff, jitter and a **budget** | a retry storm taking down the dependency that just came back | complexity; retry only on transient errors and only with idempotency |
| Circuit breaker + defined fallback | waiting the whole timeout on a dependency already known to be down | decide the fallback |
| Correct readiness/liveness/startup probes | traffic before the application is up; an aggressive probe killing a healthy pod under load | liveness with a loose `failureThreshold`; startup probe for slow JVMs |
| Graceful shutdown + `terminationGracePeriodSeconds` ≥ drain time | rolling update dropping in-flight requests and in-memory queues | nothing relevant |
| `PodDisruptionBudget` | node maintenance taking down all replicas | nothing relevant |
| Memory: `limits` with headroom above heap + per-request allocation × concurrency | `OOMKilled` at peak | may require fewer replicas per node |
| DLQ and alert on queue depth/age | a poison message blocking the consumer; silent accumulation | operation and monitoring |
| Graceful degradation (respond with the essential, defer the rest) | all or nothing under overload | decide what is essential with the business |

**Never:** silently accept what cannot be processed. Every dashboard stays
green while the data is lost.

## Cross-cutting anti-patterns

Refuse in one line, with the number, and offer the alternative. No sermon.
New technology (another language, Kafka, NoSQL…) follows the single table in
`goals-and-methods.md` ("When a new technology is justified").

| Proposal | Why refuse | Alternative |
|---|---|---|
| Cache before the `EXPLAIN` | hides the bad query until the first mass miss (deploy, expiry, restart) | `EXPLAIN` and index first; cache afterwards, if the number calls for it |
| Replicas before measuring a shared bottleneck | if throughput does not grow with replicas, replicas only spread the wait | measure throughput with 1, 2, 4 replicas |
| Cut `requests` below real usage | saves nothing; becomes throttling and eviction | `requests` = usage p95 + margin; density per node |
| Increase `limits.memory` as the OOM fix | allocation scales with concurrency; there is always a bigger burst | eliminate the allocation (streaming, pagination, queue ceiling) |
| Optimize code without a breakdown | optimizes the function that accounts for 3% of the time | per-step timer first |
| "Real time" without breaking it down | sizes everything for the burst, when only the "queryable" part needed to be fast | separate queryable from processed (`ingestion-architecture.md`) |
| Cut cost without an SLO | the cut becomes an incident and nobody can prove it saved anything | cost and SLI baseline first; rollback metric in the plan |
