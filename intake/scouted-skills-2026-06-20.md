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

## Parked
- safishamsi/graphify (code knowledge graph — later, for big codebases). Multi-agent harnesses (e.g. ruvnet/ruflo — premature).
