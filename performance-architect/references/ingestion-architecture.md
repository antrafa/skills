# Architecture for High-Volume Ingestion

Each pattern here comes with **the number that justifies it** and **the cost
it brings**. A pattern adopted without the number is fashion; adopted
without the cost, it is debt.

## Index
- [The question that comes before everything](#the-question-that-comes-before-everything)
- [Pattern 1: separate ingestion from processing](#pattern-1-separate-ingestion-from-processing)
- [Pattern 2: attachment out of the database and out of memory](#pattern-2-attachment-out-of-the-database-and-out-of-memory)
- [Pattern 3: ingestion durability](#pattern-3-ingestion-durability)
- [Pattern 4: idempotency](#pattern-4-idempotency)
- [Pattern 5: backpressure and degradation](#pattern-5-backpressure-and-degradation)
- [Pattern 6: database sized for writes](#pattern-6-database-sized-for-writes)
- [Pattern 7: real horizontal scaling](#pattern-7-real-horizontal-scaling)
- [Anti-patterns to refuse](#anti-patterns-to-refuse)
- [Adoption order](#adoption-order)

## The question that comes before everything

**What exactly needs to be ready before responding to the client?**

Almost every "real-time" premise breaks down into two things with very
different costs:

- **Ingested and queryable** — the data exists, is durable and someone can
  find it. This is usually the real requirement when the justification is
  "an agency may request this data at any moment".
- **Processed** — the business rule ran, the data was classified, enriched,
  turned into another record (a traffic ticket, a charge, an alert).

If the real requirement is the first, the second can be asynchronous, and
that separation is usually the architecture change with the largest effect
and the lowest cost in an ingestion service. If the real requirement is the
second — someone acts within seconds on the processed result — then the
requirement is legitimate and the architecture has to pay for it; in that
case the path is asynchronous processing with low, monitored latency, not
synchronous processing.

Ask this question of the requirement's owner, do not infer it. And record
the answer as an ADR: it is the decision all the others depend on.

## Pattern 1: separate ingestion from processing

**Flow:** validate the minimum that keeps invalid data out → durably persist
the raw data → respond → process the business rule in a separate consumer.

**Justified when:** response time is tied to the slowest work on the path;
or processing has higher cost/variance than ingestion; or the ingestion peak
is much higher than the average and processing can be amortized over the day
(this is the case for traffic with a daytime peak: a consumer sized a bit
above the average builds a queue during the peak and drains it outside it —
the delay is on the order of the peak's duration, and has to fit the
processing SLO; example calculation in `volume-sizing.md`).

**Gains:** response time decoupled from the business rule; peak absorbed
without scaling everything; a processing failure neither loses the data nor
rejects the client; the business rule can be reprocessed.

**Costs:** two things to operate and monitor; processing latency becomes an
explicit SLO (with a lag alert); an intermediate state ("received, not
processed") now exists and has to be visible to whoever queries; reprocessing
has to be idempotent.

**Careful:** responding `202 Accepted` is only honest if the data is already
durable. Responding before persisting trades slowness for silent data loss —
which is worse, especially with zero tolerance for loss.

## Pattern 2: attachment out of the database and out of memory

**Flow:** the attachment is streamed directly to object storage (S3, MinIO,
compatible); the database record stores the key, the size and the hash.

**Justified when:** there is a binary attachment and relevant volume —
practically always. With millions of objects per day, a `BLOB` in a
relational database is unworkable (database backup, replication and cache
skyrocket), and `byte[]` in heap blows up at peak (see `diagnosis.md`,
layer 3).

**Gains:** constant heap regardless of attachment size; storage scales and is
priced by tier (hot/cold); database backup becomes viable again; attachment
retention becomes independent of record retention.

**Costs:** two systems to keep consistent — orphans happen (object without a
record, record without an object), and need a reconciliation routine;
storage becomes an availability dependency of ingestion.

**Variant worth asking about:** can the client send the attachment directly
to storage via a pre-signed URL, sending only the metadata to the
application? If so, attachment traffic stops passing through the application
— the largest possible gain in this pattern. It depends on the client —
embedded equipment or legacy integrations do not always support it —, so it
is a question, not a premise.

## Pattern 3: ingestion durability

Two options, and the choice depends on what already exists and on the
tolerance for loss:

**A) Direct write to the database, processing reads from there.** The record
enters with status `pending`; a worker queries and processes it. No new
component. Justified when the database handles the ingestion write rate with
headroom (do the math: hundreds of small-row writes/s are comfortable for a
well-sized relational database) and the team does not operate queues. Cost:
a polling query on the same database that receives the writes; needs a
proper index on the status and care with concurrency between workers
(`SELECT ... FOR UPDATE SKIP LOCKED` solves it).

**B) Durable queue/log (RabbitMQ, SQS, Kafka).** Ingestion publishes;
consumers process. Justified when the write rate threatens the database,
when there are several independent consumers of the same event, or when
history needs to be reprocessed. Cost: a new component to operate, monitor
and size; DLQ and retry policy to design; duplicate delivery as normal
behavior (see Pattern 4).

**Kafka specifically** is only justified by log retention and re-reading, or
by multiple independent consumers that need replay — not by throughput in
the range of hundreds of msg/s, which a simple queue handles effortlessly. If
the stated reason for Kafka is throughput, the number does not support the
choice.

## Pattern 4: idempotency

**Flow:** define the event's natural key (e.g.: source + timestamp +
business identifier), apply a unique constraint in the database, treat the
violation as success ("already recorded") instead of an error.

**Justified when:** there is an automated client that resends on timeout —
assume there is until proven otherwise. And always, if there is a queue:
duplicate delivery ("at least once") is the default behavior, not the
exception.

**Gains:** resends stop being a problem; safe retry; safe reprocessing.

**Costs:** requires agreement on what "the same event" is (not always
obvious — a timestamp with the wrong granularity breaks the key both ways);
one more unique index.

**What this actually protects against:** a duplicate record that turned into
a legal consequence — a doubled traffic ticket, a doubled charge. It is the
category of defect that costs more than any latency problem, and it is born
precisely under the load one is trying to fix.

## Pattern 5: backpressure and degradation

Decide **beforehand** what the system does when it cannot keep up:

- Consumer lagging, ingestion healthy → accept and accumulate, with alerts on
  queue depth and on the age of the oldest message. It needs a ceiling:
  unbounded accumulation becomes a full storage and then unavailability.
- Ingestion saturated → rejecting explicitly with `429`/`503` and
  `Retry-After` is better than accepting and losing. An automated client
  knows how to resend; accepted-and-discarded data nobody recovers.
- Storage unavailable → where does the data need to go? Failing the request
  and letting the client resend is a legitimate and simple answer, as long as
  the client actually resends.

What to **never** do: silently accept what cannot be processed. It is the
hardest failure mode to detect, because every dashboard stays green while the
data is lost.

## Pattern 6: database sized for writes

- **Partitioning by date** on the events table: keeps indexes at a usable
  size, makes retention purging a metadata operation (`DROP PARTITION`
  instead of a `DELETE` of millions of rows) and keeps time-window queries
  efficient. Cheap to decide before, expensive after — if the volume
  justifies partitioning at some point, the moment is now.
- **Indexes for the real queries**, not for every imaginable query: business
  identifier + time window usually covers the operational case. Each extra
  index is a cost on every insert.
- **Batch insert** in the consumer, when durability is already guaranteed
  beforehand. It changes the order of magnitude of the write. Do not use it
  in synchronous ingestion: waiting for the batch to fill is latency and a
  risk of loss.
- **Separate analytical reads from ingestion writes** (read replica) when
  there are heavy queries — a report scanning history cannot compete with
  ingestion writes.
- **Retention and archiving** defined together with the business and legal
  teams. Without a retention policy, the system has an expiration date.

## Pattern 7: real horizontal scaling

Scaling only works if the application has no local state and the bottleneck
is not shared. Check: no in-memory session, no cache with functional
meaning, no files on local disk, no scheduling that cannot tolerate running
on several instances (then it needs a lock or a dedicated instance).

Then: HPA on a metric that represents the work (RPS or queue depth; CPU
misleads in a service that waits on I/O), graceful shutdown draining what is
in flight, a PDB so a node maintenance does not take down too many replicas,
and an HPA ceiling the cluster can allocate.

**If throughput does not grow when adding replicas, the bottleneck is
shared** (database, storage, lock) — and adding replicas only spreads the
wait. Measure throughput per replica before scaling.

## Anti-patterns to refuse

Refuse in one line, with the number, and offer the proportional
alternative. No sermon. Rewriting in another language, Kafka,
microservices, NoSQL and serverless follow the single table in
`goals-and-methods.md` ("When a new technology is justified"); below, only
what is specific to ingestion.

| Proposal | Why refuse | Alternative |
|---|---|---|
| Cache to solve write slowness | cache solves repeated reads; the ingestion problem is writes | size the writes: batching, partitioning, the right index |
| Increase the connection pool | the pool is where the problem shows up, not where it is | find out what holds the connection (almost always I/O inside the transaction) |
| Increase the thread pool to "accept more" | accepting more than is processed turns slowness into widespread timeouts | explicit backpressure + horizontal scaling |
| GC tuning as the first action | GC is usually a symptom of excessive allocation (attachment in heap) | eliminate the allocation; only then tune GC, with the GC log in hand |

## Adoption order

Do not adopt everything. Order by gain/risk ratio, for a typical ingestion
service:

1. Take I/O out of the transaction (partial Pattern 2) — large gain, low
   risk, small change.
2. Stream attachments to object storage (Pattern 2) — solves heap and
   storage at once.
3. Idempotency by natural key (Pattern 4) — cheap, and prevents the most
   expensive class of defect.
4. Separate ingestion from processing (Pattern 1 + 3) — the largest
   architecture gain, and the one with the highest operational cost.
5. Partitioning and indexes (Pattern 6) — before the table grows.
6. Explicit backpressure (Pattern 5) and horizontal scaling (Pattern 7).

The first three are usually enough for an order of magnitude of headroom.
Only go further if the Phase 1 number demands it.
