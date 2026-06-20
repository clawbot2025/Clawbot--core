# Core — Schema & Operating Manual

> This is the schema file for our core knowledge base, following Karpathy's "LLM Wiki" pattern
> (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
> **Read this first, then `index.md`.** It defines how this repo is structured and how I (the agent)
> maintain it so nothing gets lost between sessions.

## What this is
A versioned markdown "brain" — the foundation that projects plug into. It holds the reusable
**skills, tools, and reference docs** we collect or create, plus the **memory of decisions**, so that
building projects (e.g. AutoTube) starts from a solid base instead of from scratch.

## The three layers (Karpathy LLM Wiki)
1. **RAW SOURCES** — `docs/` — official documentation we fetch. Never invented, never "fixed." Immutable reference.
2. **THE WIKI** — `memory/` — atomic, interlinked notes the agent maintains (decisions, concepts, how-tos).
3. **THE SCHEMA** — this file (`CLAUDE.md`) — the conventions + workflows that keep the wiki disciplined.

## Directory map
- `CLAUDE.md` — this schema (read first).
- `index.md`  — catalog of everything; the table of contents (read second).
- `log.md`    — append-only chronological record of activity & decisions.
- `skills/`   — collected or created Claude Code skills (`SKILL.md` packs). Reusable capabilities.
- `tools/`    — scripts/CLIs we pull in or build.
- `docs/`     — RAW official reference for *core* tooling, by source (e.g. `docs/uv/`, `docs/spec-kit/`).
- `memory/`   — the wiki: atomic notes, decisions, concepts (Zettelkasten-style).

> **Core is project-agnostic.** Projects (e.g. AutoTube) are **separate repos** that *consume* this core —
> they are not stored inside it.

## Core vs. projects (separation principle)
- **Core** = what is reusable across projects: conventions, toolchain, skills, tools, and reference for
  that tooling. Project-agnostic.
- **A project** = its own repo, with its own specs, decisions, and project-specific docs. A project's
  technology choices (e.g. "use HeyGen") live in the **project**, never in core.
- **Promotion:** something starts in a project; only once it proves reusable do we promote it up into
  `core/skills` or `core/tools`. This keeps the foundation from getting tangled with any one project.

## Conventions
- Filenames: kebab-case (`heygen-webhooks.md`).
- Every `memory/` note has YAML frontmatter: `title, tags, created, updated, status, type`.
- Link notes with wikilinks `[[note-name]]`; link liberally.
- One idea per memory note (atomic).
- Anything derived from the web cites its source URL.
- `docs/` mirrors the source; if the source changes, re-fetch and note it in `log.md` — don't hand-edit to "correct."

## Operations (Karpathy: ingest / query / lint)
- **INGEST** — when new material arrives (a fetched doc, a decision, a skill): file it, update `index.md`, append a line to `log.md`.
- **QUERY** — to answer or build: read `index.md` first, then the relevant `docs/` + `memory/` pages, then only the raw artifacts you need.
- **LINT** — periodically check for contradictions, stale claims, orphan pages, and missing cross-links.

## Navigation rule (how I avoid getting lost)
At the start of work: read `CLAUDE.md` → `index.md` → recent `log.md` entries → the specific pages named there.
Don't re-derive what's already written; update it instead.

## Build order for the foundation
1. **Karpathy core structure** (this).  ← we are here
2. **Toolchain** (uv + Python) — done.
3. **Spec Kit** (process layer) + skills/tools collection.
Projects (AutoTube, etc.) come after the foundation is solid.
