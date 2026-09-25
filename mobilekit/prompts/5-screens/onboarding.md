# Onboarding Screen

The first screen a new user sees.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Build the onboarding for this app.

### Grill

`PRODUCT.md` describes the first session. Confirm the pattern — **ask, do not choose**:

- **A — Single welcome screen.** Logo, app name, one-line value proposition, hero image, "Get Started", plus a sign-in link for returning users. Recommended default: fastest to value, and the one most apps should ship.
- **B — Multi-step carousel.** 3–4 swipeable slides selling features, pagination, skip. Only worth it when the value is genuinely non-obvious.
- **C — Interactive setup.** One question per screen collecting preferences, with progress indication, answers stored for later use. Choose this only if the app is unusable without those answers.

Then confirm:

- What is the value proposition, in the developer's own words? Do not write marketing copy for someone's product and present it as decided — draft it, label it a draft, and ask.
- Which assets exist (logo, mascot, illustration), and what should stand in for the ones that do not?
- Where does onboarding lead — sign up, sign in, or straight into the app if accounts are optional?
- For C: which answers are collected, and are they persisted locally or sent to the server? Those fields belong in `DOMAIN.md`.

### Build

- The confirmed pattern, using design system tokens only
- Persist a completed flag so it never shows twice; route past it on subsequent launches
- Plug the completed flag into the gate `app-shell.md` built, next to auth state, so a returning signed-in user never sees onboarding flash
- For C, store answers using the domain vocabulary from `DOMAIN.md`
- Restrained motion (fade or slide); honor reduced-motion

### Done when

- [ ] Shows once, then never again — verified across a restart
- [ ] Leads to the destination confirmed above
- [ ] No flash of onboarding for a signed-in user
- [ ] Renders correctly on a small screen and with a large system font
- [ ] Copy was approved, not invented

If a design reference exists, attach it and match it: `@path/to/onboarding-design.png`
