# Log — Append-only activity & decisions

> Format: `## [YYYY-MM-DD] <op> | <summary>`  (op = ingest | decision | query | lint | setup)
> Scope: **core only.** Project-specific decisions live in each project's own repo.

## [2026-06-20] decision | Build a reusable core before building projects
Visionary direction: collect/create reusable skills, tools, and reference docs so projects
plug into a solid foundation instead of being rebuilt from scratch.

## [2026-06-20] decision | Adopt Karpathy "LLM Wiki" pattern for the core
Markdown-in-git brain: raw sources + wiki + schema (`CLAUDE.md`), with `index.md` and `log.md`
for navigation. Source: gist 442a6bf… (file `llm-wiki.md`).

## [2026-06-20] decision | Keep core project-agnostic; projects are separate repos
Realization: AutoTube/HeyGen specifics had leaked into the core. Corrected. Core now holds only
reusable, project-agnostic assets. Projects (e.g. `clawbot-autotube`) are separate repos that consume
core; their tech choices and research live with them, promoted up only when proven reusable.

## [2026-06-20] setup | Installed toolchain (user-space, no root)
uv 0.11.23 + CPython 3.12.13 via uv. apt/sudo unavailable (no passwordless root); ffmpeg/git-lfs
deferred until a project needs them.

## [2026-06-20] decision | Adopt Spec Kit at the project layer; add core constitution
Assessed Spec Kit (github/spec-kit). Verdict: strong fit, but per-project build process, not a
knowledge base — adopt when we scaffold the first project. Pulled its "constitution" idea forward as
`constitution.md` (governing principles). Roles set: Visionary + Lead Dev.

## [2026-06-20] decision | Verified Karpathy gist verbatim; aligned core structure
Cloned the real gist (file `llm-wiki.md`) instead of trusting summarizers. It is an abstract pattern:
raw sources + wiki + schema; ops ingest/query/lint; nav `index.md` + `log.md`; "answers filed back."
Aligned our instantiation: added `intake/` (raw dump / pre-triage = "raw sources") and `outputs/`
(query results filed back); `memory/` stays as the wiki; `docs/` = vetted raw reference. Triage flow
written into `CLAUDE.md`. `intake/clones/` gitignored to keep third-party code out of the repo.

## [2026-06-20] ingest | First dumps into intake/
Filed two raw notes: `scouted-skills-2026-06-20.md` (GitHub scout of reusable skills/tools) and
`session-2026-06-20-context.md` (AutoTube end-goal + verified HeyGen v3/webhook research, mostly
project-bound for clawbot-autotube). Untriaged — organize into wiki/skills/tools and route project
material to the AutoTube repo next.
