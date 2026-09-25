# Idea file format

One living file per idea at `./ideas/<slug>.md`, `<slug>` in kebab-case from the
refined problem, not from the proposed product. Created when EXPLORE closes,
updated at the end of every phase. Headings are translated to the user's
language; the structure is fixed.

```markdown
# <working title>

Class: <business | internal product | personal project> · Phase: <current> · Updated: <YYYY-MM-DD>

## Original idea
<the user's sentence, verbatim>

## Real problem
<one sentence, no solution inside>

## Target audience
<a specific, findable group>

## Job to be done
When <situation>, I want to <motivation>, so I can <expected outcome>.

## Current evidence
- <item> — strong / weak / none

## Current workaround
<what the audience does today>

## Risks and assumptions
| Assumption | Lens (D/V/F) | Importance | Evidence |
|---|---|---|---|
**Riskiest:** <assumption> — <why>
**Pre-mortem:** <failure story, past tense>
**Doing nothing:** <consequence>
**Contradictions:** <tension between answers | none found>

## Solution hypothesis
Options considered: <option> · <option> · <option, non-software>
We believe <solution> will <outcome> for <audience>.

## Differentiator
<why they switch from today's workaround>

## Refined version
<one paragraph>
**Out of v1:** <item — reason>

## Alternatives and competitors
- <name> — <what it does, price> — <link, date> | hypothesis — to verify

## Fit signals
- <signal> — current evidence: strong / weak / none

## Monetization
<who pays, how much, why that price>

## Next tests
We believe <hypothesis>. To verify, we will <test>. We measure <metric>.
We are right if <numeric criterion> by <date>.

## Recommendation
<go | pivot | stop> — <condition tied to the first test>

## Decision log
- <YYYY-MM-DD> — <decision> — <reason>
```

Fields not reached yet stay out of the file; a field reached but unanswered
reads `hypothesis — to verify`. Only `business` has the *Monetization* block.
