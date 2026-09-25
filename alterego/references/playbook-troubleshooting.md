# Playbook: SRE Troubleshooting & Pragmatic Diagnosis

This playbook guides the investigation of incidents, slowness, stuck requests and anomalous behavior in services and containers. The runbook is written for the most common case in corporate legacy, a JVM in a Linux container (Kubernetes, Docker); for another runtime the steps are the same with the equivalent tool (the runtime's thread and heap dumps, cgroup metrics, database traffic). The user's stack is in the profile; use it to pick the commands.

---

## Non-negotiable principles

1. **Evidence before touching code:** tie observations to hypotheses and name the collection that can tell them apart. Declare a proven root cause when the evidence demonstrates the failure mechanism; isolated counters and samples can only steer the investigation.
2. **Stabilize before philosophizing:** in an active incident with production impacted, the initial focus is containing the damage and recovering the service in a controlled way, before doing an architectural autopsy.
3. **Before moving or recreating, find out where the state lives:** before restarting, recreating or migrating containers/services, make sure where the data is (named volume, bind mount, node local disk, database). Destroying data to fix a temporary hang is inadmissible.
4. **Know the rollback before applying:** every configuration change, script or patch must have its reversal procedure and estimated time declared before execution.
5. **Never claim it worked without verifying:** applying is not up; up is not answering successfully. Confirm the return metric before declaring it closed.

---

## Step 0: top-down triage before any dump

The runbook below is deep and costly to run. Going straight for a thread dump on
the first symptom is choosing the instrument before knowing the organ. Three
standard sweeps decide where to cut, and each one takes a couple of minutes with
the observability that already exists:

| Sweep | Subject | What to collect | What it answers |
|---|---|---|---|
| **USE** (Brendan Gregg) | every resource: CPU, memory, disk, network, connection and thread pools | **U**tilization, **S**aturation, **E**rrors | which resource is the constraint |
| **RED** (Tom Wilkie) | every service or endpoint on the request path | **R**ate, **E**rrors, **D**uration | which hop degraded, and whether it is volume or latency |
| **Four golden signals** (Google SRE) | the user-facing service | latency, traffic, errors, saturation | whether the user is being hurt right now |

- **Saturation is the cell everyone skips, and it is the one that predicts.** A
  queue that grows, a pool at its ceiling, a run queue above the core count, GC
  time as a fraction of wall clock. 100% utilization with no saturation is a
  resource being used well; saturation at 60% utilization means the limit is
  somewhere else.
- **USE covers resources, RED covers requests.** A symptom that shows up in RED
  and not in USE points outside the process: dependency, network, or the caller.
- Each cell carries value, unit, window and source. An empty cell is a **gap**,
  not a zero — and a gap that matters becomes the next collection.
- Enter the runbook only after this, and say which cell sent you there.

### Bound the problem by contrast (is / is-not)

Before listing hypotheses, bound the problem the way Kepner-Tregoe does — by
what it is **not**, when it could have been:

| | Is | Is not, but could be |
|---|---|---|
| **What** | `POST /orders` returns 502 | `GET /orders`, same service |
| **Where** | pods in `sa-east-1b` | the other two zones |
| **When** | since 14:10, in bursts | steady before the 14:00 deploy |
| **Extent** | 3 of 12 pods | the whole replica set |

Every difference in the right column prunes a family of causes: if only one zone
fails, a code bug explains nothing. Fill it with observation, never with
deduction — this table is what keeps the investigation from following the first
plausible story.

---

## Surgical investigation runbook (worked case: JVM in a container)

### 1. Live process and overall consumption
Identify environment, namespace, pod/container and PID before collecting. Run the process commands on the target host/container and record time, duration and origin of the samples. Check which tools and permissions are available.

- Does the process exist in the pod/host?
  ```bash
  pgrep -f java            # swap for the runtime process in question
  kubectl top pod <pod-name>
  ```
- What is the consumption profile? Compare CPU with the limit and the number of cores; record the unit and the window of the metric.
  - Sustained high CPU suggests heavy computation, a loop or GC; correlate with stacks and a CPU profile.
  - Low CPU with a stuck request suggests waiting on locks, a pool or I/O; also examine `WAITING` and `TIMED_WAITING` and the external dependencies.

### 2. Thread dump collection
On HotSpot with default signal handling, `SIGQUIT` prints the dump to the JVM's stdout. Confirm the PID and the signal configuration before using `kill -3`; with `-Xrs` or another runtime, do not assume that behavior. When available and compatible with the target JVM, `jcmd <pid> Thread.print -l` is another option. Weigh the impact of the collection on the incident.

```bash
# In the same PID namespace as the JVM, after identifying the process:
kill -3 "$PID"
# On Kubernetes, if stdout goes to the container logs:
kubectl logs -n <namespace> <pod-name> -c <container-name> --since=2m
```
Preserve each complete dump: a fixed line cutoff can drop threads and the deadlock summary. Correlate the workers by identifier and analyze state, stack, awaited locks and their owners.

### 3. Comparing dumps to steer the investigation
To investigate persistence or activity, start with two dumps about 10 seconds apart and adjust the sampling to the duration of the symptom:
- **Identical stack:** consistent with waiting, repeated work or blocking; it proves neither a definitive hang nor the absence of a timeout.
- **Different stack:** shows different positions across samples; it proves neither useful progress nor N+1.
- **Deadlock:** look for the dependency cycle between threads and locks, or the JVM's explicit detection. For database locks or external dependencies, also consult that system's evidence.
- **N+1:** correlate SQL per request/operation, repeated queries and entity count. Use logs, tracing or ORM/database statistics and confirm the access path in the code. Without that correlation, record the hypothesis and the pending collection.

An explicit deadlock detection in one dump can already be enough evidence for that cycle; repeating samples helps when the mechanism is still uncertain.

### 4. Database traffic as a clue
Prefer existing metrics or traces for the operation. If you need to observe the network, filter the database host and port in the relevant network namespace, with a limited window:
```bash
# Linux with timeout and tcpdump available; replace the IP with the target database.
# Up to 10 seconds or 5000 packets; preserve stderr and the timestamps.
timeout -s INT 10s tcpdump -i any -nn -q -tttt -c 5000 'host <db-ip> and tcp port 1521'

# Sample of established TCP connections (does not count queries):
ss -Htn state established '( dport = :1521 )'
```
`-c 5000` is a capture limit, not a query measurement. Record the real duration, packets captured/dropped and any errors; termination by `timeout` is expected when the window is reached. If the tool or permission is missing, record the gap and use the existing observability.

Packets include ACKs, retransmissions and segmented results; aggregated traffic can mix operations, and TLS can hide the SQL. Packet or connection volume, on its own, confirms neither N+1 nor an unfiltered query.

### 5. Memory and throttling investigation in containers
Find the cgroup version and the process directory using `/proc/<pid>/cgroup` and the mounts visible in the same namespace. On v2, the controllers share the hierarchy: `memory.events` sits in the cgroup directory, with no mandatory `memory/` subdirectory. On v1, use that version's own interfaces.

```bash
# Set CGROUP_DIR to the v2 directory identified for the target process.
cat "${CGROUP_DIR:?set the target cgroup directory}/memory.events"
cat "$CGROUP_DIR/memory.current" "$CGROUP_DIR/memory.high" "$CGROUP_DIR/memory.max"
```
Compare deltas during the incident window, keeping the same cgroup; recreating the container invalidates that comparison. The counters are cumulative and `memory.events` includes descendants; consult `memory.events.local` for local events.

| Field | What an increment tells you |
|---|---|
| `high` | Processes were throttled and went through direct reclaim after exceeding `memory.high` |
| `max` | Usage was about to exceed `memory.max`; reclaim may have avoided an OOM |
| `oom` | There was an allocation event about to fail at the limit; it does not equal a killed process |
| `oom_kill` | Processes in the cgroup were killed by an OOM killer |

A historical `max > 0` does not demonstrate current pressure. Correlate deltas, usage, limits, memory pressure and pod/kernel events. For CPU throttling, examine `cpu.stat` and the quota; for JVM pauses, use GC logs and their duration in the same window.

### 6. Memory budget for JVM containers
The limit must accommodate the total peak accounted by the cgroup, validated under representative load. Gather the JVM's effective flags; `JAVA_OPTS` is only one possible source of configuration.

```text
Budget = heap + metaspace + thread stacks + code cache
       + direct buffers + other native allocations
       + other consumption accounted by the cgroup + validated margin
```

Use consistent units and avoid double counting: the cgroup total already includes components observed in the process. `Xmx` caps the heap; it does not cap total memory. Without an explicit `MaxMetaspaceSize`, there is no default 128 MB ceiling. The margin depends on peaks, concurrency and load variation, not on a universal percentage.

If NMT is already enabled, use `jcmd <pid> VM.native_memory summary` to break down HotSpot's memory, distinguishing reserved from committed. NMT does not cover all native memory; cross-check with RSS, cgroup metrics and buffers. Enabling it requires configuration at startup and has an observation cost. If measurements are missing, deliver the pending budget and the required collection, without declaring a safe limit.

---

## Diagnosis memo format (deliverable)

When reporting a technical investigation, use the following concise pattern:

1. **Observed symptom:** what broke or hung (with timestamp and pod/service identifier).
2. **Measured evidence:** data with source, unit, time, window and collection limits.
3. **Conclusion and degree of evidence:** proven mechanism or hypotheses, with the evidence and the collection still missing to tell them apart. A recovered service can coexist with a cause still under investigation.
4. **Immediate mitigation:** distinguish proposed action from applied action; record rollback and verified result when something was executed.
5. **Fix or next investigation:** well-grounded fix with the smallest diff, or the next experiment needed.

---

## Diagnosis closing checklist
- [ ] Was the top-down triage (USE / RED / golden signals) run before the expensive collection, and is the cell that justified it named?
- [ ] Was the problem bounded by contrast, with the *is-not* filled from observation?
- [ ] Was the state of the data mapped before any destructive command?
- [ ] Are facts, hypotheses and gaps separated, with source and collection window?
- [ ] Do the samples support the conclusion, without equating packets with queries or stacks with root cause?
- [ ] Were cgroup events interpreted by field, scope and delta?
- [ ] For applied actions, were rollback and service recovery verified?
- [ ] Is the fix well grounded, or is the next investigation explicit?

## Technical references

- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html): utilization, saturation and errors per resource.
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/): the four golden signals.
- [Oracle — Hangs and loops](https://docs.oracle.com/en/java/javase/24/troubleshoot/troubleshoot-process-hangs-and-loops.html): interpreting dumps and investigating blocking.
- [Oracle — HotSpot signals](https://docs.oracle.com/en/java/javase/24/troubleshoot/handle-signals-and-exceptions.html): SIGQUIT behavior and signal configuration.
- [tcpdump — Manual](https://man7.org/linux/man-pages/man1/tcpdump.1.html): capture, limits and packet counters.
- [Linux — cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): hierarchy, interfaces and semantics of memory events.
- [Oracle — JVM options](https://docs.oracle.com/en/java/javase/24/docs/specs/man/java.html): heap, metaspace and native memory limits.
- [Oracle — Native Memory Tracking](https://docs.oracle.com/en/java/javase/24/vm/native-memory-tracking.html): reach and limitations of the measurement. Check compatibility with the JVM version under investigation.
