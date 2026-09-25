# Home Screen

The first authenticated screen. Its job is to get the user to `PRODUCT.md`'s success action.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Build the Home screen.

### Grill

- **What is the one thing a returning user comes here to do?** The screen is designed around that, and everything else is secondary. Get the answer before laying anything out.
- **Layout pattern — ask, do not choose:**
  - **A — Feed.** A scrollable stream of content. For social, news, and content apps.
  - **B — Dashboard.** Progress or status summary, then "continue where you left off", then secondary actions. For productivity, fitness, and learning apps.
  - **C — Grid.** Category filters and a grid of cards. For commerce and galleries.
  - **D — Actionable list.** Filtered list with row actions and a create button. For task and messaging apps.

  Recommend one in a line based on `PRODUCT.md`'s central object, then wait.
- Which entities from `DOMAIN.md` appear here, and where does each come from — store, server, or local content?
- What does a brand-new user with no data see? This is the most-skipped screen state and the first one real users hit.
- Personalization: does the greeting need the user's name, and does the content differ per user?
- Is there a design reference to attach?

### Build

- A header with whatever identity the pattern needs — user name and avatar from the auth provider, with a fallback for a missing avatar
- The confirmed pattern, composed from the components in `ui-components.md` rather than one-off views
- Data through the layer already chosen: React Query for server data, the store for local state, `data/` for authored content. Do not add a second fetching path here
- Names and labels from `DOMAIN.md` vocabulary
- Long lists rendered with a virtualized list, not a mapped `ScrollView`
- Pull-to-refresh where content can change server-side

### Every state, explicitly

The empty, loading, error, and populated states are decided in `DESIGN.md` — render those decisions, with skeletons matching the real layout and the `EmptyState` component from `ui-components.md`. One state is Home's own:

- **Partial** — one section failing must not blank the whole screen

### Done when

- [ ] A first-run user with zero data sees a useful screen
- [ ] The success action is reachable from here in one tap, or the reason it is not is stated
- [ ] Loading, empty, error, and populated all verified — including with the network off
- [ ] Scrolls smoothly with a large dataset on a physical device
- [ ] No hard-coded strings that should come from data
