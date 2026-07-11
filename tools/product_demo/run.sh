#!/usr/bin/env bash
# run.sh — product_demo entrypoint (same uv deps pattern as autotube/deploy/cron_run.sh).
#   ./run.sh specs/pexels-demo.json [extra make_demo.py args...]
set -eu
export HOME="${HOME:-/config}"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:/usr/local/bin:/usr/bin:/bin"
TOOL="$(cd "$(dirname "$0")" && pwd)"

PY_DEPS=(--with anthropic --with pydantic --with trafilatura
         --with google-api-python-client --with google-auth --with imageio-ffmpeg
         --with pillow)

PYTHONPATH=/config/workspace/autotube/src uv run --no-project --python 3.12 \
  "${PY_DEPS[@]}" python "$TOOL/make_demo.py" "$@"
