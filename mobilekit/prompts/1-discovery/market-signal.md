# Market Signal

The check the rest of the library cannot perform: whether anyone outside the repo wants this app. Every other prompt verifies the build against the documents; this one verifies the documents against real people, at the moments where being wrong is still cheap.

Run it when a phase document lands — it is **optional and never gates a phase**. The workflow proceeds with or without it; what it removes is the ability to not know. Skipping it is a legitimate decision. Skipping it silently is how six months of correct execution ships an app with no users.

Produces and maintains `docs/LAUNCHES.md`.

---

## Prompt

Read `RULES.md` (this library) and `docs/PRODUCT.md` first. Write no application code and install nothing.

Put what exists today in front of real potential users, and log what comes back.

### Hard rules

1. **The developer sends everything.** Messages here are drafts under `RULES.md` §5 — the agent never posts, mails, or DMs anyone.
2. **Warm before wide.** Anyone who responded to an earlier moment hears about this one first, personally, before any public channel.
3. **Silence is a result.** "Sent to 10 people, 0 replies, 5 days" is a log entry with a decision attached, not an absence.
4. **A reply from a friend is a reply, labelled as one.** Politeness reads different from demand; the label is what keeps the log honest.
5. **The same target missed twice means the message is not the problem.** The response is rereading `PRODUCT.md` — audience, central object, or the problem itself — not a third rewrite.

### The moments

Four, each tied to a document or build the workflow already produces. Read `docs/LAUNCHES.md` to know which is next; no file means moment #1.

| # | After | What goes out | The signal that counts |
|---|---|---|---|
| 1 | `PRODUCT.md` | The problem and the promise, in the audience's words | One substantive reply |
| 2 | `DESIGN.md` or first screens | What it looks like | "Can I try it?" — a name on a list |
| 3 | A beta build | The invite (`beta-and-review.md` owns the tracks) | One tester reaches the success action |
| 4 | Store release | The public announcement | First payment — or for a free app, the first stranger's install or review |

The signals are ordered on purpose: `reply → conversation → waitlist → activated tester → payment`. Each moment asks for slightly more commitment than words, from people with less obligation to give it.

### Grill

- **Which moment is this?** A fact — read `docs/LAUNCHES.md` and confirm.
- **Who can be reached today, by name?** Specific people matching the audience in `PRODUCT.md`, or one named community where they already congregate. "Some old contacts" is not a list; eight names are. If no person and no community can be named, stop: that is a finding about `PRODUCT.md`'s audience section, and it is worth more than anything a send could return.
- **Does the message carry a price?** Recommended once `PRODUCT.md §Monetization` exists: a stated price turns "sounds useful" into evidence. The developer may decline — record that the signal was read unpriced.
- **When does it go out?** A named day within the next two. An undated draft is a decision not to send, made without saying so.

### Build

- Draft 2–3 variants from `PRODUCT.md`'s own vocabulary: open with the problem as the audience says it, show the new thing, end with one question that can be answered in a sentence. Label them drafts; the developer edits and approves.
- From moment #2 on, reference the earlier thread — "an update on what I posted about" outperforms a fresh pitch, because the audience watched it become real.
- Assemble the send list: responders from the log first, then the one channel. New channels are for channels that stayed silent, not for nerves.
- After the sends: log every response verbatim where useful — replies in the audience's words are `PRODUCT.md` corrections and future store copy. Add each new responder to the list with where they came from.
- Read the result and write the decision into the entry: **proceed**, **rewrite once and resend**, or **reread `PRODUCT.md`** (rule 5).

---

## Output

Create or update `docs/LAUNCHES.md`:

```markdown
# Launch Log

Strongest signal so far: [none | reply | conversation | waitlist | activated tester | payment] — [date]
Next moment: [#N — after which document or build]

## Responders
| Who | Came from | First response | Strongest signal | Warm? |
|---|---|---|---|---|

## Moment #1 — after PRODUCT.md — [date]
Channel: [...] · Sent: [summary or link]
Replies: [n, warm/cold split — 0 is an entry]
Signal reached: [...]
Decision: [proceed | rewrite once | reread PRODUCT.md]
```

One entry per moment, newest last. Anyone reading only this file should know how much contact this product has had with reality, and what it said back.

---

### Done when

- [ ] The message went out on the named day — logged with channel and date, not drafted and parked
- [ ] Every response is in the log, warm or cold labelled, including a zero
- [ ] New responders are on the list with their source
- [ ] The entry states the decision: proceed, one rewrite, or reread `PRODUCT.md`
- [ ] The next moment is named, so contact does not lapse for a whole phase
