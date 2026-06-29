#!/usr/bin/env python3
"""write_script — the cheap 'writer' turn of the loop. Claude HAIKU drafts one
short-form script in the channel's voice. Outputs script.txt + meta.json.

Usage: write_script.py --brief brief.txt --out DIR [--recent recent.txt] [--topic "..."]
Reads ANTHROPIC_API_KEY from operations/.secrets/.env. Model: claude-haiku-4-5 (cheap).
"""
import json, os, sys, argparse, urllib.request

KEYCHAIN = os.environ.get("KEYCHAIN", "/config/workspace/operations/.secrets/.env")
MODEL = os.environ.get("WRITER_MODEL", "claude-haiku-4-5")

def key(name):
    for ln in open(KEYCHAIN):
        if ln.startswith(name + "="): return ln.split("=", 1)[1].strip()
    raise SystemExit(f"missing {name}")

def anthropic(system, user, max_tokens=1200):
    body = json.dumps({"model": MODEL, "max_tokens": max_tokens,
                       "system": system, "messages": [{"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST",
        headers={"x-api-key": key("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    return "".join(b.get("text", "") for b in d["content"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--recent", help="file of recently-used titles/topics to avoid")
    ap.add_argument("--topic", help="force a specific topic")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    brief = open(a.brief).read()
    recent = ""
    if a.recent and os.path.exists(a.recent):
        recent = "\n\nDO NOT repeat these recent topics:\n" + open(a.recent).read()
    ask = ("Write today's video." + (f" Topic to cover: {a.topic}." if a.topic else
           " Choose a fresh, specific, high-retention smart-money principle.") + recent +
           "\n\nRespond with ONLY the JSON object, no preamble.")
    raw = anthropic(brief, ask)
    s = raw[raw.find("{"): raw.rfind("}") + 1]
    obj = json.loads(s)
    open(f"{a.out}/script.txt", "w").write(obj["script"].strip() + "\n")
    json.dump({"title": obj["title"], "keyword": obj["keyword"]}, open(f"{a.out}/meta.json", "w"))
    if a.recent:
        with open(a.recent, "a") as f: f.write(obj["title"] + "\n")
    print(f"[written] {obj['title']}  (keyword {obj['keyword']})")
    print("----\n" + obj["script"].strip())

if __name__ == "__main__":
    main()
