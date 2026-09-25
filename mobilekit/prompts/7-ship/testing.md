# Testing

Cover what breaking would actually hurt. A prototype needs almost none of this; anything handling money, auth, or user data needs the parts below.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md` and AGENTS.md first.

Set up testing for this app.

### Grill

- **What would be worst if it silently broke?** Payment, auth, data loss, the success action from `PRODUCT.md`. That list is the test scope. Coverage percentage is not a goal — a repo at 80% coverage with the checkout untested is untested.
- Is the stage in `PRODUCT.md` production or prototype? A prototype gets domain-logic tests and nothing else.
- Do tests run in CI, and does anything block on them?
- Is a test runner already configured? Check before installing one.

### Build, in this order — stop when the risk is covered

**1. Domain logic (highest value, cheapest)**

Pure functions: validation rules, calculations, state transitions, mappers from `domain-model.md`. No renderer, no mocks, fast. If domain logic is currently tangled into components, that is the finding — the extraction is worth more than the test.

**2. Critical component behavior**

Only for flows on the risk list. Test what the user experiences — a submit produces a call with the right payload, an error renders, a disabled button does not fire twice. Query by accessible role and text, not by test ids attached to implementation details, so a refactor does not fail a passing feature.

**3. One end-to-end path**

The success action from `PRODUCT.md`, on a real build. One reliable E2E test that runs is worth more than a suite that people learn to ignore. Ask before adding an E2E framework — it is real setup and real maintenance.

### Rules

- **Mock at the network boundary**, not in the middle of your own code. Mocking your own module tests the mock
- Deterministic: no real clock, no real network, no shared state between tests. A flaky test is worse than no test — it trains everyone to ignore red
- Test behavior, not implementation. A test that breaks on every refactor is friction, not safety
- Every bug that reaches a user gets a test reproducing it before the fix

### Done when

- [ ] Every item on the risk list has a test that fails when the behavior breaks — verified by deliberately breaking it
- [ ] The suite runs in CI and its result is visible
- [ ] Runtime is short enough that people run it locally
- [ ] No flaky test tolerated in the suite
- [ ] What is deliberately untested is stated, with the reason
