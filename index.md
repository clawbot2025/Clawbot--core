# Index — Core Knowledge Base

> Read this after `CLAUDE.md`. A one-line catalog of everything here. Updated on every ingest.

## ▶ Current status
- **Foundation:** Karpathy core structure laid (this repo, `clawbot-core`).
- **Toolchain:** uv 0.11.23 + Python 3.12.13 installed (user-space, no root).
- **Next:** add Spec Kit (process layer), then collect/create the first reusable skills & tools.

## Skills
- _(none yet)_ — see `skills/`

## Tools
- _(none yet)_ — see `tools/`

## Docs (raw reference for core tooling)
- _(none yet)_ — see `docs/` (e.g. uv, Spec Kit, Claude Code)

## Memory (wiki notes)
- _(none yet)_ — see `memory/`

## Projects (separate repos that consume this core)
- **clawbot-autotube** — AI-news YouTube pipeline. Paused; we return after the foundation is solid.
  Its HeyGen/YouTube research is parked for that repo, kept out of core on purpose.

## Key decisions (full history in `log.md`)
- Build the reusable foundation before any project.
- Foundation follows Karpathy's LLM Wiki pattern.
- Core stays project-agnostic; projects are separate repos that consume it.
