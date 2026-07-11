"""make_demo.py — scripted browser session -> 9:16 product-demo SHORT.

Pipeline:  demo-spec JSON -> demo_recorder.mjs (Playwright, portrait recordVideo)
        -> gen_voice (autotube: ElevenLabs Eric + word timestamps)
        -> per-step footage fitted to its narration (speed 0.85x-1.3x, else
           trim / hold last frame) -> concat -> word-pop karaoke captions
           (autotube shorts_finish recipe) -> loudnorm -> 1080x1920 mp4.

Run under the autotube uv deps pattern (see run.sh / README.md):
  PYTHONPATH=/config/workspace/autotube/src uv run --no-project --python 3.12 \
    --with anthropic --with pydantic --with trafilatura \
    --with google-api-python-client --with google-auth --with imageio-ffmpeg \
    --with pillow python make_demo.py specs/pexels-demo.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/config/workspace/autotube/src")

from autotube.produce_short import gen_voice                      # noqa: E402
from autotube.shorts_finish import (words_from_alignment, build_captions,  # noqa: E402
                                    ensure_font)
from autotube.verify_short import ffmpeg_exe                      # noqa: E402

TOOL_DIR = Path(__file__).resolve().parent
RECORDER = TOOL_DIR / "demo_recorder.mjs"
OUT_W, OUT_H = 1080, 1920
SPEED_MIN, SPEED_MAX = 0.85, 1.3
_COMMON = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]
_LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=11"


def _ff(args: list) -> None:
    r = subprocess.run([ffmpeg_exe(), "-y", *map(str, args)],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-2000:]}")


def narration_segments(words: list[list], steps: list[dict], audio_dur: float) -> list[dict]:
    """Split the single VO alignment back into per-step [t0,t1] narration spans.

    Word counts per step narration index into the flat word list; boundaries are
    midpoints between the last word of a step and the first word of the next.
    """
    counts = [len((s.get("narration") or "").split()) for s in steps]
    if sum(counts) != len(words):
        raise RuntimeError(f"word-count mismatch: script={sum(counts)} alignment={len(words)}")
    bounds, i = [0.0], 0
    for c in counts[:-1]:
        i += c
        bounds.append((words[i - 1][2] + words[i][1]) / 2)
    bounds.append(max(audio_dur, words[-1][2]))
    return [{"t0": bounds[k], "t1": bounds[k + 1], "dur": bounds[k + 1] - bounds[k]}
            for k in range(len(counts))]


def fit_step(base_mp4: Path, seg_out: Path, f_start: float, f_end: float, target: float) -> dict:
    """Cut [f_start,f_end] and fit it to `target` secs: speed within 0.85x-1.3x,
    overflow -> trim, underflow -> hold (clone) the last frame."""
    d = max(f_end - f_start, 0.2)
    speed = min(max(d / target, SPEED_MIN), SPEED_MAX)
    retimed = d / speed
    pad = max(target - retimed, 0.0)
    vf = f"setpts=PTS/{speed:.4f},fps=30,setsar=1"
    if pad > 0.01:
        vf += f",tpad=stop_mode=clone:stop_duration={pad:.3f}"
    _ff(["-ss", f"{f_start:.3f}", "-to", f"{f_end:.3f}", "-i", base_mp4,
         "-vf", vf, "-t", f"{target:.3f}", "-an", *_COMMON, seg_out])
    return {"footage": round(d, 2), "target": round(target, 2),
            "speed": round(speed, 2), "held": round(pad, 2)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="demo-spec JSON path")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--out", default=None, help="final mp4 path")
    ap.add_argument("--skip-record", action="store_true",
                    help="reuse an existing raw.webm/timeline.json in workdir")
    args = ap.parse_args()

    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text())
    name = spec_path.stem
    work = Path(args.workdir or TOOL_DIR / "output" / name / "work").resolve()
    out = Path(args.out or TOOL_DIR / "output" / f"{name}.mp4").resolve()
    work.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1) record the browser session
    if not args.skip_record:
        r = subprocess.run(["node", str(RECORDER), str(spec_path), str(work)],
                           capture_output=True, text=True, timeout=600)
        print(r.stderr, file=sys.stderr)
        if r.returncode:
            raise SystemExit(f"recorder failed: {r.stderr[-800:]}")
    timeline = json.loads((work / "timeline.json").read_text())["steps"]
    steps = spec["steps"]

    # 2) voiceover with word timestamps (single continuous read = natural flow)
    script = " ".join((s.get("narration") or "").strip() for s in steps).strip()
    if (work / "voice.mp3").exists() and (work / "alignment.json").exists():
        alignment = json.loads((work / "alignment.json").read_text())
        audio_dur = alignment["character_end_times_seconds"][-1]
        print(f"voice: reusing existing ({audio_dur:.1f}s)")
    else:
        audio_dur = gen_voice(script, work)
        alignment = json.loads((work / "alignment.json").read_text())
        print(f"voice: {audio_dur:.1f}s")
    words = words_from_alignment(alignment)
    segs = narration_segments(words, steps, audio_dur)

    # 3) normalize the recording, then fit each step to its narration span
    _ff(["-i", work / "raw.webm", "-vf", "fps=30,setsar=1", "-an", *_COMMON,
         work / "base.mp4"])
    report, concat_lines = [], []
    for i, (tstep, seg) in enumerate(zip(timeline, segs)):
        p = work / f"seg_{i:02d}.mp4"
        info = fit_step(work / "base.mp4", p, tstep["start"], tstep["end"], seg["dur"])
        report.append({"step": i, "action": tstep["action"], **info})
        concat_lines.append(f"file '{p}'")
        print(f"step {i} [{tstep['action']}] footage={info['footage']}s "
              f"target={info['target']}s speed={info['speed']}x held={info['held']}s")
    (work / "concat.txt").write_text("\n".join(concat_lines) + "\n")
    _ff(["-f", "concat", "-safe", "0", "-i", work / "concat.txt", "-c", "copy",
         work / "steps.mp4"])

    # 4) captions (proven word-pop recipe) + upscale + VO + loudnorm
    build_captions(words, work / "captions.ass")
    fonts = ensure_font().parent
    vf = (f"scale={OUT_W}:{OUT_H}:flags=lanczos,setsar=1,"
          f"tpad=stop_mode=clone:stop_duration=0.3,"
          f"subtitles={work / 'captions.ass'}:fontsdir={fonts}")
    _ff(["-i", work / "steps.mp4", "-i", work / "voice.mp3",
         "-vf", vf, "-af", _LOUDNORM,
         "-map", "0:v", "-map", "1:a", "-t", f"{audio_dur + 0.25:.3f}",
         *_COMMON, "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
         "-movflags", "+faststart", out])

    (work / "fit_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"out": str(out), "duration": round(audio_dur + 0.25, 2),
                      "steps": report}, indent=2))


if __name__ == "__main__":
    main()
