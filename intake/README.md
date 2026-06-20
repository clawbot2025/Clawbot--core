# intake/ — Raw dump (pre-triage)

Karpathy's **raw sources** layer — the "junk drawer." Drop anything collected here freely:
candidate repos, links, skills/tools to evaluate, half-ideas. **No judgment at drop time.** Messy on
purpose. Nothing here is curated or trusted yet.

## Triage (how things leave intake)
For each item ask: *relevant? proven/quality? what is it?* → then **promote or drop**:
- reference doc → `../docs/`
- skill → `../skills/`
- tool → `../tools/`
- synthesized knowledge / idea → `../memory/`
- not useful → delete it from intake

Then append to `../log.md` and update `../index.md`.

## Keep the repo clean
Lightweight items (links, notes, candidate lists) are tracked here. Heavy clones staged for evaluation
go in `intake/clones/`, which is **gitignored** so third-party code never bloats the core repo.
