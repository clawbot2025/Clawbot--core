---
type: intake
date: 2026-06-20
topic: scouted reusable skills/tools for the core
status: untriaged
---

# Scouted: reusable Claude Code skills/tools (2026-06-20)

> RAW candidates from a GitHub scout. NOT yet vetted/promoted. Caveat: star counts in the source
> environment were unreliable — judged on relevance + official/proven status. Triage later into
> `../skills/`, `../tools/`, or `../docs/` (or drop).

## Tier 1 — likely promote (proven / on-pattern)
- **anthropics/skills** — official Anthropic Agent Skills repo; authoritative source for skills. https://github.com/anthropics/skills
- **tobi/qmd** (MIT) — local markdown search engine (BM25/vector, CLI + MCP). Karpathy-recommended in the LLM-Wiki gist for searching our wiki. **Top pick for the CORE.** https://github.com/tobi/qmd
- **hesreallyhim/awesome-claude-code** — canonical curated index of skills/hooks/commands/plugins (a map to proven things). https://github.com/hesreallyhim/awesome-claude-code
- **VoltAgent/awesome-agent-skills** (MIT) + **awesome-claude-code-subagents** (MIT) — large curated skill/subagent libraries. https://github.com/VoltAgent/awesome-agent-skills

## Tier 2 — evaluate before trusting
- **affaan-m/ECC** (MIT) — "research-first" agent harness; philosophically aligned but heavy. https://github.com/affaan-m/ECC
- **multica-ai/andrej-karpathy-skills** — Karpathy-derived CLAUDE.md behavior (no license listed). https://github.com/multica-ai/andrej-karpathy-skills
- **rohitg00/agentmemory** (Apache-2.0) — benchmarked persistent memory; compare vs our markdown wiki. https://github.com/rohitg00/agentmemory

## Reference repos given by the Visionary (infrastructure design)
- **safishamsi/graphify** (MIT, YC S26, PyPI `graphifyy`, CLI `graphify`) — a "memory layer": maps a
  project (code, docs, PDFs, images, schemas) into a **queryable knowledge graph** so the agent queries
  the graph instead of re-reading files (token savings). Installs as a Claude Code skill (`graphify install`);
  output is per-project (`graphify-out/graph.json|html` + `GRAPH_REPORT.md`). Needs Python/uv (have it).
  **Fit:** complements our markdown wiki — wiki = *what was decided* (declarative); Graphify = *how the
  code is structured* (structural). A reusable **core skill**, but its value only kicks in on a real
  codebase. **Recommendation:** adopt/install at **AutoTube kickoff** (first real codebase); premature now.
  https://github.com/safishamsi/graphify

## Parked
- Multi-agent harnesses (e.g. ruvnet/ruflo) — premature.
