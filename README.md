# Core

The shared knowledge base and infrastructure layer for all projects — a markdown "second brain"
in git, following [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

It collects (and creates) reusable **skills**, **tools**, and official **reference docs**, and remembers
**decisions**, so that projects like AutoTube plug into a solid foundation instead of starting from scratch.

**Start here:** [`CLAUDE.md`](./CLAUDE.md) (the schema/operating manual) → [`index.md`](./index.md) (the catalog).

```
core/
├── CLAUDE.md   # schema: structure, conventions, operations (read first)
├── index.md    # catalog of everything (read second)
├── log.md      # append-only decisions & activity
├── skills/     # reusable Claude Code skill packs
├── tools/      # scripts / CLIs
├── docs/       # raw official reference (e.g. docs/heygen/)
├── memory/     # wiki notes (decisions, concepts, how-tos)
└── projects/   # builds that consume this core (e.g. projects/autotube/)
```
