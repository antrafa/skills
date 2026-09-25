# Building on an API you do not control

For the case where the data already exists and you cannot change its shape — a public dataset, a legacy system, another team's service. The workflow is the same five commands; what changes is that two of them stop and ask you for things only the API's owner can supply, and one prompt splits your types in two.

The example is **Linha**, a transport timetable app: lines, stops, departures, service alerts. Chosen because you can point this tutorial at a real transit API, and because real transit APIs have field names like `DEP_TM_SCHED` and dates that are strings — which is what makes the DTO lesson land.

> **Not your starting point?** [Thirty minutes and no accounts](quickstart.md) · [a complete app from scratch](new-app.md) · [users see each other's content](social-app.md) · [a project you already started](existing-project.md) · [an app already in the stores](legacy-app.md). Full index: [TUTORIALS.md](../TUTORIALS.md).

---

## Before you start

The stalls on this path are all the same stall: the agent needs something about the API that is not in your head.

| | Why |
|---|---|
| The real contract — an OpenAPI/GraphQL schema, **or** one captured response per endpoint | `domain-model.md` scenario C step 1: get the real contract *before writing a single type*. Not a description of it. |
| Among the captures: an error response and an empty-collection response | `api-integration.md` asks for these by name. The empty case is where a list screen's empty state comes from; the error case is where the error taxonomy comes from. |
| A physical device, on a network that can actually reach the API | Several `Done when` items name real hardware and a named environment. If the API needs a VPN or an allowlist, that goes into `AGENTS.md` — "works on my machine" is literal here. |
| The answer to "who owns this, and how are breaking changes announced?" | Recorded in `docs/DOMAIN.md`, including "nobody tells us". That answer changes how defensively the boundary gets written. |
| To know whether your API key is publishable or secret | Decides whether there is a server in this project at all. See [Where the key lives](#where-the-key-lives). |

---

## The behaviour that surprises people first

You ask for the timetable screens. The agent writes no types. Instead:

> Before I write a type for this: do you have an OpenAPI spec, or captured responses? I need one real response per endpoint I will call — `/lines`, `/stops`, `/stops/{id}/departures`, `/alerts` — plus one error response and one empty-collection response. Paste them, give me a link I can fetch, or save them under `docs/vendor/`. I will stop until they arrive.

This is not the agent being unhelpful, and it is not a limitation of your setup. It is [`RULES.md`](../../prompts/RULES.md) §3 — documentation is an input the agent requests, not something it recalls — plus `domain-model.md`'s scenario C, which says in step 1: do not model from prose descriptions or from a guess at what the API "probably" returns.

**`docs/vendor/` is where the answer goes** so the ask happens once. Anything saved there is read first on later runs, by every later step: the mapper, the query layer, the list screen.

The alternative is worth stating plainly, because it is what every other tool does. A type modelled from your prose description is a guess. It will be right about the field names you remembered and wrong about the one field that was always nullable — and you find that out at runtime, on a device, on the one route where the operator leaves the delay column empty. That is not a type error you can grep for; it is a crash three renders from its cause.

---

## Phase 1 — discovery, and the one answer that shapes everything

```
/mobilekit:init
/mobilekit:discovery
```

Seven blocks, one question per message. Block B still matters — the vocabulary is yours, not the API's:

> **What is the real vocabulary? The 3–7 nouns you would use talking to a colleague, and how they relate.**
>
> — A Line calls at many Stops. A Departure is one Line leaving one Stop at a time. An Alert affects a Line.

Then Block D, question 12, which is the whole reason you are reading this tutorial rather than [new-app.md](new-app.md):

> **Does the data already live somewhere?**
> Recommended: **C — an API or database you cannot change**, from what you have described. Confirm or change.
>
> — C. It is the transit authority's API. Read-only, and they will not add endpoints for us.
>
> **Then question 13: how do I inspect it?** A spec URL, a sample payload, read-only credentials — whichever exists.
>
> — There is a Swagger page, but it was last updated two majors ago.

Note what the agent does with that last answer rather than shrugging at it. `api-integration.md`'s first grill question offers three contract shapes — **A** formal spec, **B** no spec with captured payloads, **C** GraphQL — with this recommended default: whichever the API team actually publishes, *because A with a stale spec behaves worse than B with fresh payloads*. A stale spec produces confident types, which is the worst kind.

Linha lands on **B**: derive DTOs from real captured responses, and record which fields were observed, from which environment, on which date.

**What you get:** `docs/PRODUCT.md`, with `Scenario: C external/immutable source` and the access route on the `Data` line. Every later prompt reads that line before doing anything.

---

## Phase 2 — design, then plan

```
/mobilekit:design
/mobilekit:plan
```

Design is unchanged by the data source: screens trace to journey steps, and every core screen gets its four states — plus a fifth, offline, because `PRODUCT.md` says the app must work in a tunnel. Linha came out at three core screens: **Stops**, **Stop** (next departures), **Alerts**. The plan is where scenario C shows:

```markdown
## Foundation
- [x] expo-setup · already present
- [ ] nativewind
- [ ] design-system
- [ ] domain-model
- [ ] ui-components
- [ ] app-shell · boot: saved-Stops hydration and the error boundary

## Platform
- [ ] api-integration · the transit API, contract shape B
- [ ] react-query
- [ ] zustand · saved Stops only, persisted locally

## Screens
- [ ] tab-navigation · Stops · Alerts · Settings
- [ ] list-screen · Stops
- [ ] detail-screen · Stop — next Departures
- [ ] list-screen · Alerts

## Features
- [ ] offline · cached reads only
- [ ] dark-mode

## Skipped
| Step | Why |
|---|---|
| supabase | Data scenario C — `api-integration` replaces it |
| dev-environment | Expo Go reaches the API — re-add with the first native dependency |
| auth-clerk, auth-backend, account-recovery | PRODUCT.md: accounts = no. Saved Stops live on the device |
| form-screens, media-upload, content-moderation | Nothing here is user-authored |
| secure-backend | The API key is publishable — re-add the moment a secret-keyed endpoint is needed |
```

Two rows to read properly. `supabase` was not skipped for being unwanted; it was skipped because `plan` decides between mutually exclusive prompts and says why in one line. And `secure-backend` was skipped **conditionally** — the condition is written down, because it is the row that becomes wrong first.

---

## Phase 3 — `domain-model`, where the two type layers appear

```
/mobilekit:next
```

The step announces itself, states the scenario back — "`PRODUCT.md` says scenario C; confirming before I choose a branch" — and then asks for the payloads if they are not already under `docs/vendor/`.

Once they are, it presents the mapping table and waits. Hard rule 3: show the model and get approval before writing files.

| DTO field, exactly as it arrives | Type in the payload | Domain field |
|---|---|---|
| `RouteShortName` | `string` | `Line.code` |
| `stop_pt_nm` | `string` | `Stop.name` |
| `DEP_TM_SCHED` | `string`, `"2026-08-08T14:32:00"`, no zone | `Departure.scheduledAt` — a real date, in a stated zone |
| `rt_dly_sec` | `number \| null` | `Departure.delay` — seconds, or unknown |
| `alrt_txt_1`, `alrt_txt_2` | `string`, `string \| null` | `Alert.body` — one field |
| `svc_flg` | `"Y" \| "N" \| ""` | `Alert.isActive` — and the third value is a question, not a guess |

Three directories come out of this, and keeping them apart is the point:

- `types/dto/` — mirrors the payload exactly, awkward names, string dates, nullable everything
- `types/` — `Line`, `Stop`, `Departure`, `Alert`, in your vocabulary
- `services/transit-mapper.ts` — the only place that converts between them

The rule `domain-model.md` states, and the one that gets argued with most: **keep the awkward name in the mapping layer and use the product's name in the app.** Not `stop_pt_nm` in a component, and not a renamed DTO either.

**Why one shared type is the tempting mistake.** It is fewer files and no mapper, and for a week it is genuinely less work. Then `DEP_TM_SCHED` is in twelve components, each parsing that string its own way, and one of them forgets the missing timezone. Then upstream renames a field, and the diff is every screen instead of one file. The mapper is not ceremony; it is the single place where an upstream change is absorbed.

The last row of that table — `svc_flg`, three values, one an empty string — is what the mapper is for. Ask what `""` means. If nobody knows, that is `UNDECIDED — ask before assuming` in `DOMAIN.md`, not a silent `false`.

### Validate at the boundary

The external response is untrusted input. Scenario C step 3, and `api-integration.md` repeats it: validate every response where it enters the app and fail with a domain error, because `undefined` reaching a screen is a crash three renders away from its cause. The stack trace names a component that renders a time; the bug is that the API dropped a field an hour ago.

The agent asks before reaching for a library:

> No schema-validation library is installed. Four endpoints is few enough that hand-written guards in the mapper are honest — that is what I recommend. Adding one is also fine, and it pays off past roughly a dozen endpoints. Which?

`RULES.md` §5: ask before adding a dependency, say what it replaces and why doing it by hand is worse. Either answer is correct; the point is that it is your answer.

### The `DOMAIN.md` fragment that matters most

```markdown
## Source: transit-api (scenario C — external, immutable)

Contract shape: B — no usable spec. DTOs derived from captured responses,
production environment, 2026-08-08. `alrt_txt_2` observed once, in one alert.

### Limits of the source
- **No server-side filtering.** `/stops` returns the whole set (~4,100 rows).
  There is no query parameter. Search must be local.
- **No pagination.** One response or nothing, on every collection endpoint.
- **Rate limit** per key per minute. `429` carries no `Retry-After`.
- **Eventual consistency.** `rt_dly_sec` lags the on-street display by up to a minute.
- **Owner:** transit authority, data team. Breaking changes: announced nowhere.
  Treat every field as capable of disappearing without notice.

### Ours vs theirs
Saved Stops are ours — device-local, joined to their `/stops` payload by stop id.
Nothing else in this app is ours.

### Undecided
- `svc_flg == ""` — meaning unknown. UNDECIDED — ask before assuming.
```

---

## The connection most readers miss: those limits are screen decisions

Scenario C step 4 does not record the limits as trivia. It records them "because those limits will decide screen behavior later" — and later is two steps down the plan, in a different prompt, possibly a different session. Here is the payoff, verbatim from `list-screen.md`'s grill:

> **Does search filter locally or query the server?** Local only works when the full set is already loaded. Server search needs an endpoint and debouncing.

An agent without `DOMAIN.md` asks you that question cold. With it, the answer is already determined and the reasoning is auditable:

| Limit recorded | What the screen can promise |
|---|---|
| No server-side filtering | Search is local — so the Stops screen must load all ~4,100 rows once, and that decides the loading state and the cache |
| No pagination | No end-reached paging, no footer loader. Guess cursor pagination for an API that has none and you ship silent duplicate rows, which no user reports as a bug |
| Rate limit, no `Retry-After` | Pull-to-refresh is throttled; `react-query` gets a long `staleTime` for Lines and Stops and a short one for Departures — reference data and live data never want the same value |
| Eventual consistency | Departures are shown **with their age**, per `offline.md`: show cached data with its age rather than pretending it is current |
| Fields may vanish without notice | The boundary validation is not defensive programming for its own sake; it is the announcement channel the API owner does not provide |

---

## Where the key lives

The grill in `api-integration.md` asks how the API authenticates, and one branch has no client-only answer.

| If the key is… | Then |
|---|---|
| Called publishable, anon, or public by the provider's own docs — rate-limited per app, cannot spend money, cannot read anyone else's data | `EXPO_PUBLIC_*` is correct. `RULES.md` §6 says exactly this. No server, no proxy, `secure-backend` stays skipped. |
| Called a secret key, or billed per call, or grants reads beyond what one user should see | There is no client-only path. `secure-backend.md` first, then a proxy the app calls. |

There is no middle option because `EXPO_PUBLIC_*` values are compiled into the JavaScript bundle and extractable from a published app in minutes. "It works in development" is not evidence of anything, and once such a key is committed it must be **rotated**, not deleted — it is in git history. `ship`'s secret sweep greps a real build for each known secret value, which is where this gets caught if it was missed.

Linha's key is publishable, so the plan skipped `secure-backend` with the condition attached. mTLS or a corporate gateway is the same conclusion reached faster: a client certificate is not something an Expo app carries, so a server in front is decided now rather than discovered during the release build.

---

## What a `Done when` item actually looks like here

From `api-integration.md`:

```
- [ ] A malformed or truncated response surfaces a domain error and never
      reaches a screen as `undefined`
```

That is not a box to read and agree with. Running it means pointing the client at a fixture with `DEP_TM_SCHED` removed, or truncating a real response, and watching the Stop screen. Two outcomes: it renders your error state and the log names the endpoint and the field, or something renders `Invalid Date` and the item is **not met**. The report says which:

```
Step: api-integration · prompts/4-platform/api-integration.md
  met             real request from device against production
  met             malformed response → DomainError.malformedResponse, no undefined
  met             airplane mode gives the offline error, not the generic one
  not met         pagination past page two — the API has none; noted in DOMAIN.md
  not verifiable  correlation id in the server log — no log access on this API
Box left unticked: 1 item not met, 1 not verifiable.
```

Two lines there are worth more than a green tick. `not verifiable` on the correlation id is honest — you cannot read the transit authority's logs, so the check is unavailable rather than passed, and that tells you nobody on your side can prove anything when the API misbehaves at 14:32. `not met` on pagination is a checklist item that does not apply, recorded as such rather than quietly ticked.

```
/mobilekit:status
```

```
Phase:      build
PRODUCT.md  ok · 1 UNDECIDED
DESIGN.md   ok
BUILD-PLAN  8/19 · next: react-query
Drift:      plan says api-integration done, box unticked in BUILD-PLAN
Next:       /mobilekit:next
```

---

## The ways a step stops on this path

| It says | Why | You |
|---|---|---|
| "I need one captured response per endpoint, plus an error and an empty collection, before I write a type" | `RULES.md` §3 and scenario C step 1. A type from prose is a guess | Save them under `docs/vendor/` once |
| "Is that Swagger page current? A stale spec behaves worse than fresh payloads" | The contract-shape question has this as its recommended default | Say honestly which is fresher |
| "Here is the DTO → domain mapping. Approve before I write files" | Hard rule 3. Names are cheap now, expensive across ten screens | Read every row. Check `svc_flg`-shaped oddities |
| "Which failures must the user tell apart?" | At minimum four: gone, offline, session died, API broken | Decide the copy per case. One "Something went wrong" for all four generates tickets nobody can answer |
| "Which write endpoints are safe to retry, and do any accept an idempotency key?" | Usually undocumented — the prompt says ask the API owner | This may mean emailing someone. It is not the agent stalling |
| "Is staging data shaped like production's — the volume, the odd characters, the long names?" | A list tested against six tidy staging rows is untested | Answer truthfully, or test against production reads |
| "No validation library installed — hand-written guards, or add one?" | `RULES.md` §5 | Either. It is your call, not a default |
| "The provider's docs call this a secret key" | `RULES.md` §6 | `secure-backend` first, then this step |
| A checklist item comes back **not verifiable** | No device, no server log, no second page of data | Fix the gap or accept the unticked box |

**One limitation, stated rather than papered over.** Nothing in this library watches the upstream contract for you. You get boundary validation that turns a change into a domain error, and `api-integration.md`'s instruction to commit or pin the spec so a regeneration diff shows what moved. Upstream drift is caught at runtime by your own code, never in CI by a contract test — there is no prompt for that.

---

## The mistakes that cost the most on this path

**Describing the API instead of handing it over.** The single most expensive shortcut here. You get types that are right about every field you remembered and wrong about the nullable one you did not, and the failure lands on a device, in production, on the one route with an empty delay column.

**One shared type for DTO and domain.** Saves a file this week. Costs you `DEP_TM_SCHED` in twelve components, twelve parses of a zoneless string, and a rename upstream that becomes a diff across every screen instead of one mapper.

**Building the Stops list before `DOMAIN.md` records the limits.** The plan orders `domain-model` first for a reason. Override it and you implement end-reached pagination against an API that has none, then wonder why the footer loader never resolves.

**Putting a secret key in `EXPO_PUBLIC_*` because it works in development.** It does work. It also ships extractable in every build, and the fix is not deleting the file — it is rotating the key and explaining to its owner why.

---

## Where to look next

- [`new-app.md`](new-app.md) — the same loop run to a monitored release: what `ship` and `store-compliance` actually cost. Your next read
- [`existing-project.md`](existing-project.md) — if the screens already exist and you are retrofitting the boundary
- [`COMMANDS.md`](../COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../prompts/RULES.md`](../../prompts/RULES.md) — §3 and §6 shape this path. Short, worth reading yourself
