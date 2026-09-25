# Posting to the MR — API mechanics

Read this file only after the action gate in [mr-flow.md](mr-flow.md), once
the user **has already chosen** an action.

> **Everything here writes to GitLab on the user's behalf.** The rule applies
> per command, not per session: show the content and the target, get a "yes"
> for **that**, execute **only that**. Re-running the skill starts with no
> authorization whatsoever.

Use `glab api` (already authenticated; resolves the host from `origin`,
self-managed instances included). `:id` is the URL-encoded project — `glab api`
accepts a literal `:id` when run inside the repo.

## Comment template

What goes to the MR is read by someone else. Peer tone, with no structural
headers like "Observation:" / "Impact:". Four parts, in this order:

1. **Title** in bold, preceded by the Conventional Comments label that matches
   the severity — `issue (blocking):`, `suggestion (non-blocking):`, `nit:`,
   `question:`, `praise:` (the mapping is in
   [playbook-review.md](playbook-review.md#severity-and-verdict)). The label is
   not a structural header: it tells the author in the first three words whether
   this blocks the merge.
2. **What was noticed and why it matters** — 1-2 sentences, peer tone ("I
   noticed that...", "what if we...").
3. **Context** — path and line in italics.
4. **Suggestion** — an actionable recommendation, with a code block **in the
   file's language** when it fits.

Example:

````text
**suggestion (non-blocking): "pending" status repeated as a literal**

I noticed that `"pending"` shows up raw in two places. If the status name ever
changes, missing one of them leaves the behavior inconsistent and the bug is
silent.

*Relevant lines: `src/service/OrderService.java` around line 42 and
`src/handler/CheckoutHandler.java` around line 17*

What if we pulled it out into a constant?

```java
public static final String STATUS_PENDING = "pending";

if (STATUS_PENDING.equals(order.getStatus())) {
    // ...
}
```
````

Do not use the dense terminal format here, and do not invent another format.

## Inline comment (draft notes + batch publish)

Posting note by note fires one notification per finding and floods everyone's
inbox. Create everything as drafts and publish in one go.

Requires the three shas from `diff_refs` collected in Step 2 of `mr-flow.md`.

**Positioning:** added or modified line → `new_line` + `new_path`. Removed
line → `old_line` + `old_path`. Always `position_type: "text"`.

```bash
# 1. one draft per finding
glab api --method POST "projects/:id/merge_requests/<iid>/draft_notes" \
  --field "note=<body in markdown>" \
  --field "position[base_sha]=<base_sha>" \
  --field "position[start_sha]=<start_sha>" \
  --field "position[head_sha]=<head_sha>" \
  --field "position[position_type]=text" \
  --field "position[new_path]=<path>" \
  --field "position[new_line]=<line>"

# 2. publish the batch — approved findings only; do not leave drafts dangling
glab api --method POST "projects/:id/merge_requests/<iid>/draft_notes/bulk_publish"
```

**Fallback:** if positioning fails (`line is out of bounds`, file outside the
current version's diff), do not insist — post it as a general MR discussion,
naming the file and line in the body:

```bash
glab api --method POST "projects/:id/merge_requests/<iid>/discussions" \
  --field "body=**<path>:<line>** — <body>"
```

Explain in the closing, in one sentence, that the fallback was used and why.

## Single summary comment (idempotent)

When the user wants a consolidated verdict instead of inline comments, use a
marker so repeated reviews never duplicate it. The marker remains
`<!-- mr-checker -->` for compatibility: notes already published on open MRs
carry it, and changing it would create a second comment instead of editing the
existing one.

```bash
# look for a previous note from this skill
glab api "projects/:id/merge_requests/<iid>/notes" \
  | python3 -c "import json,sys; print(next((n['id'] for n in json.load(sys.stdin) if '<!-- mr-checker -->' in n.get('body','')), ''))"
```

Found an id → `PUT .../notes/:id` (edit). Not found → `POST .../notes`
(create). Always end the body with:

```
<!-- mr-checker -->
```

## Approve

```bash
glab mr approve <iid>
```

With a critical security finding, confirm a second time first.

## Request changes

Requires you to be on the MR's reviewer list. Add yourself **preserving the
existing reviewers** — overwriting the list drops the other people from the
review:

```bash
# current reviewers + your user
glab api "projects/:id/merge_requests/<iid>" \
  | python3 -c "import json,sys; print(','.join(str(r['id']) for r in json.load(sys.stdin).get('reviewers',[])))"
glab api "/user" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])"

# resend the full list (current + you), never just your own id
glab api --method PUT "projects/:id/merge_requests/<iid>" \
  --field "reviewer_ids=<id1,id2,your_id>"
```

Then the request-changes state via GraphQL:

```graphql
mutation requestChanges($projectPath: ID!, $iid: String!) {
  mergeRequestRequestChanges(input: { projectPath: $projectPath, iid: $iid }) {
    mergeRequest { id }
    errors
  }
}
```

`mergeRequestRequestChanges` only exists on recent GitLab. Inspect the `errors`
array; if the mutation does not exist on the instance, do not improvise — tell
the user and offer to post the findings as inline comments instead.

## Never

- `glab mr merge` — merging is not a persona action, under any circumstances.
- `git push`, `git commit`, editing files — the fix belongs to the MR author.
- Printing a token, not even in an error log.
