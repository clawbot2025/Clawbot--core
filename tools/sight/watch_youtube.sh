#!/usr/bin/env bash
# sight/watch_youtube.sh — let the agent WATCH any YouTube video.
#
# Uses Gemini's native YouTube ingestion (Google fetches the video on its own
# servers), so it sidesteps yt-dlp / cookies / datacenter-IP bot-walls entirely.
# Proven 2026-06-25 on https://youtu.be/ONmaDdOBGig.
#
# Usage:
#   watch_youtube.sh <youtube_url> "<question/prompt>" [max_output_tokens]
#
# Requires: curl, jq, and GEMINI_API_KEY (read from the operations keychain).
# Notes:
#   - A 5-6 min video tokenizes to ~100K input tokens on gemini-2.5-flash (cheap).
#   - thinkingBudget:0 keeps the whole output budget for the actual answer
#     (otherwise the model spends it "thinking" and truncates — finishReason MAX_TOKENS).
set -euo pipefail

URL="${1:?usage: watch_youtube.sh <url> <prompt> [max_tokens]}"
PROMPT="${2:?usage: watch_youtube.sh <url> <prompt> [max_tokens]}"
MAXTOK="${3:-4000}"
KEYCHAIN="${GEMINI_KEYCHAIN:-/config/workspace/operations/.secrets/.env}"

GEMINI_API_KEY="${GEMINI_API_KEY:-$(grep '^GEMINI_API_KEY=' "$KEYCHAIN" | cut -d= -f2-)}"
[ -n "$GEMINI_API_KEY" ] || { echo "no GEMINI_API_KEY" >&2; exit 1; }

PAYLOAD=$(jq -n --arg url "$URL" --arg p "$PROMPT" --argjson mt "$MAXTOK" \
  '{contents:[{parts:[{fileData:{fileUri:$url}},{text:$p}]}],
    generationConfig:{maxOutputTokens:$mt,temperature:0.3,thinkingConfig:{thinkingBudget:0}}}')

RESP=$(curl -s --max-time 280 \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" -X POST -d "$PAYLOAD")

# API errors (429 quota, depleted credits, 403 blocked key, ...) must FAIL,
# not print the error as if it were the answer (learned 2026-07-02: depleted-
# credit messages got written into an intel brief as "analysis").
ERR_MSG=$(echo "$RESP" | jq -r '.error.message // empty')
if [ -n "$ERR_MSG" ]; then
  ERR_CODE=$(echo "$RESP" | jq -r '.error.code // "?"')
  ERR_STATUS=$(echo "$RESP" | jq -r '.error.status // "?"')
  echo "GEMINI API ERROR $ERR_CODE ($ERR_STATUS): $ERR_MSG" >&2
  # exit 29 for rate/quota-type errors so callers can retry-later; 1 otherwise
  [ "$ERR_CODE" = "429" ] && exit 29
  exit 1
fi

echo "$RESP" | jq -r '.candidates[0].content.parts[0].text // "PARSE FAIL"'
FR=$(echo "$RESP" | jq -r '.candidates[0].finishReason // "?"')
[ "$FR" = "MAX_TOKENS" ] && echo "[warn: truncated at MAX_TOKENS — re-run with a higher 3rd arg]" >&2
exit 0
