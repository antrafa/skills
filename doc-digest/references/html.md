# `--html` mode

Generates the `.md` as usual and, in addition:

1. `<out>/<name>-digest.html`, next to the `.md`, with the same content as
   the template.
2. The diagram in `<pre class="mermaid">`, with Mermaid from
   `https://cdn.jsdelivr.net/npm/mermaid@12/dist/mermaid.min.js` and
   `mermaid.initialize({ startOnLoad: true })`. The major stays pinned: an
   unpinned URL lets a new major break every digest already generated.
3. The `[!WARNING]`, `[!IMPORTANT]` and `[!CAUTION]` alerts become textual
   labels in weight 600 — `WARNING —`, `IMPORTANT —`, `CAUTION —`, translated
   into the document's language (in Portuguese: `AVISO —`, `IMPORTANTE —`,
   `CUIDADO —`) — followed by the subtitle in normal weight, over a neutral
   `#F5F5F5` background spanning the block width.
4. Visual style follows `~/.claude/DESIGN.md`. When it is absent, use: one
   sans-serif font, monochrome with a single accent, 1px borders, no shadow,
   no sidebar. Width `max-width: 960px` in both cases, above the 720px for
   running text in DESIGN.md because the four-column matrix and the diagram
   need it.
5. In chat, show both paths and the command to open the HTML:
   `xdg-open <file>` (Linux) or `open <file>` (macOS).
