# Building a social app — accounts, a database, and other people's content

The path where the screens are the easy part. Once one member can see another member's content, the work is authentication, row-level authorization, moderation, consent and deletion — and each of those is a decision the agent will stop and ask you for rather than pick.

The example is **Muda**, a plant-swap community: members post cuttings they have spare, other members comment, and you follow the people whose plants you want. Vocabulary: `Member`, `Post`, `Comment`, `Follow`. That is the whole domain; everything interesting below is platform work. If you have not run the skill before, read [new-app.md](new-app.md) first for how the phases fit together — this tutorial covers only what this path adds.

> **Not your starting point?** [Thirty minutes and no accounts](quickstart.md) · [a complete app from scratch](new-app.md) · [the data is behind someone else's API](external-api.md) · [a project you already started](existing-project.md) · [an app already in the stores](legacy-app.md). Full index: [TUTORIALS.md](../TUTORIALS.md).

---

## Before you start

| | Why |
|---|---|
| A physical device, and a **second** signed-in device or account | Half the checklists on this path are two-party: block one member from the other, read another member's row and be denied, reset a password and watch the other session sign out. One device cannot prove any of them. |
| A real mailbox you control | Verification codes and password reset are verified end to end from a real email, not from a log line. |
| An auth provider project and a backend project | Clerk publishable key, or a Supabase project URL and anon key. The agent stops rather than stub a credential. |
| **A named person who will read reports, and a target time** | `content-moderation.md` asks for a name and a target. This is the prerequisite people arrive without, and it is not a technical one. |
| A published developer contact route | A store requirement for user-generated content, needed in the submitted build and reachable while signed out. |
| Whoever owns your privacy policy, and 40 minutes of attention | `privacy-consent.md` lists the policy owner as a prerequisite and invents no policy of its own. Discovery and design are conversation; answered distracted they produce a plausible product definition, which is worse than none. |

**Four things separate a social app that ships from one that gets rejected:** the auth decision made once and early; row-level authorization, which is not a later task; moderation, which is a store requirement rather than a feature; and consent before any SDK initializes, with deletion that deletes. Everything else — feed, detail, profile, comment box — is the shape covered in [new-app.md](new-app.md).

---

## Phase 0 and 1 — init and discovery

```bash
mkdir muda && cd muda && git init
```

```
/mobilekit:init
```

No `expo` dependency, so it asks whether to scaffold, whether this is a legacy app, or whether you are in the wrong folder. It writes `AGENTS.md` with the product sections marked `TBD`, because there is no product yet.

```
/mobilekit:discovery
```

Seven blocks, one question per message, each with a recommended default. Three of them decide this whole path.

**Block B — the central object.** The block that removes `Item` from forty files:

> **What is the real vocabulary? The 3–7 nouns you would use talking to a colleague, and how they relate.**
>
> — A Member writes many Posts. A Post has many Comments, each by a Member. A Member follows other Members.
>
> **Is any of this content authored by you, or created by users? Both?**
>
> — All of it is the members'. Nothing is curated.

That last answer is the one that pulls moderation into the plan. "Created by users" plus "another member can see it" is the trigger condition in `content-moderation.md`, and it does not care that you call them cuttings.

**Block D — data.** Question 14 is the pivot: *does content differ per user, or does everyone see the same content?* Answer it precisely, because it sets the moderation scope and the authorization policies:

> — Every Post has an owner. Posts are visible to any signed-in member; the feed is not public to the internet.

**Block E — identity.** *Do users need accounts at all? If yes: managed provider or your own backend? Which sign-in methods?* This is the auth decision, and the next section is about it.

**What you get:** `docs/PRODUCT.md`, under 100 lines. Abbreviated, with the lines that matter on this path:

```markdown
# Product Definition

## What this is
A community for swapping plant cuttings locally. · Audience: hobby growers · Stage: production

## Domain vocabulary
| Term | Meaning | Relates to |
|---|---|---|
| Member | A person with an account | writes Posts, Comments; follows Members |
| Post | A cutting offered for swap | belongs to Member, has many Comments |
| Comment | A reply on a Post | belongs to Post and Member |
| Follow | One Member following another | Member → Member |

Central object: Post
Content ownership: user-generated

## Data
Scenario: A new schema
Per-user data: yes — every Post and Comment has an owner
Visibility: Posts and Comments are readable by any signed-in Member; nothing is public
Offline: no

## Identity
Accounts: yes · Provider: Supabase Auth · Methods: email + password, Apple, Google
Roles: member; one admin who reads reports

## Capabilities
| Capability | Now | Later | Never |
|---|---|---|---|
| Media upload | x | | |
| Analytics & errors | errors now | analytics later | |
| Payments | | | x |
| Push | | x | |
| AI | | | x |
```

**The `Visibility` line is the answer that changes everything downstream.** Members-only means the feed is behind auth, every read path is policy-checked against the signed-in member, and moderation is in scope because members see each other. Change that one line to *public, signed out* and you change the cold-start route, the policies, the age rating, and what the store reviewer sees before signing in. This is why the line goes in `PRODUCT.md` and not in your head.

---

## The auth decision, once and early

`PRODUCT.md` Block E asks it. `plan` then has to choose between two mutually exclusive prompts and say why in one line. The logic the prompts actually carry is narrow, so do not expect a decision tree:

| Situation | What the library says |
|---|---|
| The app already uses Supabase | `auth-backend.md` recommends **Supabase Auth**: session refresh, email verification and password reset are already solved there, and hand-rolling them is where custom auth usually breaks. |
| A custom API | Allowed, but `auth-backend.md` will demand the real contract — endpoints, request and response shapes, token lifetimes. It will not assume `/api/auth/login`. |
| No backend of your own to speak of | `auth-clerk.md`, the managed path. In the exemplar's plan the one-line reason reads `managed, because there is no backend team here`. |

Muda uses Supabase for the database, so Supabase Auth wins on the recommendation above and `auth-clerk.md` Step 2 is skipped.

**But Step 1 of `auth-clerk.md` still runs, whichever provider you chose.** It is the auth UI, and it is provider-agnostic by design: Sign Up and Sign In routes in an auth group, only the fields your chosen methods need, social buttons styled and inert, a verification step with a 6-digit input if email verification is one of your methods, and — the part that matters — **inline error slots and a loading state on the primary button, built now**. The prompt says retrofitting those later means editing every screen again. The outcome is deliberately mocked: the primary button advances the flow so navigation is testable end to end before any provider exists.

`auth-backend.md` then wires that same UI, and instructs plainly: *do not change the designs*. Which is the point — swapping Clerk for Supabase Auth six weeks in is a change to one integration step, not a screen rewrite. Two things it insists on that are easy to skip and expensive to add: tokens in `expo-secure-store` and never AsyncStorage, which is unencrypted; and an explicit loading state while the session restores, so a signed-in member never sees a flash of the sign-in screen.

---

## Phase 2 — design, with signed-out states

```
/mobilekit:design
```

Same three steps as any app. Three questions bite harder here:

- **Where does the app open on cold start** — for a new user, a returning signed-in user, and a returning signed-out user. Three routes, three redirects someone forgets to write.
- **Which screens require authentication, and what happens when a signed-out member arrives via a link.** This is recorded because `deep-linking.md` needs it as an input. A shared Post link is the whole growth mechanism of an app like Muda, and it will be opened by people with no account.
- **Own profile or public profile.** `profile-screen.md` opens with it: *is this the user's own profile, a public profile others can view, or both? They are different screens with different privacy rules; do not build one and assume it covers the other.* Muda needs both, so `DESIGN.md` lists two screens.
- **The four states per core screen.** For the Feed, the error state is the one people get wrong: already-loaded posts stay on screen and the failure is retryable, rather than a blank rectangle where a working list used to be.

---

## Phase 3 — the plan, and where moderation comes from

```
/mobilekit:plan
```

59 prompts in, your steps out. The rule that matters on this path is in `workflow/plan.md`: steps a store submission requires stay in whatever the product is — including **`content-moderation` if users can publish anything other users see**, and `account-recovery` if the app has passwords. Neither is negotiable by preference.

`docs/BUILD-PLAN.md`, abbreviated:

```markdown
## Foundation
- [ ] dev-environment · media and permissions need a development build
- [ ] design-system
- [ ] domain-model
- [ ] ui-components
- [ ] app-shell · session gate and the three cold-start routes

## Platform
- [ ] auth-clerk · Step 1 only — provider-agnostic auth UI
- [ ] auth-backend · Supabase Auth, because the app already uses Supabase
- [ ] supabase
- [ ] react-query
- [ ] native-permissions

## Screens
- [ ] tab-navigation · Feed · Post · Profile
- [ ] list-screen · Feed
- [ ] detail-screen · Post, with Comments
- [ ] form-screens · new Post
- [ ] profile-screen · own account
- [ ] profile-screen · public Member profile
- [ ] account-recovery · the app has passwords

## Features
- [ ] media-upload · one photo per Post
- [ ] content-moderation · PRODUCT.md: Posts are member-visible user content
- [ ] deep-linking · shared Post links, signed-out arrival

## Release
- [ ] testing
- [ ] accessibility
- [ ] privacy-consent
- [ ] error-tracking
- [ ] security-review · the two-party checks, re-run on the release build
- [ ] store-compliance
- [ ] eas-build
- [ ] beta-and-review

## Skipped
| Step | Why |
|---|---|
| monetization, in-app-purchases, payments, ads | PRODUCT.md: payments = never |
| ai-features | PRODUCT.md: AI = never |
| analytics | PRODUCT.md: analytics = later |
| push-notifications | PRODUCT.md: push = later |
```

Compare that `content-moderation` line with the exemplar's, where it was *skipped* with the reason "Notes are visible only inside a private Club — confirm if that changes". Same prompt, opposite outcome, and the deciding input is one line in `PRODUCT.md`. The plan cites the reason either way, so in six months the entry reads as a decision rather than an oversight.

Note also that `content-moderation.md` names accounts as a prerequisite — reporting and blocking need an identity on both sides — so it cannot lead the plan even if you wanted it to.

---

## Row-level authorization is not deferrable

The paragraph to read twice. `domain-model.md` scenario A, step 4, is titled *Row-level authorization* and opens: **if any data is per-user, this is not optional and not deferrable.** For Postgres and Supabase it means RLS enabled on those tables with the policies written **in the same migration that creates them**, and it states the reason in one sentence: *a table with per-user data and no policy is a data leak, not a TODO.* You are also required to state plainly which tables are intentionally public.

Why it is that severe on this path: your app ships with `EXPO_PUBLIC_SUPABASE_ANON_KEY` compiled into the bundle. `RULES.md` §6 spells out that `EXPO_PUBLIC_*` is readable by anyone with the app, and `supabase.md` finishes the thought — *the anon key is in the bundle: without RLS, every row is readable by anyone who extracts it.* Not "readable by a determined attacker". Readable by anyone who unzips your app. Every Member row, every Post, every Comment, every Follow edge.

So the checklist item is not "RLS enabled". It is:

```
- [ ] RLS verified by attempting to read another user's row and being denied
```

You need the second account for that, and you have to actually run it. Ticking that box because the migration mentions `enable row level security` is the exact move this line exists to prevent: a policy that exists but grants everything looks identical from the inside of your own session. `domain-model.md`'s acceptance checklist adds the paper trail — *every per-user table has an enforced authorization rule, named in `docs/DOMAIN.md`*.

Two more things `domain-model.md` will stop and ask, both of which are authorization questions wearing schema clothes:

- **Which entities are per-user** (needing an owner column) versus shared or authored content. In Muda: all four.
- **An explicit `ON DELETE` decision per relation.** When a Member goes, what happens to their Posts, their Comments, and the Follow rows pointing at them? Cascade is a choice here, not a default, and it is the same question moderation and deletion ask again later from their own side.

And before any of it is written: *show the model and get approval before writing migrations*, presented as a table first. That review is the highest-leverage five minutes of the build, because schema is the most expensive thing to unwind.

---

## Moderation is a store requirement, not a feature

`content-moderation.md` is blunt about its trigger: *if any user can see content another user wrote, this prompt applies. It does not matter that the product calls it "comments", "a shared list", "notes on a booking" or "a display name — nobody will abuse that".*

And about its status: *not a feature request*. Apple's review guideline for user-generated content requires four things — a mechanism to filter objectionable content, a way to report, a way to block, and published developer contact details. An app with UGC and none of these is rejected, **and the rejection arrives after the build is submitted**.

This is the step readers resent most and need most: it buys nothing a member will praise, and it is the difference between submitting and shipping. Where it stops and asks:

- **What exactly is user-visible, and to whom** — public, scoped to a group, or private. Answered **per content type, not once for the app**: "a private journal with a public profile photo is still UGC." Muda answers scoped-to-signed-in-members for Posts and Comments, and public for display name and avatar.
- **Pre- or post-publication moderation.** Recommended default: publish immediately, remove on report — because a review queue "is a commitment to a shift rota disguised as a checkbox".
- **Who reviews a report, and within what time.** The prompt requires a name and a target: *"We'll look at it" with nobody named means reports accumulate unread and the next store review finds them.* The review surface can be a database view someone opens by hand — but the report must say plainly that it needs a named owner, because an unstaffed queue is worse than none: it looks handled.
- **What happens to a blocked member's content already on the blocker's screen** — hidden retroactively or only future content. "Blocking that leaves yesterday's abuse on screen is not a block."
- **What happens to published content when its author deletes their account** — deleted, anonymised, or retained as written.

What gets built, in short: report reachable from *every* surface showing member content, because "one missed surface is the one the reviewer taps"; a bidirectional block applied **at the query layer** so every list inherits it rather than each screen filtering by hand; and a moderation state on the entity — `visible | reported | hidden | removed` — living in `docs/DOMAIN.md` as a domain union, filtered **server-side**, because filtering in the client means the content was already delivered to the device. A boolean bolted on later cannot tell "hidden pending review" from "removed for cause", and every read path then guesses.

The checklist items that need a device and a second account:

```
- [ ] Report and block reachable from every surface that shows user content — walked one by one
- [ ] Blocking removes the blocked user's existing content from the blocker's view immediately, no refresh
- [ ] A submitted report lands somewhere a named person opens, and that person has opened it once
- [ ] A hidden item is absent from the API response, not just from the rendered list
- [ ] The developer contact route is live and reachable from a signed-out state
```

Because Muda has photos, `media-upload.md` hands off here explicitly: where uploaded media is shown to other users, `content-moderation.md` owns what happens next. Two of its own decisions are worth knowing before you reach it — files private with signed reads rather than a public bucket URL, which is "public forever, guessable, and outside every auth check the rest of the app enforces"; and **EXIF as a decision, not a default**, because GPS coordinates inside a shared plant photo are a location leak the member never agreed to. On a swap app the photo is taken at home, so that one is not hypothetical.

---

## Consent runs before analytics, and deletion is real

**Ordering.** `privacy-consent.md` runs *before* `analytics.md` and `error-tracking.md`, and the reason is mechanical: an SDK that starts collecting at launch has already collected — device identifier, IP, session — before any consent screen renders, and **that ordering is the violation**. Retrofitting a dialog in front of an already-initialized SDK does not undo it. The prompt goes further: importing the module at the top of a screen is often enough to start it, so the stored decision has to be read before the first paint, in the same root-layout gate as auth and theme hydration. A gate that resolves one frame late is a frame of collection. It states no legal thresholds and offers no legal advice; the basis for each purpose belongs to your counsel or privacy officer, and the prompt's job is making the app behave the way that basis says it does. Verification is a network capture on a real device — refuse consent on a fresh install and watch nothing leave, including on cold start, backgrounding and crash. The simulator's console cannot prove this.

**Deletion.** `profile-screen.md` asks it directly: *if the app has accounts and ships on the App Store, in-app deletion is required by Apple.* `store-compliance.md` repeats it as a required in-app mechanism — reachable without contacting support, and it must actually delete rather than just sign out. What gets built: double confirmation, an explicit statement of what is deleted, **a server-side action, never client-only**, and immediate sign-out afterwards. `privacy-consent.md` then points back at that same path for data-subject deletion rather than building a second one, and says why: two deletion paths means one of them will be forgotten and keep the data.

**And the decision nobody makes on purpose.** Two prompts ask the same question from opposite ends — `profile-screen.md` asks whether deletion deletes or anonymises and what happens to the member's content; `content-moderation.md` asks what happens to published content when its author deletes their account. The answer options are: deleted with them, anonymised, or retained as written. The consequence of not choosing is named: *orphaned posts attributed to a ghost account are the default nobody chose.* For Muda that means a swap thread where the person offering the cutting no longer exists and the comments still ask when they can collect. Decide it once, write it in `PRODUCT.md`, and let the `ON DELETE` decision in `domain-model.md` implement it.

---

## The ways a step stops on this path

| It says | Why | You |
|---|---|---|
| "`PRODUCT.md` records Post visibility as members-only. Confirm before I write the policies." | Every RLS policy and the entire moderation scope depend on this line. | Confirm, or change it — and know that changing it re-opens the plan. |
| "Here are the four entity tables and the relationships. Approve before I write the migration." | Schema is expensive to unwind, and the `ON DELETE` decisions are in it. | Read it properly. This is the five minutes that pays for itself. |
| "Blocked: this needs the Supabase project URL and anon key." | It will not invent a credential or stub one to keep moving. | Create the project, paste them. The box stays unchecked until a real query returns data. |
| "I need the `@supabase/supabase-js` docs for the installed major — the session storage adapter shape changed." | It read `package.json` and will not write setup from memory. | Paste the page, or save it under `docs/vendor/`. Anything there is read first next time, so the ask happens once. |
| "Who reviews a report, and within what target time? I need a name." | `content-moderation.md` requires a named owner; an unstaffed queue looks handled and is not. | Name someone. If nobody can be named, that is the finding, not a blocker to route around. |
| "RLS: not verifiable — I could not sign in as a second member." | Reported as **not verifiable** rather than passed; that third outcome is the honest one. | Make the second account and run it yourself. Do not tick it for the agent. |
| "What happens to a deleted member's Posts — deleted, anonymised, or retained?" | Asked by two prompts because both need the answer. | Answer once; it is written back to `PRODUCT.md`. |
| "Recommended default: publish immediately, remove on report. Confirm or change." | An option is a question. | Confirm, or commit to staffing a queue every day, weekends included. |

```
/mobilekit:status
```

```
Phase:      build
PRODUCT.md  ok · 1 UNDECIDED
DESIGN.md   ok
BUILD-PLAN  11/26 · next: content-moderation
Drift:      plan says supabase done, RLS not enabled on comments
Next:       /mobilekit:next
```

That `Drift` line is the most useful output in the tool: a ticked box whose work is not in the repo is a lie in a file. It tells you which side is wrong and leaves the fix to you.

---

## The four mistakes that cost the most on this path

**Leaving visibility vague in discovery.** "Sort of public, sort of not" produces an `UNDECIDED` that blocks `domain-model`, then `content-moderation`, then the age rating in `store-compliance`. One sentence in Block D or three steps stalled later.

**Treating RLS as a follow-up ticket.** The anon key ships in the bundle. Between the migration and the policy, every Member row in your database is readable by anyone who extracts the key from your app — and nothing in your own session will look wrong. There is no window where this is a TODO.

**Deferring moderation until "we have users".** The rejection arrives after submission, which is the most expensive moment to discover a missing report button, a one-way block, or a queue with nobody's name on it. Building it during the build costs a step; building it under a rejection costs the release date.

**Shipping error tracking before consent.** The SDK collects on import. Ordering is the whole control, and no dialog added afterwards undoes what already left the device. The plan puts `privacy-consent` before `error-tracking` for exactly this reason — do not reorder it to unblock a build.

---

## Where to look next

- [`COMMANDS.md`](../COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../prompts/README.md`](../../prompts/README.md) — all 59 prompts with a description each, and the reference build order
- [`../prompts/RULES.md`](../../prompts/RULES.md) — the rules every prompt inherits. §6, on what ships in the bundle, is the one this path lives on.
- [`prompts/6-features/content-moderation.md`](../../prompts/6-features/content-moderation.md) — read it before you plan, not when you reach it

**Next:** [new-app.md](new-app.md) for the phases in full, including ship and post-release, which this tutorial only touched. If some of your content comes from a source you do not control — a plant species catalogue, say — [external-api.md](external-api.md) covers the DTO-versus-domain split that `domain-model.md` scenario C requires.
