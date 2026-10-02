# Report Design — the default for HTML reports

The visual standard for every HTML page this skill generates: the control
report from `/alterego control`, and any other HTML report the user asks for
without naming a design. Which design applies — this one or the user's own
`DESIGN.md` — is decided in
[playbook-control.md](playbook-control.md#2-design).

## 1. Core principle

The report is a working tool: whoever opens it needs to find the number,
understand the criterion and trust the data. It should look **clear, built and
pleasant to read**, with no decoration that informs nothing.

Two clichés to avoid:

* **The "premium editorial"**: decorative serif (Playfair, Lora), off-white
  background, terracotta/forest-green accent, Roman numerals, a callout with a
  thick side border.
* **The "template dashboard"**: blue-purple gradient, colored icon in a little
  box, card floating on a shadow, emoji as a bullet.

Dry is a defect too. A page of nothing but text and thin rules makes the reader
dig for the information. Color, weight and grouping exist to guide the eye to
what matters.

## 2. Visual identity

**Light mode, always.** White background, no automatic dark mode. The report
travels by e-mail, meeting and shared screen, and must look the same everywhere.

**A palette in shades of blue.** One tonal scale of the same blue does
everything: section background, table header, proportion bar, link, highlight
number. Light shades are surfaces and dark shades are text and data. That is
what gives the page unity without needing a second color.

| Token | Hex | Use |
|---|---|---|
| `--blue-50` | `#F2F6FD` | section surface, note background |
| `--blue-100` | `#E1EAFA` | table header, bar track |
| `--blue-200` | `#C3D4F4` | highlight border, section divider |
| `--blue-500` | `#2F5FD0` | data bar, active chip |
| `--blue-700` | `#1D3F94` | link, highlight number |
| `--blue-900` | `#0F2152` | title, emphasis text |
| `--ink` | `#1A2233` | body text (a neutral pulled toward blue) |
| `--muted` | `#5B6478` | secondary text, caption |
| `--line` | `#DCE2EC` | common border and divider |
| `--bg` | `#FFFFFF` | page background |

Pure gray stays out. The neutrals carry a touch of blue so they talk to the
palette. Semantic color (ok, attention, critical) stays separate from the blue
scale and only appears when the data really is a state: green `#1F7A4D`, amber
`#A15C00`, red `#B42318`.

**Shape.** 6px radius on section blocks, chips and tiles; 4px on inputs and
buttons. No floating shadow. Separation comes from a tonal surface
(`--blue-50`) and a 1px border. No gradients.

## 3. Typography

One sans-serif family with its monospaced sibling: **IBM Plex Sans** and **IBM
Plex Mono**, loaded from Google Fonts, with `system-ui` and `Menlo` as
fallback. Hierarchy comes from weight, size and color, never from switching
family.

* **H1**: 1.75rem/700, `--blue-900`, `text-wrap: balance`.
* **H2**: 1.15rem/600, `--blue-900`, with a short supporting line in `--muted`
  right below explaining what the section answers.
* **Body**: 0.95–1rem/400, `line-height: 1.55`, up to ~70 characters per line.
* **Label** (eyebrow, small column header): 0.72rem/600, uppercase,
  `letter-spacing: .06em`, `--muted`.
* **Data** (metric, code, path, ID): Plex Mono with
  `font-variant-numeric: tabular-nums`. It is the only place the family
  switches, and the switch says something: this is data, not prose.

## 4. Components

### Header
Full-width band in `--blue-50`, with a bottom border in `--blue-200`. Inside it
go a context label (team, date, data source), the title and one sentence saying
what the page answers. It is not a hero: its height follows the content.

### Highlight numbers
When the report exists to answer a number, open with 2 to 4 tiles: large value
in Plex Mono `--blue-900`, label above and a context line below ("46% of the
total"). The tile has a white background, a 1px `--line` border and the
standard radius. If the number is not the point of the page, do not use tiles.

### Tables
The header has a `--blue-100` background and weight 600, no forced uppercase.
Rows are separated by a 1px `--line` border, and row hover uses `--blue-50`.
Numbers are right-aligned in Plex Mono. When a column is a proportion, pair the
number with a thin horizontal bar: track in `--blue-100`, fill in `--blue-500`.

### Chips
A short label to classify an item (signal, status, type), at 0.75rem/600 with
`2px 8px` padding and the standard radius. The default variant has a
`--blue-100` background and `--blue-700` text. The strong variant has a
`--blue-500` background and white text, and is reserved for the state that
matters most. Never use emoji.

### Notes and alerts
A block in `--blue-50` with a 1px `--blue-200` border, opening with a text
label in weight 600 (`NOTE —`, `CRITERION —`, `RISK —`). For risk, switch to
the matching semantic color. No thick side border.

### Long lists
Group by category in a collapsible `<details>`, with the count next to the
title. Each item carries the main data on the left and the metadata (date,
chips) on the right, aligned.

### Text lists
Default bullet (`•`), no Roman numerals. Use numbering only when the order is
information. Spacing between items is 6–8px.

### Layout
A `max-width: 960px` column, a minimum 16px side gutter and sections separated
by 40px. Inside each section the information is dense: the breathing room
separates one unit from the next, it does not inflate the item. At phone width
(~400px), tiles and columns stack, and a wide table scrolls inside its own
container.

## 5. Checklist before delivering

* The number that answers the question shows without scrolling the page.
* Every number comes with the criterion that produced it, visible on the page.
* No color appears only as decoration: every blue marks a surface, data or an
  action.
* The page opens legible in light mode and prints to PDF from the browser.
