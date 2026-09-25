# Mobile Ads

Ad-funded revenue via Google AdMob. Skip unless `PRODUCT.md`'s Monetization section names ads — an ad SDK in an app that does not need one is a consent prompt and a review question for nothing.

Prereqs: an AdMob account with the app registered; a development build (the native SDK does not run in Expo Go); `privacy-consent.md` run or planned, because ads do not initialize before consent resolves.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Integrate AdMob.

**Check the installed `react-native-google-mobile-ads` version and follow its docs** (RULES.md §3 · canonical: https://docs.page/invertase/react-native-google-mobile-ads) — the config plugin carries the AdMob app ids, and initialization has moved across majors.

### Grill

- **Which formats, where?** **A** — banners on list or home screens. **B** — interstitials at natural breaks. **C** — rewarded ads the user chooses to watch for something, pairing naturally with a credit balance. Recommended default: A or C only to start; interstitials are the format users review-bomb and stores police for placement.
- **What may an ad never sit next to?** Name this product's sensitive content now, not after a screenshot circulates.
- **Is the app in a kids or family category, or could it end up there?** Answer against the store category, not the intention — it flips the SDK into restricted configuration and constrains every format.
- **How many interstitials per session are acceptable?** Recommended default: a cap enforced in code, not a hope.

### Build

- The config plugin with both platforms' AdMob app ids; **test ad unit ids everywhere until release** — clicking real ads in your own app is how accounts get banned
- Initialization gated on the consent state from `privacy-consent.md`, with the tracking answer matching `store-compliance.md`'s declarations: refusal means non-personalized ads, never a blocked app
- One component per format with a real fallback — an ad that fails to fill collapses to nothing, not a grey hole in the layout
- Rewarded flow, where chosen: the reward granted only on the SDK's earned-reward event, and server-side when it feeds a credit balance (`in-app-purchases.md`)
- Placement honours the answers above: never on the paywall, never adjacent to a destructive action — a misclick that costs the user is a one-star review — and capped per session

### Done when

- [ ] Test ads render on a device in every chosen format, and a failed fill leaves no layout hole
- [ ] With consent refused, the app runs with non-personalized ads or none — verified on a device
- [ ] The data-safety and tracking declarations match what the SDK actually sends, per `store-compliance.md`'s network capture
- [ ] A rewarded ad grants exactly once, on the earned event; closing early grants nothing
- [ ] No real ad unit id present in a debug or preview build
- [ ] The interstitial cap holds across a session
