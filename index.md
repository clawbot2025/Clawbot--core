# Index — Core Knowledge Base

> Read this after `CLAUDE.md`. A one-line catalog of everything here. Updated on every ingest.

## ▶ Current status
- **Foundation:** Karpathy core structure + `constitution.md` (governing principles) in place.
- **Toolchain:** uv 0.11.23 + Python 3.12.13 installed (user-space, no root).
- **Spec Kit:** decided — adopt at the *project* layer when we build the first project; not installed yet.
- **Next:** collect/create the first reusable skills & tools (and resume AutoTube as its own repo when ready).

## Foundation docs
- `CLAUDE.md` — schema / operating manual (how the wiki works).
- `constitution.md` — governing principles for how we build.

## Skills
- _(none yet)_ — see `skills/`

## Tools
- _(none yet)_ — see `tools/`

## Docs (raw reference for core tooling)
- _(none yet)_ — see `docs/` (e.g. uv, Spec Kit, Claude Code)

## Memory (wiki notes)
- _(none yet)_ — see `memory/`

## Projects (separate repos that consume this core)
- **clawbot-autotube** — AI-news YouTube pipeline. Paused; resume after the foundation is solid.
  Its HeyGen/YouTube research is parked for that repo, kept out of core on purpose.

## Key decisions (full history in `log.md`)
- Build the reusable foundation before any project.
- Foundation follows Karpathy's LLM Wiki pattern.
- Core stays project-agnostic; projects are separate repos that consume it.
- Spec Kit: adopt at the project layer, when we build a project (not bolted onto core).
