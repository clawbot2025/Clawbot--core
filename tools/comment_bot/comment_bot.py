#!/usr/bin/env python3
"""comment_bot — watch a video's comments for a keyword, auto-reply the funnel link.
Idempotent (won't reply twice) and rate-aware. Uses the channel's youtube.force-ssl token.

Usage: comment_bot.py --video VIDEO_ID --keyword WORD --link URL [--state FILE] [--dry-run] [--max N]
"""
import json, os, argparse, time
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = os.environ.get("YT_TOKEN", "/config/workspace/autotube/.secrets/youtube_token.json")
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def creds():
    d = json.loads(Path(TOKEN_FILE).read_text())
    c = Credentials(token=d.get("token"), refresh_token=d["refresh_token"],
                    token_uri=d.get("token_uri", "https://oauth2.googleapis.com/token"),
                    client_id=d.get("client_id"), client_secret=d.get("client_secret"),
                    scopes=d.get("scopes", SCOPES))
    if not c.valid:
        c.refresh(Request()); Path(TOKEN_FILE).write_text(c.to_json())
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--keyword", required=True)
    ap.add_argument("--link", required=True)
    ap.add_argument("--reply", default="Here you go, my friend \U0001f447 {link}")
    ap.add_argument("--state", default=None)
    ap.add_argument("--max", type=int, default=20, help="max replies per run (rate safety)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    state_file = a.state or f"/tmp/cb_{a.video}.json"
    replied = set(json.load(open(state_file))) if os.path.exists(state_file) else set()
    yt = build("youtube", "v3", credentials=creds(), cache_discovery=False)
    kw = a.keyword.lower()

    found = matched = sent = 0
    page = None
    while True:
        resp = yt.commentThreads().list(part="snippet", videoId=a.video,
                                        maxResults=100, order="time", pageToken=page,
                                        textFormat="plainText").execute()
        for item in resp.get("items", []):
            found += 1
            top = item["snippet"]["topLevelComment"]
            cid = top["id"]
            text = top["snippet"]["textOriginal"]
            author = top["snippet"]["authorDisplayName"]
            if kw not in text.lower() or cid in replied:
                continue
            matched += 1
            msg = a.reply.format(link=a.link)
            if a.dry_run:
                print(f"[dry] would reply to {author!r} ({cid}): {msg}")
            else:
                yt.comments().insert(part="snippet",
                    body={"snippet": {"parentId": cid, "textOriginal": msg}}).execute()
                print(f"[replied] {author} ({cid})")
                replied.add(cid); sent += 1
                time.sleep(2)  # gentle pacing
            if sent >= a.max:
                break
        page = resp.get("nextPageToken")
        if not page or sent >= a.max:
            break
    if not a.dry_run:
        json.dump(sorted(replied), open(state_file, "w"))
    print(f"scanned={found} matched_keyword={matched} replies_sent={sent} (dry_run={a.dry_run})")

if __name__ == "__main__":
    main()
