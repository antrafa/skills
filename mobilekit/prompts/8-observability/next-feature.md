# Next Feature

The plan ran out; production data is the new input. `post-release.md` produces the four numbers — this prompt turns them into the next cycle of `docs/BUILD-PLAN.md`, so the `next` phase keeps working unchanged.

Run it when every box is checked, real users are in the app, and the question is "what do we build now?". Prereq: the four numbers exist with baselines. Without them this prompt is taste with a checklist — either ship the instrumentation first, or be honest that the next cycle is a bet and run a discovery round for the delta instead.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DESIGN.md`, `docs/BUILD-PLAN.md`, and the four numbers from `post-release.md` first. Read `docs/LAUNCHES.md` if it exists.

Decide what the next build cycle contains, from evidence.

### Hard rules

1. **A number outranks an opinion.** A candidate justified by no number is a bet — legitimate, but written down as one, never dressed up as data.
2. **Repair competes with surface, and usually wins.** A funnel step losing half its users is worth more than any new feature; new scope must argue against fixing the weakest number, not assume the slot.
3. **Every chosen step names the number that proves it worked**, and ships behind the same event — `post-release.md`'s loop back, applied forward.
4. **New scope comes from `PRODUCT.md`'s "later" column.** Scope in nobody's document means a discovery round for the delta first — not a line item smuggled into the plan.
5. **The plan stays the tracker.** The output is a cycle appended to `docs/BUILD-PLAN.md`, one prompt per box, so `next` runs it with no new mechanics.

### Grill

- **Which goal is this cycle for — activation, retention, conversion, or reach?** Recommended: the weakest of the four numbers against its own baseline decides; say which number and its value today.
- **What does the qualitative signal say?** `docs/LAUNCHES.md` responders, store reviews, beta feedback — read them before asking. They name what the numbers cannot: *why*.
- **How big is the cycle?** Recommended: 3–5 boxes ending in something shippable. A cycle that cannot ship is a stall with a theme.

### Build

- Gather candidates from three sources: the worst funnel step (`analytics.md`), capabilities marked "later" in `PRODUCT.md`, and what responders and reviews actually ask for.
- Rank them with the evidence each carries — a number, a quote, or "bet". Present the ranking; the developer picks.
- A candidate needing new screens or a domain change gets its design and domain round for the delta before entering the plan.
- Append the cycle to `docs/BUILD-PLAN.md`:

```markdown
## Cycle 2 — [goal] — [date]
Target: [number], [today's value] → [target]
- [ ] [step] · [prompt id] · proves: [which number moves]

### Rejected this cycle
| Candidate | Why not now |
|---|---|
```

### Done when

- [ ] The cycle's goal is named and tied to one of the four numbers, with its value today
- [ ] Candidates were ranked with their evidence — each a number, a quote, or an explicit bet
- [ ] The chosen steps are in `BUILD-PLAN.md` as one-prompt boxes, and `next` can run the first one
- [ ] Every step names the number that will prove it worked
- [ ] What was rejected is recorded with the reason, so the next cycle does not re-argue it
