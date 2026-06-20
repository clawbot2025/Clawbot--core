# Log — Append-only activity & decisions

> Format: `## [YYYY-MM-DD] <op> | <summary>`  (op = ingest | decision | query | lint | setup)
> Scope: **core only.** Project-specific decisions live in each project's own repo.

## [2026-06-20] decision | Build a reusable core before building projects
Visionary direction: collect/create reusable skills, tools, and reference docs so projects
plug into a solid foundation instead of being rebuilt from scratch.

## [2026-06-20] decision | Adopt Karpathy "LLM Wiki" pattern for the core
Markdown-in-git brain: raw sources (`docs/`) + wiki (`memory/`) + schema (`CLAUDE.md`), with
`index.md` and `log.md` for navigation. Source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## [2026-06-20] decision | Keep core project-agnostic; projects are separate repos
Realization: AutoTube/HeyGen specifics had leaked into the core. Corrected. Core now holds only
reusable, project-agnostic assets. Projects (e.g. `clawbot-autotube`) are separate repos that consume
core; their tech choices and research live with them, and are promoted up only when proven reusable.
AutoTube research from this session is parked for the AutoTube repo when we resume it.

## [2026-06-20] setup | Installed toolchain (user-space, no root)
uv 0.11.23 + CPython 3.12.13 via uv. apt/sudo unavailable (no passwordless root); ffmpeg/git-lfs
deferred until a project needs them.

## [2026-06-20] decision | Adopt Spec Kit at the project layer; add core constitution
Assessed Spec Kit (github/spec-kit). Verdict: strong fit, but it is a per-project build process, not
a knowledge base — so adopt it when we scaffold the first project (AutoTube), not bolted onto core.
Pulled its "constitution" idea forward now as `constitution.md`: project-agnostic governing
principles (official-sources-only, build-on-proven, proper-over-fast, spec-before-code, core/project
separation, persist-knowledge, safe/honest/tidy). Roles set: Visionary + Lead Dev.
