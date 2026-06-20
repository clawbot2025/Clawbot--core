---
type: intake
date: 2026-06-20
topic: AutoTube end-goal + session knowledge dump
status: untriaged
routing: mostly PROJECT-specific → destined for the clawbot-autotube repo (not core)
---

# Session dump — AutoTube vision + verified research (2026-06-20)

## End goal (the why behind all of this)
A fully automated YouTube content pipeline: RSS/feeds + other sources → AI-written script → AI avatar
video → assemble → **auto-upload** to the channel. We built the core/knowledge-base first so this
project plugs in cleanly instead of being rebuilt from scratch.

## AutoTube components (project-specific → clawbot-autotube repo)
- **Sourcing:** RSS via Miniflux (self-hosted), tiered primary-source feeds + a Python dedup/scoring layer. (Old setup gone; rebuild.)
- **Scripting:** AI-written per episode (Claude).
- **Voice:** HeyGen built-in voice (no separate TTS in v1).
- **Avatar video:** HeyGen.
- **Assembly:** FFmpeg (intro + anchor, normalize, concat, verify streams).
- **Publish:** YouTube Data API v3, OAuth, unlisted-by-default, auto-upload.
- **Hosting:** Hostinger VPS (always-on; webhook receiver + Miniflux live here).
- **Pipeline B (later):** Wan 2.2 14B via ComfyUI on RunPod GPU (generative video). Repo: clawbot2025/comfyui-runpod.
- **Also evaluated:** Higgsfield (external gen: Seedance/Veo/Kling) as an optional alt provider.

## VERIFIED official research to reuse — HeyGen v3 (grounded, cited)
- **Create:** `POST https://api.heygen.com/v3/videos` (header `x-api-key`). Flat payload: `type=avatar`,
  `avatar_id`, `script`, `voice_id`, `resolution` (1080p), `aspect_ratio`, optional `background`.
  Avatars/voices fetched live (`GET /v3/avatars/looks`, `GET /v3/voices`). v1/v2 legacy sunset **2026-10-31**.
- **Webhooks (we want these for scale — NOT polling):** register `POST /v3/webhooks/endpoints`, subscribe
  `avatar_video.success` / `avatar_video.fail`; verify via `Signature` header = **HMAC-SHA256(raw body, secret)**.
  One always-on HTTPS receiver on the VPS: verify → return 200 → dedupe → match `callback_id` → download → assemble → upload.
- Old repo `clawbot-autotube` = legacy/messy reference only (used deprecated v2). Rebuild fresh.

## Decisions locked
- Rebuild AutoTube from scratch (do not copy old repo files).
- HeyGen v3 + webhooks; HeyGen built-in voice; unlisted-by-default; AI-written scripts.

## Next action toward the goal
Stand up the `clawbot-autotube` project (fresh), Spec-Kit-driven, consuming the core. Triage Tier-1 skills first.
