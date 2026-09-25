# Diagram skeletons

Starting points for the diagrams in SKILL.md's *Diagram rules* table whose
syntax is less common. Each skeleton was validated with mermaid-cli 12; keep
its shape and replace the content. Cite `L<n>` inside a label only when it
fits in a few words.

## Mind map: what is settled, what is open

Root = the subject. The three branches are fixed and translated with the
digest; drop a branch with no content.

```mermaid
mindmap
  root((Subject))
    Decided
      Choice A L27
    Open
      Question still unanswered
    Discarded
      Option B L23
```

No `classDef` and no legend: branch position already says what each item is.

## Ishikawa: why did it happen

Causes grouped by category, all converging on the effect. Categories fit
software: People, Process, Technology, Environment, and Data when data is in
play. Keep only the categories with causes the text states.

```mermaid
flowchart LR
  subgraph Process
    R1["Rollback never tested (L40)"]
  end
  subgraph Technology
    T1[Connection pool fixed at 10]
  end
  R1 --> E
  T1 --> E
  E(["Effect: API down for 40 min"])
```

Legend: "boxes = causes grouped by category · rounded = effect".

## Concept map: how the ideas relate

Every edge carries a verb, so each arrow reads as a sentence
("Process receives Entry").

```mermaid
flowchart LR
  Process -- receives --> Entry
  Entry -- "opens (L13)" --> Deadline
```

## Quadrant: which option wins on two criteria

Only when the text itself ranks options on two criteria; positions follow
what the text says, as `[x, y]` between 0 and 1.

```mermaid
quadrantChart
  x-axis Low effort --> High effort
  y-axis Low gain --> High gain
  quadrant-1 Plan
  quadrant-2 Do now
  quadrant-3 Skip
  quadrant-4 Avoid
  Option A: [0.2, 0.6]
  Option B: [0.7, 0.8]
```
