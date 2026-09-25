# AI / LLM Features

Text, voice, or realtime AI in the app. Skip unless `PRODUCT.md` marks AI "now".

Prereq: `secure-backend.md`. Every model call goes through a server you control — a provider key in the app is someone else's free inference.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Build the AI feature described in `PRODUCT.md`.

### Grill

- **What problem does the AI solve that a normal feature would not?** If the answer is vague, stop here — an LLM added because it is available is latency and cost with a chat bubble on top.
- **Which interaction shape?** These are three different builds:
  - **A — Request/response.** User acts, model answers, done. Cheapest, most reliable. Recommended default.
  - **B — Streaming text.** Answers long enough that waiting feels broken.
  - **C — Realtime voice or video.** A live session with a transport layer. An order of magnitude more work and cost.
- Which provider and model, and what is the cost per interaction? Multiply by expected usage before building — this is the question most projects skip until the first invoice.
- **What data leaves the device?** User content, personal data, anything from `DOMAIN.md`? Confirm the developer accepts sending it to this provider, whether users must be told, and whether the provider trains on it.
- What happens when the model is wrong, refuses, or returns nonsense? Every AI feature needs a defined failure behavior, because it will happen.
- Is the output stored or acted on? If it writes to the database or triggers an action, it must be validated first.

### Build

**Server side** (per `secure-backend.md`)

- Provider key server-side only; the app calls your endpoint
- Prompts live in version-controlled files, not inline strings scattered across handlers. A prompt is behavior — it gets reviewed and changed deliberately
- Context assembled server-side from `DOMAIN.md` entities the user is allowed to see. Never let the client supply the system prompt or the context — that is prompt injection with the door held open
- Per-user quota and rate limit, enforced before the provider call
- Timeouts, and a bounded retry that does not silently double the bill

**App side**

- Explicit states: idle, sending, streaming, done, failed, cancelled
- **Cancellation.** The user must be able to stop a running generation, and cancelling must actually abort the request, not just hide it
- Streaming rendered incrementally, with the scroll position behaving sanely as text grows
- Output treated as untrusted: validate shape before parsing, before storing, and before acting. If you asked for structured data, verify it is structured — do not assume
- Make it visible that the answer is AI-generated where the user could mistake it for fact or for a human

**Realtime voice/video (C only)**

- Ephemeral session token from the server, scoped to this user and session, with the minimum role that allows publishing
- Microphone and camera permissions requested at the moment of use, with the denied path handled
- Session lifecycle explicitly handled for: user ends it, screen unmounts, app backgrounds, network drops, and app killed. Each one must tear the session down — per-minute billing does not stop because the user swiped away
- Connection states surfaced: connecting, connected, reconnecting, failed
- Verify the SDK's actual join and lifecycle method signatures against the installed version before writing the flow. Do not write against remembered API shapes

### Done when

- [ ] No provider key in the bundle — grep confirms
- [ ] A client attempting to override the system prompt or inject context is ignored
- [ ] Quota enforced: exceeding it returns a clear message instead of a charge
- [ ] Cancelling mid-generation aborts the request
- [ ] A provider outage shows a real message and leaves the app usable
- [ ] Malformed model output cannot corrupt stored data
- [ ] Realtime: backgrounding, killing, and losing network each end the session — verified server-side, not assumed
- [ ] Cost per interaction measured against the estimate
