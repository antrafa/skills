# Goals and Methods

The skill's workflow is the same for any goal. What changes is how the
target is written, what usually decides the case and the typical trap. This
file covers that and the standard industry methods that back the analysis.

## Contents
- [The six goal types](#the-six-goal-types)
- [Combined goals](#combined-goals)
- [Measuring the current state when there are no metrics](#measuring-the-current-state-when-there-are-no-metrics)
- [Standard methods](#standard-methods)
  - USE · RED · Little's Law · Utilization knee · Universal Scalability Law · Percentiles · Load tests · Headroom · SLO
- [When a new technology is justified](#when-a-new-technology-is-justified)

## The six goal types

### 1. Scale to volume X

- **Target:** design peak req/s, acceptable p95, loss tolerance,
  "queryable" window. E.g.: "400 req/s peak, p95 < 300 ms, zero loss".
- **What decides:** what saturates first at peak; what sits inside the
  transaction boundary; storage accumulated over retention; whether the
  bottleneck is shared across replicas (database, storage, lock, ID
  generator).
- **Trap:** sizing by the average, or treating daily volume as
  instantaneous load. And confusing the hourly peak with a burst (see
  `volume-sizing.md`).
- **Patterns:** `ingestion-architecture.md` for writes; `patterns-by-goal.md`
  for reads.

### 2. Reduce latency

- **Target:** p95 (and p99, if there is a tail SLO) per endpoint or per
  journey, in ms, **at a declared volume** — latency without volume is not
  a target.
- **What decides:** per-step breakdown (without it, you optimize what
  accounts for 3% of the time); synchronous work that could be out of the
  response; serial calls that could run in parallel; N+1; external waits
  without a timeout; serialization/deserialization of a large payload.
- **Trap:** optimizing code before having the breakdown. And looking at the
  average: a great p50 with a bad p99 is the most common case, and the user
  feels the p99.
- **Patterns:** `patterns-by-goal.md` § Critical-path latency.

### 3. Reduce cost / right-sizing

- **Target:** money or resources (vCPU, GiB, nodes) per month, **with the
  SLO kept** — write the SLO next to the cost target, or the cut will be
  billed as an incident three weeks later.
- **What decides:** `requests` vs real p95 usage (not the average);
  replicas with low, flat utilization; misaligned heap/`limits`; HPA with
  `min` set too high; storage and log/metric retention; non-production
  environments running 24 h; reserved vs on-demand instances.
- **Trap:** cutting `requests` below the p95 of usage — it saves nothing,
  it trades cost for throttling/OOM. Cutting a replica in a service that
  already lacks N+1. And measuring "before" only at the calmest hour of the
  day.
- **Patterns:** `patterns-by-goal.md` § Cost and right-sizing.

### 4. Stability under load

- **Target:** zero `OOMKilled`/restarts at peak; error rate < x%; no client
  timeout while the server looks "healthy"; deploys without errors.
- **What decides:** memory = allocation per request × concurrency (it blows
  up at peak, not in the local test); missing timeouts on external clients;
  in-memory pools and queues without a ceiling; missing or aggressive
  probes; non-graceful shutdown; retry without jitter taking the dependency
  down.
- **Trap:** raising the memory limit as the fix — it treats the symptom;
  allocation scales with concurrency and there is always a bigger burst.
- **Patterns:** `patterns-by-goal.md` § Resilience under load.

### 5. Batch / job window

- **Target:** "finish before 6 a.m." becomes `records/s needed = volume ÷
  seconds in the window`, with headroom for next year's volume.
- **What decides:** whether the job can be parallelized by partition (date,
  customer, ID range); batch size and commit frequency; indexes that serve
  the job's reads and hurt its writes; competition with OLTP on the same
  instance; whether it is restartable (idempotent checkpoint).
- **Trap:** parallelizing without partitioning (every worker fighting over
  the same rows), and "optimizing the query" without an `EXPLAIN` of the
  plan at real volume.
- **Patterns:** `patterns-by-goal.md` § Batch and processing window.

### 6. Read-heavy

- **Target:** p95 of the page or query **at the access peak** (publication,
  enrollment opening, month-end close), not the daily average.
- **What decides:** `EXPLAIN` of the heavy pages' queries; how often the
  data changes (defines cacheability); pagination of what loads everything
  today; N+1; read replica; text search with the right index.
- **Trap:** applying ingestion patterns (queue, asynchronous processing,
  idempotency) to a system nobody writes to. And caching before the
  `EXPLAIN`: the cache hides the bad query until the first mass miss.
- **Patterns:** `patterns-by-goal.md` § Read-heavy.

## Combined goals

"Scale 10x without raising cost more than 2x", "reduce latency without
touching the database", "cut cost without touching code". There is always a
**primary** — the one that defines the verdict (holds / does not hold /
reached / not reached) — and **constraints**, which every proposal must
respect and which show up in the cost table and in the ADRs as a discarded
alternative ("discarded because it violates constraint X").

State explicitly which is which. When the user does not know, propose one:
the primary is what hurts today; the rest are constraints.

## Measuring the current state when there are no metrics

A common, non-blocking scenario. Current volume can almost always be
measured with what already exists, and **measured volume is worth more than
declared volume**:

| Source | What it gives | How |
|---|---|---|
| Application log (1 line per event) | volume per hour, busiest hour, per-second burst | count lines per hour (`cut` on the timestamp + `sort \| uniq -c`); for bursts, count per second in the busiest minute |
| Gateway / ingress / Istio access log | real RPS per endpoint, status, latency | same procedure; usually has per-request latency |
| Database | historical volume per day/hour, table sizes, growth | `COUNT(*) GROUP BY` creation date; catalog views for size |
| Broker (RabbitMQ, SQS, Kafka) | publish and consume rate, queue depth, age of the oldest message | management console/API; it is the best source for the consumer |
| `kubectl top` / `describe` | real CPU and memory usage, restarts and their reason | see `cluster-collection.md`; collect at peak |
| Cloud bill / console | current cost per service, per environment | mandatory baseline for a cost goal |

Record in the evidence inventory how the number was obtained (command, time
window) and what was missing in the window (hours without logs, an atypical
day). Interpolating missing hours is acceptable if declared as an
assumption.

## Standard methods

### USE — per resource

For **each resource** on the path (CPU, memory, database connection pool,
thread pool, disk/IO, network, queue, external storage), answer three
questions: **U**tilization (how much is in use), **S**aturation (how much
is waiting in the resource's queue), **E**rrors. A resource can be at 40%
utilization and saturated (a queue waiting for connections while the
database CPU is low is the classic example). The symptom → cause table in
`diagnosis.md` is USE applied.

### RED — per service

For **each service**: **R**ate (req/s), **E**rrors (error rate),
**D**uration (latency in percentiles). They are the minimum "golden
signals"; without them no SLO is possible. When they do not exist, the
first item of the plan is to expose them (Actuator/Prometheus,
OpenTelemetry, or the stack's equivalent).

### Little's Law

```
concurrency = throughput × residence time
```

It holds for in-flight requests, held connections, messages being
processed. It is what turns req/s into threads, connections and replicas.
Details and an example in `volume-sizing.md`.

### Utilization knee

On a shared resource with random arrivals, queue wait time grows roughly
with `utilization / (1 − utilization)`, in multiples of the service time.
At 50% utilization the wait equals the service time; at 80% it is 4x; at
90% it is 9x. **Above ~70–80% sustained utilization, latency stops being
predictable.** Consequences:

- "CPU at 85% is great, 15% left over" is wrong for latency — capacity is
  left over, predictability is not.
- Size shared resources (database, pool, storage) to stay below the knee at
  peak, not at 100%.
- A connection pool larger than the database's capacity only moves the
  queue inside the database, where it is more expensive to see.

### Universal Scalability Law (why replicas stop helping)

Throughput does not grow linearly with replicas for two reasons:
**contention** (the serial part: lock, ID control row, shared table, single
storage) and **coherence** (the cost of keeping state consistent across
instances: distributed cache, replicated session). Past a certain point, an
extra replica **reduces** throughput.

Practical diagnosis: measure throughput with 1, 2 and 4 replicas. If it
does not double when replicas double, the bottleneck is shared — and it
lives outside the application. Adding replicas only spreads the wait. This
is the measurement that decides between "scale" and "remove the
contention".

### Percentiles, not averages

The average hides the tail, and the user feels the tail. Always p50, p95,
p99 — and the **rate** with them, because a p99 at 3 req/s means nothing.

**Tail amplification:** if a journey touches N services and each has 1% slow
responses, the probability of the journey being slow is `1 − 0.99^N`: with
10 calls, ~10%. In a fan-out, each dependency's p99 becomes the aggregate's
p90. It is the numeric argument against serial calls on the critical path.

### Load test types and what each one answers

| Test | Question it answers | When |
|---|---|---|
| Smoke | does the test environment work under minimal load? | before any other |
| **Load on 1 replica** | **capacity per replica** — the number without which the replica calculation is a guess | first real test |
| Load | at design volume, does the SLO hold? | validates the sizing |
| Stress | where does it break, and how (gracefully or losing data)? | finds the ceiling and the failure mode |
| Soak (endurance) | over hours at design volume, is there a leak, heap growth, degradation? | before going live in production |
| Spike | is the burst absorbed (queue/buffer) or does it knock things down? | when the burst factor is high |

The skill **does not run** load tests; it says which test is missing, what
it must measure, and puts it in the plan as an item. Recommend a tool only
if the team has none (k6, Gatling, JMeter, Locust are all adequate; the
choice is the team's).

### Headroom

- Size for **design peak × headroom**: 1.3–2x depending on loss tolerance
  (2x for ingestion that cannot lose data).
- **N+1** replicas: survive a rolling update and the loss of a node.
- An HPA ceiling the cluster can **actually allocate** (`Pending` does not
  scale).
- Shared resources below the utilization knee at peak.

### SLO: the target has to be one

The SLI is the measure (p95 latency of endpoint X). The SLO is the target on
that measure (p95 < 300 ms in 99% of the minutes of the month). Without an
SLO, "good performance" is opinion and "cut cost without degrading" cannot
be verified. When the user has no SLO, propose one from what the business
tolerates, mark it as an assumption and put measuring the SLI as the first
item of the plan.

## When a new technology is justified

Each technology comes with the **number that requires it** and the
**operational cost it brings**. Quick rules, with the proportional
alternative:

| Technology | The number that justifies it | If the number does not hold it up |
|---|---|---|
| Queue/broker (when there is none) | peak ≫ average and amortizable processing; producer and consumer with different load profiles; a processing failure must not reject the producer | a `pending` state in the database itself with `SKIP LOCKED` |
| Kafka specifically | replay of history or multiple independent consumers of the same event | a simple queue (RabbitMQ/SQS): hundreds or thousands of msg/s do not call for Kafka |
| Distributed cache | repeated reads of the same data with a predictable hit ratio > 80% and tolerable freshness; or state shared across replicas | a local cache per replica; or just the missing index |
| Read replica | heavy reads competing with writes on the same instance, visible in the write p95 | index + pagination + cache |
| Object storage | binary attachments at relevant volume (practically always) | — (it is the standard, not the exception) |
| Partitioning | a table that grows without a ceiling and retention-based purging | — (cheap before, very expensive after) |
| Another database (NoSQL) | a different data model or guarantee required by the case; **never** speed | partition and index the relational one |
| Another language | CPU-bound proven by a profile on the critical path, after I/O is eliminated | measure the breakdown; the bottleneck in a web service is I/O in 9 out of 10 cases, and the rewrite throws away business rules already validated without touching the cause |
| Microservices | genuinely distinct load profiles or deploy cycles | split only what has a different profile (typically ingestion vs processing) |
| Serverless | sporadic traffic with long idle periods | horizontal scaling with HPA |
