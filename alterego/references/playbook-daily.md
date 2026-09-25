# Playbook: Workday (`/alterego daily` and `/alterego wrap`)

The day has two short rituals: open the board in the morning and close it at the
end. Both fit in two minutes. What happens between them is normal work, with the
other playbooks.

---

## Invocation modes

```
/alterego daily [<overview>]     (organizes the day; without an overview, uses profile and repository)
/alterego wrap [<notes>]         (closes the day; without notes, rebuilds from the session and git)
```

In Codex: `$alterego daily`, `$alterego wrap`.

---

## 1. `daily`: opening the board

The user dumps whatever is on the desk (meetings, bugs, PRs, designs, loose ends),
without organizing it first. Organizing is the persona's job.

1. **Separate noise from real priority.** Whatever has an owner, a deadline and a
   consequence stays; the rest becomes a waiting list, stated in one line.
2. **Apply the yardstick, in this order:** production stability before new work;
   a blocked colleague has high operational priority; architecture and risk
   mitigation come before features when they compete.
3. **Limit the work in progress.** Prioritizing without limiting produces a
   board where everything is started and nothing is finished. Two items in
   progress is the working ceiling for one person; the third opens only when one
   closes. So the board opens by asking what can be **finished** today, not what
   can be started — a task 80% done delivers zero, and the more work in flight,
   the longer every item takes to come out (Little's Law).
4. **When two items compete for the same slot, compare the cost of delay, not
   the effort.** (CD3, Don Reinertsen.) Which one costs more per day of waiting,
   and between two with a similar cost, the shorter one goes first. That is why
   a two-hour fix that unblocks three people beats a two-day refactor nobody is
   waiting on.
5. **Slice into concrete deliverables** and point at the first step. If there is a
   meeting in the way, offer to move forward in parallel on the front that does
   not depend on it (analysis, draft, MR reading).
6. **Pull what was left from yesterday.** If Mentat has the entry from the last
   `wrap`, its pending items go onto the board without the user having to
   remember.
7. **Resurface one earlier learning**, from a past `wrap` — a week or a month
   ago, not yesterday's. Retrieval spaced out in time is what turns a noted
   gotcha into something the user actually has at hand; a learning filed and
   never read again was typing. One line, at the end, no quiz.

Done when the user knows what to do first and what not to do today.

## 2. `wrap`: closing the day

This is what gives "journey partner" its meaning: the next day starts where this
one stopped, not from zero.

1. **Rebuild the day from evidence**, not from memory: `git log --since=today`
   in the repositories touched, dirty working tree, open worktrees, MRs with a
   pending review verdict, what was discussed in this session.
2. **Return the close-out** in four short blocks:

   ```
   Done
     - <deliverable with evidence: commit, MR, recorded decision>
   Left over
     - <what did not close, and the concrete next step>
   Learned
     - <fact, gotcha or criterion worth carrying; one per line>
   Open risk
     - <what could blow up tomorrow with nobody watching>
   ```

   An empty block does not appear.
3. **Offer to record, once.** "Left over" and "Learned" are what is worth
   persisting. On a "yes", save through the `mentat` skill (an entry of type
   `learning` or `note`, one per item that deserves it). Without Mentat, append
   to the end of `~/.alterego/journal.md`, one section per date. Without a
   "yes", nothing is saved and the close-out stays in the conversation.
4. **Point at tomorrow's first step** in one line. It is what the next `daily`
   will pull.

Done when the pending items are written somewhere the next session reads.

---

## Closing checklist
- [ ] In `daily`, was the noise named and left out, instead of becoming an item?
- [ ] Was the priority yardstick applied in order, and is the first step stated?
- [ ] Does the board say what closes today, respecting the WIP ceiling, instead of listing everything that could start?
- [ ] In `wrap`, does everything under "Done" have evidence, not recollection?
- [ ] Were the pending items saved only after the "yes", and through the `mentat` skill when it exists?
