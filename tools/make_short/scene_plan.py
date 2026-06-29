#!/usr/bin/env python3
"""Cut a voiceover (ElevenLabs alignment.json) into ~5s scene beats for shot-based video.

Each scene = a contiguous run of words, broken at sentence boundaries, targeting ~TARGET sec
(hard cap MAXLEN sec so it fits a single image-to-video clip). Assigns a rotating camera-motion
preset per scene. Output: scenes.json -> [{idx,start,end,dur,text,motion}].

Usage: scene_plan.py <alignment.json> <out_scenes.json> [target_sec=5] [max_sec=6]
"""
import json, sys

src, out = sys.argv[1], sys.argv[2]
TARGET = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
MAXLEN = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0

a = json.load(open(src))
chars, starts, ends = a["characters"], a["character_start_times_seconds"], a["character_end_times_seconds"]

# words with timing
words = []
cur, cs, ce = "", None, None
for ch, s, e in zip(chars, starts, ends):
    if ch.isspace():
        if cur: words.append((cur, cs, ce)); cur, cs = "", None
        continue
    if cs is None: cs = s
    cur += ch; ce = e
if cur: words.append((cur, cs, ce))

# Higgsfield-style camera moves to rotate through (label only; map to real motion_id at call time)
MOTIONS = ["push-in slow", "arc left", "arc right", "pull-back reveal", "tilt up",
           "crane down", "dolly in", "slow orbit", "handheld drift", "rack focus"]

scenes, buf, bstart = [], [], None
def flush():
    if not buf: return
    txt = " ".join(w[0] for w in buf)
    st, en = buf[0][1], buf[-1][2]
    scenes.append({"idx": len(scenes), "start": round(st,2), "end": round(en,2),
                   "dur": round(en-st,2), "text": txt,
                   "motion": MOTIONS[len(scenes) % len(MOTIONS)]})

for w in words:
    if bstart is None: bstart = w[1]
    buf.append(w)
    dur = w[2] - bstart
    ends_sentence = w[0].rstrip('"\'').endswith(('.', '?', '!', ':'))
    if (dur >= TARGET and ends_sentence) or dur >= MAXLEN:
        flush(); buf, bstart = [], None
flush()

json.dump(scenes, open(out, "w"), indent=2)
total = scenes[-1]["end"] if scenes else 0
print(f"scenes={len(scenes)} total={total:.1f}s avg={total/max(len(scenes),1):.1f}s/scene")
for s in scenes:
    print(f"  [{s['idx']:2d}] {s['start']:5.1f}-{s['end']:5.1f} ({s['dur']:.1f}s) {s['motion']:14s} | {s['text'][:54]}")
