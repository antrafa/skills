# Performance Diagnosis by Layer

This file covers where to look for **performance under load**, layer by
layer. The code examples are Spring Boot because it is the most common case
on this team; the final section maps the same points to other stacks. For
the cluster access flow and the collection commands, use
`cluster-collection.md`; for the methods (USE, RED, utilization knee),
`goals-and-methods.md`.

## Index
- [Investigation order](#investigation-order)
- [Symptom → likely cause → evidence](#symptom--likely-cause--evidence)
- [Layer 1: the request's critical path](#layer-1-the-requests-critical-path)
- [Layer 2: transaction and connection pool](#layer-2-transaction-and-connection-pool)
- [Layer 3: memory and GC](#layer-3-memory-and-gc)
- [Layer 4: database](#layer-4-database)
- [Layer 5: cluster and scaling](#layer-5-cluster-and-scaling)
- [Idempotency: the bug that only shows up under load](#idempotency-the-bug-that-only-shows-up-under-load)
- [By stack: where the same problems show up](#by-stack-where-the-same-problems-show-up)
- [What to ask for when there are no metrics at all](#what-to-ask-for-when-there-are-no-metrics-at-all)

## Investigation order

Always from the outside in, because the bottleneck has to be somewhere and
saturation points to where:

1. What saturates first at peak — CPU, memory, connection pool, thread
   pool, I/O, network, or nothing (and then the bottleneck is an external
   wait)?
2. Which step of the request consumes the time — this needs a per-step
   breakdown, not total time.
3. Only then, the code of that step.

Jumping from the symptom straight to the code is the most common mistake: it
leads to optimizing a function that accounts for 3% of the time while 70% is
spent waiting on I/O.

**Saturation in nothing** is the most misdiagnosed case: if no local
resource saturates and latency rises, the bottleneck is a queue on an
external wait (database, storage, third-party service) or serialization on a
lock. Do not add replicas — measure the wait.

## Symptom → likely cause → evidence

| Symptom | Likely cause | Evidence that confirms |
|---|---|---|
| Latency rises at peak, CPU low | I/O wait or exhausted pool | pool saturation, connection wait time, latency breakdown |
| Connection pool exhausted, database CPU low | connection held by work that is not database work (upload, HTTP call inside the transaction) | mean connection usage time vs query time; `@Transactional` on the method that does I/O |
| Latency proportional to attachment size | attachment read whole into memory before writing | latency × size correlation, heap spikes, GC log |
| `OutOfMemoryError` only at peak | payload/attachment accumulation in heap × concurrency | heap dump, GC log, `-XX:+HeapDumpOnOutOfMemoryError` |
| Periodic pauses of hundreds of ms | recurring full GC from allocation pressure | GC log (`-Xlog:gc*`), pause time per minute |
| Client timeout, server with no error | unnecessary synchronous work in the request path | per-step breakdown; compare time of what is mandatory vs total |
| Throughput does not grow when adding replicas | shared bottleneck (database, storage, lock) or state in the application | throughput per replica falling as replicas increase |
| One specific query degrades with volume | missing index, or index not used by the predicate | `EXPLAIN` / `EXPLAIN ANALYZE` |
| Many small queries per request | ORM N+1 | SQL log with count per request |
| Duplicate record under load | client resend on timeout without idempotency | duplicate count per natural key, client log |
| Pod restarting at peak | memory limit below real usage under load | `describe` (exit 137, `OOMKilled`), `top pod` |
| Latency with steps in multiples of 100 ms | CPU throttling from low `limits` | `container_cpu_cfs_throttled_seconds_total`, `limits` vs usage |
| Success response, data does not show up later | response sent before durability (async work in memory, queue without confirm) | read the handler: what happens between the `return` and the commit; what does a restart discard? |
| Infrastructure error returned as `4xx` | automated client reads "do not resend" and the data is lost | exception mapping in the controller; `4xx` log correlated with dependency failure |
| Job finishes outside the window | commit per row, `findAll()` in memory, no per-partition parallelism | current vs required records/s; where the time goes (read/write/wait) |
| Throughput does not grow with replicas even with the database idle | serialization on a control row (per-table ID generator, counter, application lock) | trace of one INSERT; who does `SELECT … FOR UPDATE` on every write |

## Layer 1: the request's critical path

Read the handler end to end and classify **each** operation into one of
three boxes:

- **Mandatory before responding** — without it the response is a lie.
  E.g.: durably persisting the data that cannot be lost.
- **Necessary, but not before responding** — can be asynchronous. E.g.:
  classifying, calculating, notifying, indexing, generating derivatives.
- **Unnecessary** — can be skipped. E.g.: a query whose result nobody uses,
  repeated validation, serializing a response the client discards.

The minimum achievable response time is the sum of the first box. Everything
in it that should not be there is the biggest gain opportunity in an
ingestion service — and it is an architecture gain, not a
micro-optimization.

Where to look in a Spring Boot app:

- The controller and the service on the ingestion path.
- How the attachment is received: `MultipartFile.getBytes()` / `byte[]` /
  base64 `String` load the whole file into heap. `getInputStream()` streaming
  to the destination does not.
- Synchronous network calls (`RestTemplate`, `WebClient.block()`, Feign) on
  the path: each one adds its latency and its timeout to the total.
- `@Transactional` — where it really starts and where it really ends.
- Work that runs "for free": listeners, interceptors, auditing, aspects,
  heavy serialization/validation, logging the whole payload.
- Explicit timeout on every external client. Missing timeouts in an
  ingestion service under peak is not slowness, it is unavailability: the
  threads get stuck and the service stops accepting traffic.

## Layer 2: transaction and connection pool

The rule that solves most cases: **no network call, no upload and no
external wait inside the transactional boundary.** The database connection
is the scarcest and most expensive resource on the path, and it is held for
the whole transaction, not for the duration of the queries.

See the calculation in `volume-sizing.md` ("Sizing threads and
connections"): the same throughput requires 3.5 or 210 connections depending
only on what is inside the transaction.

What to check:

- `@Transactional` on a method that also writes an attachment, calls an API
  or publishes to a queue → the connection pays for all of that.
- `@Transactional` on the whole class or on a method far up the stack,
  wrapping much more than needs to be atomic.
- Hikari metrics: `hikaricp_connections_pending`,
  `hikaricp_connections_acquire_seconds`, `hikaricp_connections_usage_seconds`.
  Waiting for connections with low database CPU is the signature of improper
  retention.
- `maximumPoolSize` larger than the database supports: moves the queue into
  the database, where it is harder to see.
- Server thread pool (`server.tomcat.threads.max`) misaligned with the
  calculated concurrency — too small queues before entering, too large lets
  the application accept more than it can process and turns slowness into
  widespread timeouts.

## Layer 3: memory and GC

In an ingestion application with attachments, memory scales with
`attachment size × concurrency`, and that is what blows up at peak — not in
the local test with one request.

- Attachment in heap: 3 images of 200 KB × 84 in-flight requests ≈ 50 MB in
  buffers alone, and that is the best case (no intermediate copy). Base64 in
  transit increases the payload by ~33% and usually doubles the allocation
  because of the conversion.
- Ask for: GC log (`-Xlog:gc*:file=...`), pause time per minute, heap after
  full GC (the number that tells whether there is a leak or only allocation
  pressure).
- Heap after full GC stable and high = legitimate work, needs more memory or
  less allocation. Growing over time = leak.
- The container's `limits.memory` needs headroom above the heap (metaspace,
  thread stacks, direct buffers, native code). Heap equal to the limit is an
  `OOMKilled` waiting for the peak.

## Layer 4: database

On the ingestion path, writes dominate. What to check:

- `EXPLAIN` of the critical-path queries — including the validation ones
  ("does this passage already exist?"), which are easy to forget and run on
  every request.
- Indexes that serve the write and the operational query (typically business
  identifier + time window), without overdoing it: each extra index is a
  cost on every insert.
- One-by-one vs batch insert. In high-volume ingestion, batching changes the
  order of magnitude — but it requires durability to be guaranteed first
  (see `ingestion-architecture.md`).
- Table growth and partitioning by date — a decision that is cheap before
  and very expensive after.
- Attachment in a database column (`BLOB`/`bytea`): unworkable at this
  volume. Backup, replication and database cache costs skyrocket.
- Ingestion writes competing with analytical reads on the same instance.
- Every proposal for a new index or schema change on a large table says how
  to apply it without stopping the system: creating an index locks writes on
  the table, unless done online (`CREATE INDEX CONCURRENTLY` in PostgreSQL,
  `ONLINE = ON` in SQL Server, `ONLINE` in Oracle); a new column with a
  populated value needs a batched backfill, not a single `UPDATE`. And it
  says how to undo it.

## Layer 5: cluster and scaling

- Replicas and `requests` consistent with the Phase 1 sizing.
- Low `limits.cpu` causes throttling that shows up as stepped latency, not
  as high CPU — it misleads the diagnosis.
- HPA: on which metric? CPU does not represent a service that waits on I/O
  well; RPS or queue depth do.
- Horizontal scaling requires an application without local state: session,
  in-memory cache with meaning and files on local disk break scaling.
- `terminationGracePeriodSeconds` and graceful shutdown: without them, every
  rolling update drops in-flight requests — at hundreds of req/s, a deploy
  becomes an incident.
- HPA ceiling that the cluster can actually allocate.

## Idempotency: the bug that only shows up under load

An automated client that hits a timeout **resends**. Under peak, timeouts
stop being rare. Without an idempotency key, the resend creates a duplicate
record — and when the record has legal consequences (a traffic ticket, a
charge), the duplicate is a much bigger problem than the slowness that
caused it.

What to check: is there a unique natural key (e.g.: source + timestamp +
business identifier) with a constraint in the database? Does resending the
same request produce the same result, or a second record? The asynchronous
processing, if it exists, is also idempotent — duplicate delivery is normal
queue behavior, not an anomaly.

## By stack: where the same problems show up

The problems are the same — held connection, allocation × concurrency,
unnecessary synchronous work, missing timeouts. Where to look changes.

| Stack | Connection / thread pool | Memory | Concurrency: what locks everything | What to ask for |
|---|---|---|---|---|
| **JVM** (Spring, Quarkus) | Hikari (`connections_pending`, `acquire_seconds`), `server.tomcat.threads.max` | heap vs `limits.memory` (metaspace, stacks, direct buffers sit outside); attachment `getBytes()` | `@Transactional` wrapping I/O; `synchronized` on a singleton; `parallelStream` on the common pool | GC log (`-Xlog:gc*`), heap dump on OOM, Actuator/Micrometer |
| **Node.js** | `pg`/`mysql2` pool per process; **one** process = one event thread | V8 heap (`--max-old-space-size`) vs `limits`; upload buffers in memory | any CPU-bound work (large JSON, crypto, compression) blocks the whole event loop — latency of everything rises together | event loop lag, `--heapsnapshot`; run in cluster/PM2 or 1 process per pod with more replicas |
| **.NET** | `SqlConnection` pool per connection string; ThreadPool | server vs workstation GC; `LOH` with large arrays | **sync-over-async** (`.Result`, `.Wait()`) exhausting the ThreadPool — thread pool starvation shows up as latency with low CPU | `dotnet-counters` (threadpool queue length, GC), `dotnet-trace` |
| **Python** (Django, FastAPI) | pool per **worker**: `workers × pool_size` connections to the database; gunicorn/uvicorn workers × threads | RSS per worker × workers vs `limits` | GIL: CPU-bound work serializes per process; synchronous I/O in an async handler blocks the loop | `workers` consistent with CPU; `EXPLAIN`; profile with `py-spy` |
| **Go** | `database/sql` `SetMaxOpenConns` (default unlimited!); cheap goroutines | `GOMEMLIMIT`; `GOMAXPROCS` ≠ cgroup limit without `automaxprocs` (throttling) | goroutine leak (waiting on a channel that never closes); global `sync.Mutex` | `pprof` (CPU, heap, goroutines), `runtime/metrics` |

In all of them: explicit timeout on every external client; a ceiling on
every in-memory queue; a readiness probe that only lets traffic in once
connections and caches are ready; graceful shutdown that drains what is in
flight.

## What to ask for when there are no metrics at all

A common scenario, and not a blocker. In this cost/benefit order:

1. **Actuator + Prometheus** already expose the essentials in Spring Boot:
   latency per endpoint, Hikari metrics, GC, threads. It is the smallest
   change with the largest information return.
2. **GC log** turned on — a file, no relevant cost in production.
3. **`EXPLAIN`** of the critical-path queries, which requires nothing in
   production.
4. **`kubectl top` and `describe`** for real usage vs requests and restart
   history — read-only, following `cluster-collection.md`.
5. **Single-instance load test** to find the capacity per replica — without
   that number, every replica calculation is a hypothesis.

Until this data exists, deliver the analysis with the conclusions marked as
hypotheses and the instrumentation as the first item of the plan. An honest
analysis with declared gaps is useful; an analysis that pretends to have
measured is not.
