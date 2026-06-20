# Constitution — Governing Principles

> Project-agnostic principles for how we build. Read alongside `CLAUDE.md`.
> Earned from real experience; revised deliberately (and logged) as we learn.
> **Roles:** **Visionary** (direction, curation, judgment) + **Lead Dev** (research, build, upkeep).
> When we adopt Spec Kit per project, these formalize via `/speckit.constitution`.

## 1. Ground in official sources — never invent
Build against real, fetched documentation from the source. No guessing, no memory-as-fact, no
workarounds dressed up as progress. If we can't verify it, we say so.

## 2. Build on what's proven
Reuse established, successful tools and skills before creating our own. Create only when nothing
good exists. Pull from GitHub and elsewhere rather than reinventing.

## 3. Proper over fast
Do it the way the creators intend, even if slower. Surface blockers honestly instead of papering
over them. A shortcut that hides missing setup is not progress.

## 4. Spec before code
Disciplined spec → plan → tasks → implement. No vibe-coding. Decisions get written down where
they'll be found again.

## 5. Separate core from projects
Core is reusable and project-agnostic. Projects are separate repos that consume core. Technology
choices live in projects; things move up into core only once proven reusable.

## 6. Persist knowledge (Karpathy LLM Wiki)
Markdown-in-git brain. Every meaningful change: ingest → update `index.md` → append `log.md`. So
nothing is forgotten and we never get lost in the weeds.

## 7. Safe, honest, and tidy
Confirm before irreversible or outward-facing actions. Report outcomes truthfully — if it failed or
was skipped, say so. Secrets never go in git.
