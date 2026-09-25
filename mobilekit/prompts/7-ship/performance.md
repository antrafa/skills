# Performance Pass

Run this before the first submission, and again whenever the app gains a heavy screen. A simulator on a developer laptop is the one environment where every app is fast — nothing measured there tells you what a user with a three-year-old Android holds in their hand.

Prereqs: a real low-end Android device, a release-mode build (development builds are slower in ways that mislead), and `docs/PRODUCT.md` to say which screen matters.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DESIGN.md` and AGENTS.md first.

Measure this app's performance on a real low-end device, fix what the numbers justify, and measure again.

### The rule this prompt exists for

**Measure, then fix, then measure again.** An optimization with no before-number is a guess that costs code — it adds a `memo`, a cache, a lazy import, and buys nothing you can prove. And the corollary: **fix what the user waits on, not what the profiler finds interesting.** A 40 ms function called once at startup is not the problem; the list that drops frames under the user's thumb is.

### Grill

- **What do you actually observe as slow, and on which device?** A real complaint ("the feed stutters on my old phone") beats a synthetic sweep. If there is no complaint, say so — then this pass is a baseline, not a fix.
- **Which screen matters most?** Default: the cold-start destination, plus the screen holding `PRODUCT.md`'s success action. Everything else waits.
- **What is the worst device the app must support?** Name the model. That device's numbers are the only ones that count; a flagship hides every problem this prompt is looking for.
- **Is there a budget worth committing to** — time to interactive, list scroll frame rate, JavaScript bundle size? Recommended default: cold start to interactive under 3 s and no dropped frames while scrolling, on the named device. Without a number this pass has no finish line and becomes permanent.
- Is anything here allowed to change behaviour to get faster — fewer items per page, images at lower quality, a screen split in two? That is a product decision, not an optimization.

### Build

Record a before-number for each area you touch. An area with no measurement gets no change.

**Startup**

- Inventory what runs before first paint: analytics, error tracking, purchases, push registration. Most SDKs do not need to initialize before the first screen renders — defer or lazy-init them and keep the ones that genuinely gate correctness
- Fonts and assets blocking the splash, a persisted store hydrating synchronously (see `zustand.md`), and a session check that gates rendering are the three usual holds
- Measure cold start on the named device — app killed, not backgrounded — and **separate the splash from time to interactive**. A splash held for two seconds hides the problem instead of fixing it

**Lists**

- Confirm virtualization is actually in effect. A `.map()` inside a `ScrollView` renders every row on mount and is the single most common cause of a stuttering feed; see `list-screen.md`
- Stable keys from domain ids, never the array index
- Row components that do not re-render when the parent does, and fixed or estimated item sizes so the list does not measure every row as it scrolls
- Images sized to their display box, not the source resolution

**Images**

- Served at display size rather than downloaded large and downscaled on device, cached between launches, with dimensions known before layout so nothing jumps when they arrive

**Re-renders**

- Find them with a profiler on the busiest screen instead of guessing. The usual causes: a context value recreated every render, a global store subscribed to as a whole where one field was needed, expensive work in render instead of derived once
- A `memo` added without a measurement is a `memo` that costs more than it saves — it adds a comparison on every render and a stale-props bug later

**JavaScript bundle**

- Inventory what is in it. Look for a dependency disproportionate to its use — a full date library for one format call, an icon set for four icons — and for anything shipped that no route can reach. Removing an unreachable dependency is the only optimization with no downside

**Animations and gestures**

- Running on the UI thread, per `animations.md`. Anything driven by React state per frame is a dropped-frame generator

**Network**

- Count the requests on the most important screen. Requests that could be one, requests fired on every focus that could be cached (`react-query.md`), and anything blocking paint that could stream or arrive after the first render

### Done when

- [ ] Cold start, the main screen's time to interactive, and list scroll measured on the worst supported device, in a release build, with before and after numbers recorded
- [ ] Every change traces to one of those measurements — no fix justified by instinct
- [ ] The busiest screen profiled for re-renders, and the causes named rather than blanket-memoized
- [ ] Time to interactive measured separately from the splash, and the splash is not covering a slow start
- [ ] The bundle inventoried, and anything unreachable removed
- [ ] Scrolling the longest list on the named device drops no frames the developer can see
- [ ] Any budget agreed in the Grill is either met, or the remaining gap is stated with what it would take to close
