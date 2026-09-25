# List / Feed Screen

A browsable collection of one entity, with search and filtering.

---

## Prompt

Read `RULES.md` (this library), `docs/PRODUCT.md`, `docs/DOMAIN.md` and AGENTS.md first.

Build the list screen.

### Grill

- **Which entity, and what is the default sort order?** Both from `DOMAIN.md`. A list with an arbitrary order is a list users cannot trust.
- Roughly how many records — tens, thousands, unbounded? This decides whether pagination is needed at all.
- **Does search filter locally or query the server?** Local only works when the full set is already loaded. Server search needs an endpoint and debouncing.
- Which filters are real, and are they single or multi-select? Take the values from the domain — not "All / Active / Archived" by default.
- Row actions: tap to detail only, or also swipe to delete/archive? Destructive swipe actions need confirmation or undo.
- Does the user create records from here (a floating button), or elsewhere?

### Build

- A virtualized list (`FlatList`, or `FlashList` if already installed — ask before adding it) with a stable `keyExtractor` from the entity id
- Pagination via end-reached with a footer loader, only if the dataset warrants it. Guard against firing repeatedly at the end of the data
- Pull-to-refresh where server data can change
- A row/card component in the shared UI folder: the fields that matter for scanning, truncated predictably, tapping through to the detail screen
- Search: debounced (~300ms), with a clear action, and a distinct "no results for this query" state that is not the same as "nothing here yet"
- Filter chips reflecting the real values, with the active state visible without relying on color alone, and a way to clear
- Data through the existing layer — the entity's query hook, store, or local content

### Every state, explicitly

The base states — empty, loading, error, populated — are decided in `DESIGN.md`; render them with skeleton rows matching the row layout and the `EmptyState` component from `ui-components.md`. A list adds three of its own:

- **Empty (filtered or searched)** — different copy from "nothing here yet", plus a clear-filters action
- **Loading more** — footer spinner that does not shift the layout
- **Refreshing** — the platform indicator, not a full-screen loader; already-loaded rows stay visible through an error

### Done when

- [ ] Scrolls smoothly through a large dataset on a physical low-end device
- [ ] Search and filters combine correctly, and clearing them restores the full list
- [ ] All six states verified, including offline
- [ ] "Nothing here yet" and "no results" read differently
- [ ] Pagination does not duplicate or skip rows, and stops cleanly at the end
- [ ] Swipe actions, if built, confirm or offer undo
