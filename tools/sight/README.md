# sight — let the agent WATCH video

**Capability:** the agent can watch any YouTube video and answer questions about it
(structure, hook, visuals, audio, CTA, how-it-was-made, etc.).

**How it works (the key trick):** instead of downloading with yt-dlp (which gets
blocked by YouTube's bot-wall on datacenter IPs, even *with* cookies), we hand the
YouTube URL straight to **Gemini** via `fileData.fileUri`. Google fetches the video
on its own servers and returns a multimodal analysis. No download, no cookies, no
ffmpeg, no IP problem.

**Proven:** 2026-06-25 on `https://youtu.be/ONmaDdOBGig` (Nate Herk). Full blueprint
it produced: `operations/outputs/nateherk-fable5-video-analysis.md`.

## Use
```bash
core/tools/sight/watch_youtube.sh <youtube_url> "<question>" [max_output_tokens]
```
- Reads `GEMINI_API_KEY` from `operations/.secrets/.env` (override via `$GEMINI_KEYCHAIN`/`$GEMINI_API_KEY`).
- Model: `gemini-2.5-flash`, thinking disabled so the full output budget goes to the answer.
- A 5-6 min video ≈ ~100K input tokens (cheap on flash). Call takes ~30s.
- If output ends with `[warn: truncated at MAX_TOKENS]`, re-run with a bigger 3rd arg.

## Known gaps / next
- Returns Gemini's *interpretation* — for exact on-screen text/links use the video
  description (see funnel notes), not the visual read.
- yt-dlp on this box is bot-walled; a durable fix (persistent logged-in browser on a
  burner account) is noted in operations as the real download path if we ever need files.
