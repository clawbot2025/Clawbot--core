#!/usr/bin/env python3
"""loop.py — one autonomous channel turn: cheap Haiku writer -> make_episode factory -> upload.
This is what the cron fires. Uploads UNLISTED by default (review before public).

Usage: loop.py --brief brief.txt --channel-dir DIR [--privacy unlisted|public] [--face-prompt "..."]
"""
import json, os, subprocess, sys, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
PY = ["uv", "run", "--python", "3.12", "python"]

def run(cmd, **kw):
    print("» " + " ".join(cmd[:6]) + ("…" if len(cmd) > 6 else ""))
    p = subprocess.run(cmd, **kw)
    if p.returncode: sys.exit(f"step failed: {' '.join(cmd[:4])}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True)
    ap.add_argument("--channel-dir", required=True)
    ap.add_argument("--privacy", default="unlisted")
    ap.add_argument("--face-prompt", default=None)
    a = ap.parse_args()
    a.channel_dir = os.path.abspath(a.channel_dir)
    a.brief = os.path.abspath(a.brief)
    eps = os.path.join(a.channel_dir, "episodes")
    os.makedirs(eps, exist_ok=True)
    n = 1 + len([d for d in os.listdir(eps) if d.startswith("ep")])
    EP = os.path.join(eps, f"ep{n:04d}")
    os.makedirs(EP, exist_ok=True)
    recent = os.path.join(a.channel_dir, "recent.txt")

    # 1) WRITE (cheap Haiku)
    run(PY + [f"{HERE}/write_script.py", "--brief", a.brief, "--out", EP, "--recent", recent])
    meta = json.load(open(f"{EP}/meta.json"))

    # 2) FACTORY (deterministic make_episode)
    ep_cmd = PY + [f"{HERE}/episode.py", "--script", f"{EP}/script.txt", "--out", EP, "--no-upload"]
    if a.face_prompt: ep_cmd += ["--face-prompt", a.face_prompt]
    run(ep_cmd)

    # 3) UPLOAD (unlisted by default) via the proven autotube uploader
    kw = meta["keyword"]; title = meta["title"]
    desc = f"{title}\n\nComment {kw} and I'll send you the free guide — link in bio."
    up = (f"import sys; sys.path.insert(0,'/config/workspace/autotube/src');"
          f"from autotube.publish.youtube import upload;"
          f"r=upload({json.dumps(EP+'/episode.mp4')}, title={json.dumps(title[:95])},"
          f" description={json.dumps(desc)}, tags=['smartmoney','money','finance'], privacy={json.dumps(a.privacy)});"
          f"print('UPLOADED', r['url'])")
    run(["env", "PYTHONPATH=/config/workspace/autotube/src"] +
        ["uv", "run", "--no-project", "--python", "3.12",
         "--with", "google-api-python-client", "--with", "google-auth", "--with", "google-auth-oauthlib",
         "python", "-c", up], cwd="/config/workspace/autotube")

    with open(os.path.join(a.channel_dir, "loop_log.txt"), "a") as f:
        f.write(f"{EP}\t{kw}\t{title}\n")
    print(f"[loop done] {title}")

if __name__ == "__main__":
    main()
