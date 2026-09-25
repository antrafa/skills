# Playbook: Building Local Applications (`/alterego local-app`)

This playbook guides the design, scaffolding and implementation of complete,
modern, functional web applications that are **100% runnable locally on the
user's machine**.

---

## Invocation modes

```
/alterego local-app <idea>                (starts design and scaffolding in the current folder)
```

In Codex:
```
$alterego local-app <idea>
```

---

## Philosophy & core principles

1. **100% Local Execution:** The application runs on the user's machine without
   requiring cloud, Vercel, AWS or Docker. It works straight away with:
   ```bash
   npm install && npm run dev
   # and also
   npm run build && npm start
   ```
2. **Current Folder:** Scaffolding happens directly in the current working directory.
3. **Pragmatic Local Persistence:** If the application needs a database, use
   **SQLite** (via Prisma, Drizzle or `better-sqlite3`) or local files (JSON/Markdown on the filesystem).
4. **Simplest solution:** No microservices or unnecessary enterprise layers.
   The simplest solution that solves the problem well is the winner.

---

## Step 1: Interactive alignment (the 3 key decisions)

Before generating any code, the persona runs a quick alignment in 3 blocks
tailored to the user's idea:

### 1. Stack decision: Next.js Full-Stack vs. React + Router (Vite)
Present the pros and cons specific to the idea at hand:
- **Next.js Full-Stack (App Router):**
  - *Pros:* Native API routes/Server Actions, direct access to the filesystem and SQLite on the backend, excellent for apps that mix UI with local server logic.
  - *Cons:* Denser configuration, slightly longer build time.
- **React + Router (Vite SPA):**
  - *Pros:* Instant startup and HMR, extremely lightweight, ideal for purely client-side tools or ones that talk to existing local CLIs/APIs.
  - *Cons:* No built-in backend; if it needs endpoints or access to protected files, it will need a bridge or a mini-server.

### 2. AI decision (if the idea involves Artificial Intelligence)
Assess whether the idea calls for AI and question the strategy:
- **Option A — Local agents and models (Ollama, local CLI, subprocess, MCP):**
  - *Pros:* 100% offline, absolute data privacy, zero API cost.
  - *Cons:* Requires local machine resources (RAM/GPU), smaller or slower models.
- **Option B — Direct API keys (OpenAI, Anthropic, Gemini, Groq, etc.):**
  - *Pros:* Top-tier models (more intelligence and reasoning), very fast responses, no local hardware consumed.
  - *Cons:* Requires the user's own API key, token costs per call, requires an internet connection.
- **Option C — Integration with the current AI agent:**
  - Use of sidecars, MCP or a bridge to the active harness (Claude Code, Antigravity, Codex).

### 3. Interface & design direction decision
Present to the user:
1. **At least 3 visual styles adapted to the idea:**
   - *Example 1 (Minimalist / Editorial):* Strong typography, generous spacing, focus on content;
   - *Example 2 (Technical Dashboard / Monospace):* High data density, snappy micro-interactions, modern terminal style;
   - *Example 3 (Modern SaaS / Clean):* Elegant shadcn/ui components, soft cards, clear hierarchy.
2. **Mandatory requirement — Dark & Light Mode:**
   - Every application created must implement native support for dark and light themes with persistence (via `next-themes` or Tailwind classes) and a smooth toggle button.
3. **Recommended sources of inspiration:**
   - Actively suggest that the user visit two leading references to pick visual patterns:
     - [getdesign.md](https://getdesign.md/) — design guidelines, UI components and modern patterns.
     - [neuform.ai](https://neuform.ai/) — interface and design system inspiration for AI.

---

## Step 2: Scaffolding and construction

After the user validates the 3 decisions:

**Current docs before the file.** Check the current API of the chosen stack
(Next.js/Vite, shadcn/ui, Tailwind, `next-themes`, ORM) — see
[sources.md](sources.md#external-facts-carry-a-date). Scaffolding written from
memory goes stale before the first `npm install`.

1. **Mandatory UI stack:**
   - Tailwind CSS;
   - `shadcn/ui` (or components inspired by it for React);
   - `lucide-react` for icons;
   - Strict TypeScript (`strict: true`).
2. **File generation:**
   - Clear, lean structure (`src/app/`, `src/components/`, `src/lib/`, `src/types/`);
   - Dark/light theme configuration (`theme-provider.tsx`, `mode-toggle.tsx`);
   - Data schemas and working routes/actions;
   - README with direct startup instructions.

---

## Step 3: Validation and handoff

When the application is finished:
1. Verify that `npm install` and the build pass without type errors.
2. Deliver the formal handoff stating:
   - Commands to run: `npm install && npm run dev`
   - Local URL (e.g. `http://localhost:3000` or `http://localhost:5173`)
   - Core files created
   - Optional next steps (tests, new screens, deploy)
