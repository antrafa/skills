# Tutorials

Six walkthroughs. They differ by **where you are starting from**, not by difficulty — pick the row that describes your situation rather than reading them in order.

Each one uses a worked example whose domain needs no explanation, shows the commands you type, the documents that come out, and — the part that matters most — **where the agent stops and asks you**, because that is where the quality comes from.

## Which one

| Your situation | Tutorial | Example | Length |
|---|---|---|---|
| Just installed the skill, want proof it works | [**quickstart**](tutorials/quickstart.md) | Shared shopping list | 30 minutes |
| A new app, from idea to a monitored release | [**new-app**](tutorials/new-app.md) | Book club | The full path |
| Users will see each other's content | [**social-app**](tutorials/social-app.md) | Mini social network | Auth-heavy |
| The data lives behind someone else's API | [**external-api**](tutorials/external-api.md) | Transport timetables | No backend |
| An Expo project you already started | [**existing-project**](tutorials/existing-project.md) | Half-built workout journal | Adoption |
| An app already in the stores | [**legacy-app**](tutorials/legacy-app.md) | Time-clock app in Cordova | Migration |

**Start with quickstart if you have never run the skill.** Thirty minutes, no paid accounts, no backend. It ends at your first green step, and hands off to whichever row above actually describes your project.

## What every tutorial assumes

**A physical device.** A simulator proves nothing about fonts, shadows, permissions or push, and several checklist items cannot be ticked without real hardware.

**That you will answer questions.** The skill grills one question at a time, with a recommended answer to each, and it does not fill gaps — an unresolved answer becomes `UNDECIDED — ask before assuming` in a file, and later steps stop on it. Discovery and design are conversation, not configuration.

**That three markdown files are the state.** `docs/PRODUCT.md`, `docs/DESIGN.md` and `docs/BUILD-PLAN.md` in your project are the workflow's entire memory. No database, no hidden config. You can read them, edit them by hand, and review them in a pull request.

## Two entry points, not one

Everything above splits at a single question: **is your app in production?**

**No** — discovery interviews the product into existence. That is quickstart, new-app, social-app, external-api and existing-project.

**Yes** — inventory replaces the interview. A live app has a domain, users and links that outrank any interview, so the skill reads the code and the store listings and asks only about the gaps. That is [legacy-app](tutorials/legacy-app.md), and reading a from-scratch tutorial first will mislead you.

## Reference, once you are running

- [`COMMANDS.md`](COMMANDS.md) — every command: what it reads, what it refuses, what it produces
- [`../prompts/README.md`](../prompts/README.md) — all 59 prompts with a description each, and the reference build order
- [`../prompts/RULES.md`](../prompts/RULES.md) — the rules every prompt inherits. Worth reading once yourself; it is short.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — adding a prompt, or a vertical the library does not cover
