# Index — Core Knowledge Base

> Read this after `CLAUDE.md`. A one-line catalog of everything here. Updated on every ingest.

## ▶ Current status
- **Foundation:** Karpathy LLM Wiki pattern (verified verbatim) instantiated — schema + intake/wiki/outputs + index/log.
- **Toolchain:** uv 0.11.23 + Python 3.12.13 (user-space, no root).
- **Spec Kit:** decided — adopt at the *project* layer; not installed yet.
- **Next:** start collecting into `intake/`, then triage into `docs/` `skills/` `tools/` `memory/`.

## Foundation docs
- `CLAUDE.md` — schema / operating manual.
- `constitution.md` — governing principles.

## intake/ — raw dump (pre-triage)
- `scouted-skills-2026-06-20.md` — GitHub scout of reusable skills/tools (Tier 1/2). Untriaged.
- `session-2026-06-20-context.md` — AutoTube end-goal + verified HeyGen v3 research. Mostly project-bound → clawbot-autotube.

## docs/ — vetted raw reference (core tooling)
- _(none yet)_ — e.g. uv, Spec Kit, Claude Code.

## skills/
- _(none yet)_

## tools/
- _(none yet)_

## memory/ — the wiki
- _(none yet)_

## outputs/ — query results filed back
- _(none yet)_

## Projects (separate repos that consume this core)
- **clawbot-autotube** — AI-news YouTube pipeline. Paused; resume after the foundation is solid.

## Key decisions (full history in `log.md`)
- Build the reusable foundation before any project.
- Foundation follows Karpathy's LLM Wiki pattern (verified verbatim from the gist).
- Core stays project-agnostic; projects are separate repos that consume it.
- Spec Kit: adopt at the project layer, not bolted onto core.
