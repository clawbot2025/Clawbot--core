#!/usr/bin/env bash
# make_short — generate a faceless 9:16 short from a script, end-to-end.
#
# Pipeline (each step proven 2026-06-25, see operations/outputs/proof-short/RECIPE.md):
#   script.txt -> ElevenLabs voice+timestamps -> word-synced captions (ASS)
#   -> AI image (Pollinations/Flux) -> ffmpeg (Ken Burns + vignette + captions + ambient bed)
#   -> short.mp4 (720x1280)
#
# Usage:
#   make_short.sh --script FILE --image-prompt "..." --out DIR \
#                 [--voice VOICE_ID] [--no-music] [--reuse] [--words-per-cap N]
#
# Env/deps: curl, jq, uv (for python), a static ffmpeg (set $FFMPEG, default /tmp/ffmpeg).
# Keys: ELEVENLABS_API_KEY from operations keychain (override $KEYCHAIN).
set -euo pipefail

VOICE="JBFqnCBsd6RMkjVDRZzb"        # George — British storyteller
KEYCHAIN="${KEYCHAIN:-/config/workspace/operations/.secrets/.env}"
FFMPEG="${FFMPEG:-/tmp/ffmpeg}"
HERE="$(cd "$(dirname "$0")" && pwd)"
MUSIC=1; REUSE=0; WPC=3; SCRIPT=""; IMGPROMPT=""; OUT=""

while [ $# -gt 0 ]; do case "$1" in
  --script) SCRIPT="$2"; shift 2;;
  --image-prompt) IMGPROMPT="$2"; shift 2;;
  --out) OUT="$2"; shift 2;;
  --voice) VOICE="$2"; shift 2;;
  --no-music) MUSIC=0; shift;;
  --reuse) REUSE=1; shift;;            # reuse existing voice.mp3/alignment.json/image.png if present
  --words-per-cap) WPC="$2"; shift 2;;
  *) echo "unknown arg: $1" >&2; exit 2;;
esac; done

[ -n "$SCRIPT" ] && [ -n "$OUT" ] || { echo "need --script and --out" >&2; exit 2; }
mkdir -p "$OUT"
command -v "$FFMPEG" >/dev/null 2>&1 || [ -x "$FFMPEG" ] || { echo "ffmpeg not found at $FFMPEG (set \$FFMPEG)" >&2; exit 1; }

# Anton font for captions
FONTS="${FONTS:-/tmp/fonts}"; mkdir -p "$FONTS"
[ -f "$FONTS/Anton-Regular.ttf" ] || curl -sL "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf" -o "$FONTS/Anton-Regular.ttf"

XI="$(grep '^ELEVENLABS_API_KEY=' "$KEYCHAIN" | cut -d= -f2-)"

# 1) Voice + timestamps
if [ "$REUSE" = 1 ] && [ -f "$OUT/voice.mp3" ] && [ -f "$OUT/alignment.json" ]; then
  echo "[voice] reusing existing"
else
  echo "[voice] ElevenLabs $VOICE"
  jq -n --rawfile t "$SCRIPT" '{text:$t,model_id:"eleven_multilingual_v2",voice_settings:{stability:0.5,similarity_boost:0.75,use_speaker_boost:true}}' > "$OUT/_tts.json"
  curl -s "https://api.elevenlabs.io/v1/text-to-speech/${VOICE}/with-timestamps?output_format=mp3_44100_128" \
    -H "xi-api-key: $XI" -H "Content-Type: application/json" -X POST -d @"$OUT/_tts.json" -o "$OUT/_tts_resp.json"
  jq -r '.audio_base64' "$OUT/_tts_resp.json" | base64 -d > "$OUT/voice.mp3"
  jq '.alignment' "$OUT/_tts_resp.json" > "$OUT/alignment.json"
fi

# 2) Captions
uv run --python 3.12 python "$HERE/make_ass.py" "$OUT/alignment.json" "$OUT/captions.ass" "$WPC"

# 3) Image
if [ "$REUSE" = 1 ] && [ -f "$OUT/image.png" ]; then
  echo "[image] reusing existing"
else
  [ -n "$IMGPROMPT" ] || { echo "need --image-prompt (or --reuse an image.png)" >&2; exit 2; }
  echo "[image] Pollinations/Flux"
  ENC=$(jq -rn --arg p "$IMGPROMPT" '$p|@uri')
  curl -s "https://image.pollinations.ai/prompt/${ENC}?width=720&height=1280&nologo=true&model=flux&seed=7" -o "$OUT/image.png" --max-time 120
fi

# 4) Optional ambient bed
DUR=$(uv run --python 3.12 python -c "import json;a=json.load(open('$OUT/alignment.json'));print(round(a['character_end_times_seconds'][-1]+1,2))")
AUDIO_MAP=( -map "1:a" ); FILTER_A=""
if [ "$MUSIC" = 1 ]; then
  "$FFMPEG" -y -f lavfi -i "sine=frequency=110:duration=$DUR" -f lavfi -i "sine=frequency=164.81:duration=$DUR" \
    -f lavfi -i "sine=frequency=220:duration=$DUR" -f lavfi -i "sine=frequency=329.63:duration=$DUR" \
    -filter_complex "[0][1][2][3]amix=inputs=4:normalize=1,tremolo=f=0.12:d=0.7,aecho=0.8:0.7:80:0.4,lowpass=f=600,highpass=f=80,afade=t=in:st=0:d=4,afade=t=out:st=$(awk "BEGIN{print $DUR-5}"):d=5[bed]" \
    -map "[bed]" -t "$DUR" "$OUT/bed.wav" 2>/dev/null
fi

# 5) Assemble
if [ "$MUSIC" = 1 ]; then
  "$FFMPEG" -y -i "$OUT/image.png" -i "$OUT/voice.mp3" -i "$OUT/bed.wav" -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.00035,1.18)':d=99999:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30,vignette=PI/4.5,subtitles=$OUT/captions.ass:fontsdir=$FONTS[v];[2:a]volume=0.09[bg];[1:a][bg]amix=inputs=2:normalize=0:duration=first[a]" \
    -map "[v]" -map "[a]" -c:v libx264 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$OUT/short.mp4" 2>/dev/null
else
  "$FFMPEG" -y -i "$OUT/image.png" -i "$OUT/voice.mp3" -filter_complex \
"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.00035,1.18)':d=99999:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30,vignette=PI/4.5,subtitles=$OUT/captions.ass:fontsdir=$FONTS[v]" \
    -map "[v]" -map "1:a" -c:v libx264 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$OUT/short.mp4" 2>/dev/null
fi

echo "[done] $OUT/short.mp4"
