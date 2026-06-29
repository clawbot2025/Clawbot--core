#!/usr/bin/env python3
"""Turn an ElevenLabs alignment.json into a styled word-synced ASS subtitle file.

Usage: make_ass.py <alignment.json> <out.ass> [words_per_chunk=3]
The alignment JSON must have: characters[], character_start_times_seconds[], character_end_times_seconds[].
"""
import json, sys

src = sys.argv[1]
out = sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 3

align = json.load(open(src))
chars = align["characters"]
starts = align["character_start_times_seconds"]
ends = align["character_end_times_seconds"]

words = []
cur, cs, ce = "", None, None
for ch, s, e in zip(chars, starts, ends):
    if ch.isspace():
        if cur:
            words.append((cur, cs, ce)); cur, cs = "", None
        continue
    if cs is None: cs = s
    cur += ch; ce = e
if cur:
    words.append((cur, cs, ce))

def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"

events = []
for i in range(0, len(words), N):
    grp = words[i:i+N]
    events.append((grp[0][1], grp[-1][2], " ".join(w[0] for w in grp)))

# Colours are &HAABBGGRR. Yellow = R255 G255 B0 -> &H0000FFFF
header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,62,&H0000FFFF,&H000000FF,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,5,3,2,50,50,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(out, "w") as f:
    f.write(header)
    for st, en, text in events:
        f.write(f"Dialogue: 0,{fmt(st)},{fmt(en)},Cap,,0,0,0,,{text}\n")

print(f"words={len(words)} lines={len(events)} duration={ends[-1]:.2f}s")
