# Volume and Sizing

## Contents
- [Survey script](#survey-script)
- [Business volume → req/s](#business-volume--reqs)
- [Peak factor](#peak-factor)
- [Data volume and storage](#data-volume-and-storage)
- [Sizing threads and connections](#sizing-threads-and-connections)
- [When the goal is not volume](#when-the-goal-is-not-volume)
- [Replicas and headroom](#replicas-and-headroom)
- [Worked example: speed-camera ingestion](#worked-example-speed-camera-ingestion)

## Survey script

Every question can be skipped. When the user does not know, **assume a
default, declare the default in the report and mark it as an assumption** —
never stall the analysis waiting for a number nobody has. A marked
assumption can be revised; an invented, unlabeled number is debt.

| # | Question | Default if unknown |
|---|---|---|
| 1 | Total volume per day (today and at the target) | use the declared target, with no additional growth |
| 2 | How is the volume spread over 24h? | concentrated daytime peak: factor 6x over the average |
| 3 | Average payload size (without attachments) | 2 KB of JSON |
| 4 | Number and average size of attachments/images | assume the declared maximum; 200 KB per image |
| 5 | Legal retention of the data and of the attachment | 5 years for the record; question whether the attachment needs the same period |
| 6 | Acceptable response time on ingestion | 200 ms p95 |
| 7 | What happens if a request is lost? | zero tolerance (the most expensive case; if there is tolerance, it simplifies the architecture a lot) |
| 8 | What is the real "near real time" window? | seconds for the data to become queryable |
| 9 | Expected growth over 2 years | +30% |
| 10 | Does the client resend automatically on timeout? | yes — assume it does until proven otherwise (defines the need for idempotency) |

Questions 7 and 8 are the ones that change the architecture the most.
Question 10 is the one that causes the most production bugs when nobody
asks it.

## Business volume → req/s

```
average req/s = volume per day ÷ 86,400
```

This number serves one purpose only: giving the problem a scale. **Never
size by the average** — the system is not sized for the day, it is sized for
the worst hour of the day.

## Peak factor

```
design req/s = average req/s × peak factor
```

| Distribution | Factor | When to apply |
|---|---|---|
| Uniform over 24h | 1.5x | automated process with no human rhythm (batch, constant telemetry) |
| Business hours (8 working hours) | 3x | human use during office hours |
| Concentrated daytime peak | 6x | traffic that follows people's movement — road traffic, retail, customer service. Conservative: equals ~25% of the day's volume in the peak hour |
| Concentrated event | 20x+ | ticketing, enrollment, Black Friday |

Prefer the measured factor to the table's: if there is a requests-per-minute
metric, the real factor is `measured_peak ÷ measured_average`, and it is
worth more than any estimate. The table is for when there are no metrics —
and in that case the factor goes into the report as an assumption.

Size with headroom over the design peak (2x is reasonable for ingestion that
cannot lose data), because the peak of the peak gives no warning.

### Hourly peak ≠ burst

They are two different factors, and confusing them is off by an order of
magnitude:

```
hourly peak factor = busiest hour ÷ hourly average           (e.g.: 1.6x)
burst factor       = busiest second ÷ average of the hour    (e.g.: 30x)
```

The **hourly peak** is absorbed with replicas: it is sustained load. The
**burst** is absorbed with a queue or buffer: it lasts seconds, and CPU-based
scaling does not react in time. Automated clients (devices, integrations,
third-party jobs) tend to accumulate and dump in batches — a high burst with
a low hourly peak is the typical profile. Measure both when there is a log
with a per-event timestamp (`goals-and-methods.md`, "Measuring the current
state"); when volume scales, the burst does **not** scale linearly — more
sources fall out of sync and the aggregate smooths out. Model a floor
(Poisson: `mean + 3√mean`) and a ceiling (correlated bursts) and declare
which one you adopted as an assumption.

## Data volume and storage

```
objects/day   = req/day × attachments per request
storage/day   = objects/day × average attachment size
total storage = storage/day × retention days
```

Do this math **before** any discussion of code. In ingestion systems with
attachments (image, audio, document), storage is the item that decides the
project's viability long before any CPU bottleneck — and it is the only
number that grows even when the system is working perfectly.

If the result is large, the subject becomes **tiered retention**, not code
optimization: how long the attachment stays in immediate access, when it
moves to cold storage, when it is discarded. That is a legal and business
decision, not a technical one — take the number to whoever decides.

Add the database growth too: `req/day × row size × retention`, plus indexes
(estimate 30-50% over the data for a table with few indexes).

## Sizing threads and connections

Little's Law:

```
required concurrency = throughput (req/s) × response time (s)
```

E.g.: 700 req/s at 200 ms → 140 simultaneous in-flight requests. This is the
number the server thread pool must support in aggregate across all replicas.

For the **database connection pool**, what counts is not the total request
time, it is the time the connection is held:

```
required connections = throughput × time holding the connection
```

E.g.: 700 req/s holding a connection for 5 ms → 3.5 connections. The same
700 req/s holding a connection for 300 ms (because the transaction wraps the
attachment upload) → 210 connections, which no database delivers
comfortably. **It is the same throughput.** The only difference is what sits
inside the transaction — and that is why "increase the pool" is almost never
the right answer: the pool is where the problem shows up, not where it lives.

An oversized pool also costs: each connection consumes memory and
concurrency in the database. A pool larger than the database's real capacity
only moves the queue from inside the application to inside the database,
where it is more expensive to diagnose.

## When the goal is not volume

The same arithmetic works with a different input:

- **Batch:** `records/s needed = volume ÷ seconds in the window`, using next
  year's volume; compare with the records/s measured today.
- **Cost:** `cost per 1,000 requests = monthly cost ÷ (req/month ÷ 1,000)`
  — it is the number that compares alternatives and shows whether scaling is
  linear.
- **Latency:** a per-step budget — the target p95 split across the steps of
  the critical path, to know how much each dependency may consume.

Details per goal in `goals-and-methods.md`.

## Replicas and headroom

```
replicas = ceil(design req/s ÷ measured capacity per replica) + headroom
```

`measured capacity per replica` must come from a load test or a production
metric. Without that number, the replica calculation is a guess — declare it
as a hypothesis and say the pending measurement is a load test of a single
instance.

Headroom: at least +1 replica to survive a rolling update and the loss of a
node, and an HPA configured with a ceiling the cluster can actually allocate
(an HPA that asks for replicas that do not fit in the cluster does not scale,
it only piles up `Pending` pods).

## Worked example: speed-camera ingestion

Declared target: 6 million requests/day, payload + up to 3 images, daytime
peak distribution, data must become queryable within seconds.

```
average req/s    = 6,000,000 ÷ 86,400         ≈ 70 req/s
design req/s     = 70 × 6 (daytime peak)      ≈ 420 req/s
with 2x headroom                              ≈ 840 req/s for sizing

objects/day   = 6,000,000 × 3                 = 18,000,000 images/day
storage/day   = 18,000,000 × 200 KB           ≈ 3.4 TB/day
storage/year                                  ≈ 1.2 PB/year

concurrency at 200 ms = 420 × 0.2             ≈ 84 in-flight requests
connections, 5 ms transaction = 420 × 0.005   ≈ 2 connections
connections, 300 ms transaction = 420 × 0.3   ≈ 126 connections
```

Reading these numbers:

- **420 req/s is not a language problem.** A well-configured Spring Boot
  handles it with a few replicas. Whoever proposes a rewrite at this level
  is solving the wrong problem.
- **3.4 TB/day is the real problem.** It is the line that dominates the cost,
  and it is decided by retention — not by code.
- **The difference between 2 and 126 connections is only the content of the
  transaction.** This is the most likely bottleneck of an ingestion service
  with attachments, and it is solved by taking the I/O out of the
  transaction, not by growing the pool.
