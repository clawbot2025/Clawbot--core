# product_demo — scripted browser session → 9:16 demo SHORT

Turns a JSON "demo spec" into a finished 1080x1920 short: Playwright drives the
product's website in a portrait viewport, ElevenLabs Eric narrates it (word
timestamps), each step's footage is fitted to its narration, and the proven
MOTO word-pop karaoke captions are burned on top. Client-demo grade output for
Project C ("here's your product, demoed by AI, in an afternoon").

Reuses the proven stack — nothing hand-rolled:
- `autotube/capture/capture.mjs` rig (wrapped rootless Chromium, UA, flags, consent sweep)
- `autotube.produce_short.gen_voice` (ElevenLabs `/with-timestamps`)
- `autotube.shorts_finish` (`words_from_alignment`, `build_captions`, Anton font)

## Run

```bash
cd /config/workspace/core/tools/product_demo
./run.sh specs/pexels-demo.json            # full pipeline
./run.sh specs/pexels-demo.json --skip-record   # re-assemble, reuse raw.webm + voice
```

Output: `output/<spec-name>.mp4` (+ `output/<spec-name>/work/` intermediates:
`raw.webm`, `timeline.json`, `voice.mp3`, `alignment.json`, `fit_report.json`).

Requires `ELEVENLABS_API_KEY` in `operations/.secrets/.env` (loaded via
`autotube.config`). Recording alone costs nothing; the VO call is the only spend.

## Writing a demo spec

```jsonc
{
  "product": "Pexels Videos",
  "url": "https://www.pexels.com/videos/",
  "viewport": { "width": 608, "height": 1080 },   // 9:16 portrait (default)
  "steps": [
    { "action": "goto",   "url": "...", "secs": 4, "narration": "hook — first 2 seconds" },
    { "action": "type",   "selector": "input[...]", "text": "query", "enter": true, "secs": 4, "narration": "..." },
    { "action": "scroll", "px": 1400, "secs": 7, "narration": "..." },
    { "action": "click",  "selector": "a[href^='/video/']", "secs": 0.5, "narration": "..." },
    { "action": "hover",  "selector": "...", "secs": 2, "narration": "..." },
    { "action": "wait",   "secs": 3, "narration": "outro, one breath" }
  ]
}
```

Rules that make it good:
- **Every step needs `narration`** — the full script is one continuous ElevenLabs
  read (natural flow), then split back into per-step spans via word timestamps.
- **Narration writes the pacing.** Footage is fitted to each narration span:
  speed-adjust within 0.85x–1.3x, overflow trimmed, underflow holds the last
  frame. Aim `secs` ≈ narration length so fits stay near 1.0x (see
  `fit_report.json` after a run).
- **Hook at 0.0s** — the first step's narration is the hook; no intro. Outro =
  one breath. Follow `BRAND-VOICE` shorts rules.
- `goto` starts its clock **after** the page paints (loading white frames are
  excluded from the cut).
- Human feel is built in: eased mouse moves, 150–300 ms settle before clicks,
  ~60 ms/char typing, eased smooth scrolls.
- Headless caveat: bot-walled sites (some login pages, Cloudflare-hard targets)
  won't render — probe first with `autotube/capture/capture.mjs shot <url> x.png`.

## Files
- `demo_recorder.mjs` — Playwright recorder: spec → `raw.webm` + `timeline.json`
- `make_demo.py` — orchestrator: record → voice → fit → concat → captions → mp4
- `run.sh` — uv wrapper (autotube deps pattern)
- `specs/` — demo specs; `output/` — finished shorts (gitignored intermediates)
