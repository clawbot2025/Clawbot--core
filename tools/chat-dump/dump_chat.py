#!/usr/bin/env python3
"""Dump a Claude Code session transcript (.jsonl) to readable markdown.

Reusable core tool. Extracts the human <-> assistant TEXT turns (skips internal
thinking, raw tool I/O, and injected <system-reminder> blocks) so a conversation
can be filed into intake/chats/ as recallable source material.

Usage:
  dump_chat.py <session.jsonl> [--out DIR]
  dump_chat.py --latest [--projects-dir DIR] [--out DIR]

No third-party dependencies (stdlib only). Run with:
  uv run --no-project --python 3.12 dump_chat.py --latest
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

DEFAULT_PROJECTS = Path("/config/.claude/projects/-config-workspace")


def text_of(content) -> str:
    """Join the human-visible text from a message's content (string or block list)."""
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts = []
    for b in content:
        if isinstance(b, dict) and b.get("type") == "text":
            tx = (b.get("text") or "").strip()
            if tx and not tx.startswith("<system-reminder>"):
                parts.append(tx)
    return "\n\n".join(parts).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="?", help="path to a session .jsonl")
    ap.add_argument("--latest", action="store_true",
                    help="use the most recently modified session in --projects-dir")
    ap.add_argument("--projects-dir", default=str(DEFAULT_PROJECTS))
    ap.add_argument("--out", default="intake/chats")
    args = ap.parse_args()

    if args.latest:
        pd = Path(args.projects_dir)
        sessions = sorted(pd.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not sessions:
            sys.exit(f"no .jsonl sessions in {pd}")
        src = sessions[0]
    elif args.jsonl:
        src = Path(args.jsonl)
    else:
        sys.exit("provide a .jsonl path or --latest")

    if not src.exists():
        sys.exit(f"not found: {src}")

    title = None
    first_ts = last_ts = None
    turns: list[tuple[str, str]] = []

    for line in src.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = obj.get("type")
        if t == "ai-title" and not title:
            title = obj.get("title") or obj.get("text")
        ts = obj.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        if t not in ("user", "assistant"):
            continue
        msg = obj.get("message") or {}
        role = msg.get("role") or t
        txt = text_of(msg.get("content"))
        if not txt:
            continue  # skips pure tool-result / tool-call / thinking-only turns
        turns.append((role, txt))

    if not turns:
        sys.exit(f"no text turns extracted from {src.name}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = (first_ts or "")[:10] or "session"
    out_path = out_dir / f"{stamp}-{src.stem[:8]}.md"

    head = [
        "---",
        "type: chat",
        f"session: {src.stem}",
        f"date: {stamp}",
        f"title: {title or '(untitled session)'}",
        f"turns: {len(turns)}",
        "status: untriaged",
        "---",
        "",
        f"# Chat — {title or src.stem[:8]}",
        f"_session {src.stem} · {first_ts or '?'} → {last_ts or '?'} · {len(turns)} text turns_",
        "",
    ]
    body = []
    for role, txt in turns:
        label = "🧑 User" if role == "user" else "🤖 Assistant"
        body += [f"## {label}", "", txt, ""]
    out_path.write_text("\n".join(head + body))
    print(f"wrote {out_path}  ({len(turns)} turns, {out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
