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
| `--side` | `#F6F8FB` | side menu background |

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

* **H1**: 1.85rem/700, `--blue-900`, `text-wrap: balance`. It is a sentence
  that answers the page's question ("Staging closed; production still has 6
  open items"), not the document's name.
* **H2**: 1.15rem/600, `--blue-900`, with a short supporting line in `--muted`
  right below explaining what the section answers.
* **Body**: 0.95–1rem/400, `line-height: 1.55`, up to ~70 characters per line.
* **Label** (eyebrow, small column header): 0.72rem/600, uppercase,
  `letter-spacing: .06em`, `--muted`.
* **Data** (metric, code, path, ID): Plex Mono with
  `font-variant-numeric: tabular-nums`. It is the only place the family
  switches, and the switch says something: this is data, not prose.

## 4. Components

### Page structure
Two columns: a fixed **side menu**, 264px wide in `--side` with a 1px `--line`
right border, and the content with a `max-width` of 1040px. The menu lists the
page's sections, with a count next to them when there is one. When the report
belongs to a set (one page per client, environment or module), the menu lists
the sibling pages instead, each with a minimal state indicator (two 8px
squares, one per dimension), and opens the current page's sections nested
under its own entry. What has no page yet shows in `--muted`, without a link,
with a short label ("next", "queued"). A deadline that governs the set sits at
the top of the menu, with the day count computed on load.

A single report — the control report among them — stays one self-contained
file, with its CSS inline. A set of reports shares **one stylesheet and one
menu script** (`assets/report.css`, `assets/nav.js`) that every page
references: the menu list and the look change in one place, never in a copy
per page.

### Top
No header band and no number boxes. From top to bottom:

* **Kicker** at 0.84rem/600 in `--blue-500` with the context (client, team,
  region) and, in `--muted`, the dates each piece of data was measured. Data
  more than a day old goes in amber ("production measured 10/13").
* **H1** as a sentence (see Typography) and a **lede** of up to three lines
  with the next milestone.
* **State bars**: one block with a 1px `--line` border, one row per dimension
  (environment, phase), each with a bar of N segments 8px tall — one segment
  per measured item, in the report's order — and a sentence beside it with the
  number in bold ("**6 open** · 1 contained only by the WAF"). A small legend
  below. When the per-item state is not known, the row carries a chip and the
  sentence, with no invented segments.

Numbers live inside sentences, not in tiles. The bar shows the shape of the
problem (where the open items are), and the sentence gives the count.

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

### Expandable list
For items with long evidence (the points of a scope, the findings of a
pentest): a grid with a `--blue-100` header and one `<details>` row per item,
with the number in mono, the name, one chip per dimension and an arrow that
turns when it opens. The open content sits on `--blue-50` as a definition
list (`Staging 10/14`, `Production 10/13`, `Missing`, `Criterion`). When
printing, everything is open.

### Next actions
A table with action, owner and when. An undefined owner shows as "To be
defined" in the semantic red; an immediate deadline in a red chip, today's in
amber. What the action blocks or depends on goes on a secondary line in
`--muted`, right under the action.

### Long lists
Group by category in a collapsible `<details>`, with the count next to the
title. Each item carries the main data on the left and the metadata (date,
chips) on the right, aligned.

### Text lists
Default bullet (`•`), no Roman numerals. Use numbering only when the order is
information. Spacing between items is 6–8px.

### Layout
Sections separated by 44px; inside each section the information is dense: the
breathing room separates one unit from the next, it does not inflate the item.
At phone width (up to ~900px) the menu becomes a short strip at the top with
only the entries that have a page, as pills, without the sections or the
legend; the state bars move their sentence below the bar, and a wide table
scrolls inside its own container. When printing, the menu disappears and the
content takes the page.

## 5. Language

The report is read by someone who does not master the subject. The language is
plain and still precise: the reader understands what is happening without
knowing the mechanism. Write in the user's language.

* **Plain word first.** Write "the security team's rule", not "the policy";
  "fingerprint", not "digest". A technical term stays only when it is the name
  the reader will meet again (in the tool, in the meeting), explained the first
  time it appears ("the `.gitlab-multi-image.yml` file, a note that tells the
  scanner where the image is"). When the user's language has a word for it,
  use that word instead of the English one.
* **Acronyms spelled out or swapped.** An acronym the reader would not say out
  loud gets replaced by the plain word; one they must learn is spelled out the
  first time ("merge request (MR)"). Team-internal acronyms and code names
  carry a short gloss too ("SMO, the works measurement system").
* **Situation before mechanism.** Explain with a scene the reader would live
  ("a developer opens an MR; the pipeline compiles and the MR is accepted"),
  with the before and the after. Numbers, tables and technical detail come
  after, as proof.
* **Every number says what it means.** "91 critical flaws, most of them
  inherited from the operating system", not "91 CVEs CRITICAL". The reader
  never has to work out whether a number is good or bad.
* **Machine identifiers live in the proof.** Pipeline, commit, project and
  ticket IDs, file paths and commands go in the **Proof** of a finding or in
  the activities' evidence. The title, the lede and "In short" carry only
  words.
* **"In short" right after the top.** Two or three paragraphs say what is
  being attempted, followed by two boxes side by side, **Today** and **After**
  (the second on `--blue-50`).
* **Findings in three parts.** In the expandable list, each finding's title is
  a sentence stating the fact ("Changing everyone's build at once would break
  37 projects") and, opened, **In plain words**, **Why it matters** and
  **Proof**.
* **Chips name the weight in plain words:** `blocks`, `careful`, `helps`,
  `works`, `ready`, `not started`, in the user's language. Severity codes
  (P1, HIGH) stay inside the proof.
* **Long explanation goes to a sibling page.** When the subject needs a
  glossary, a step-by-step flow and alternatives, add a "How it works" page to
  the set and keep on the main page only what changes the decision, with a
  link to it.
* **Short glossary** as a definition list, term on the left: one or two
  sentences per term, with the project's real example.
* **Decision with a recommendation.** Every open decision carries the
  recommendation on the same row, in one sentence.
* **Machine text at the end.** Commands, absolute paths and agent prompts go
  at the bottom of the page — the control report's handoff included; the
  beginning is for the person reading.
* Short sentences, active voice, concrete verbs; corporate jargon and filler
  words stay out.

## 6. Checklist before delivering

* The number that answers the question shows without scrolling the page,
  inside a sentence, not in a box.
* Every number comes with the criterion that produced it, visible on the page.
* No color appears only as decoration: every blue marks a surface, data or an
  action.
* The page opens legible in light mode and prints to PDF from the browser.
* In a set of reports, no page carries its own styles: everything comes from
  the shared stylesheet.
* Someone outside the subject understands the H1 and "In short" without
  opening another page, and meets no unexplained acronym or ID in them.
