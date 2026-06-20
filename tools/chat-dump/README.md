# chat-dump

Reusable core tool: convert a Claude Code session transcript (`.jsonl`) into readable markdown,
filed into the (gitignored, local-only) `intake/chats/` so our conversations become recallable
source material.

It keeps the **human ↔ assistant text turns** and skips internal `thinking`, raw tool I/O, and
injected `<system-reminder>` blocks. No third-party dependencies (stdlib only).

## Usage
```bash
# dump the most recent session
uv run --no-project --python 3.12 tools/chat-dump/dump_chat.py --latest

# or a specific transcript
uv run --no-project --python 3.12 tools/chat-dump/dump_chat.py \
  /config/.claude/projects/-config-workspace/<session>.jsonl
```
Transcripts live in `/config/.claude/projects/-config-workspace/*.jsonl`.

## Automation (optional, next step)
A Claude Code **Stop hook** can run `--latest` at the end of every session so chats are dumped
automatically — "just dumped into intake," no manual step.
