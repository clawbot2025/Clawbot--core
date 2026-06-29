# make_short — faceless 9:16 short generator

Turns a script into a finished vertical short, the @EdmundCavendishHale way:
**ElevenLabs voice (+ word timestamps) → word-synced yellow captions → AI image (Pollinations/Flux)
→ ffmpeg (Ken Burns zoom + vignette + ambient music bed) → `short.mp4` (720×1280).**

Proven 2026-06-25 — first outputs: youtu.be/HojypywuCFE (v1), youtu.be/FblTx2dscDY (v2, music+vignette).
Origin/notes: `operations/outputs/proof-short/RECIPE.md`, north-star `operations/memory/north-star-edmund-hale.md`.

## Use
```bash
core/tools/make_short/make_short.sh \
  --script path/to/script.txt \
  --image-prompt "Photorealistic vertical portrait of a distinguished elderly gentleman ..." \
  --out output/dir \
  [--voice JBFqnCBsd6RMkjVDRZzb]   # default: George, British storyteller
  [--no-music] [--reuse] [--words-per-cap 3]
```
- `--reuse` skips TTS/image if `voice.mp3`/`alignment.json`/`image.png` already exist in `--out` (no API spend).
- Outputs into `--out`: `voice.mp3`, `alignment.json`, `captions.ass`, `image.png`, `bed.wav`, `short.mp4`.

## Requirements (this box)
- `ELEVENLABS_API_KEY` in `operations/.secrets/.env` (override `$KEYCHAIN`).
- Static **ffmpeg** at `/tmp/ffmpeg` (override `$FFMPEG`). Install: johnvansickle static; box lacks `xz`,
  so decompress the `.tar.xz` via `uv run python -c "import lzma…"` then `tar -xf` (see RECIPE.md).
- `uv` (python), `curl`, `jq`. Anton font auto-fetched to `/tmp/fonts`.

## To publish a result so it's watchable (esp. on tablet)
Upload UNLISTED via the autotube uploader → returns a youtu.be link:
```bash
cd autotube && PYTHONPATH=src uv run --no-project --python 3.12 \
  --with google-api-python-client --with google-auth --with google-auth-oauthlib \
  python -c "from autotube.publish.youtube import upload; print(upload('OUT/short.mp4', title='...', privacy='unlisted')['url'])"
```

## Known polish TODOs
- Music is a synthesized ambient pad (placeholder) — swap a real royalty-free orchestral track for production.
- Captions are N-word chunks; add karaoke `\k` word-by-word highlight for extra polish.
- Single static image (matches the format); paid image generator for higher hero quality.
