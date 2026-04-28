#!/usr/bin/env python3
"""
Extract frames from video files for LoRA training data prep.

Why: Image-to-video models (Midjourney, Grok, Runway) preserve identity from
the source frame. Every extracted frame is the same person by construction.
Pulling stills from those videos gives us drift-free training data.

Usage:
    # Extract every frame from every video in the default folder:
    uv run shared/scripts/extract_video_frames.py

    # Extract from a specific video or folder:
    uv run shared/scripts/extract_video_frames.py path/to/video.mp4
    uv run shared/scripts/extract_video_frames.py path/to/folder/

    # Sample every Nth frame instead of all of them:
    uv run shared/scripts/extract_video_frames.py --every 4    # every 4th frame
    uv run shared/scripts/extract_video_frames.py --fps 2      # 2 frames per second

    # Custom output folder:
    uv run shared/scripts/extract_video_frames.py --out data/training_v3_frames
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "midjourney_videos"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "training_v3_frames"
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def find_videos(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() in VIDEO_EXTS else []
    return sorted(p for p in input_path.iterdir() if p.suffix.lower() in VIDEO_EXTS)


def probe_video(video: Path) -> dict:
    """Return {duration, fps, frames, width, height} via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
        "-of", "default=noprint_wrappers=1",
        str(video),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    info = {}
    for line in out.strip().splitlines():
        k, _, v = line.partition("=")
        info[k] = v
    fps_str = info.get("r_frame_rate", "0/1")
    num, _, den = fps_str.partition("/")
    fps = float(num) / float(den) if den and float(den) > 0 else 0.0
    duration = float(info.get("duration", 0) or 0)
    return {
        "duration": duration,
        "fps": fps,
        "frames": int(info.get("nb_frames", 0) or round(duration * fps)),
        "width": int(info.get("width", 0) or 0),
        "height": int(info.get("height", 0) or 0),
    }


def extract(video: Path, out_dir: Path, every: int | None, fps: float | None) -> int:
    """Extract frames from one video into out_dir/<stem>/. Returns frame count."""
    stem = video.stem.replace(" ", "_")
    target = out_dir / stem
    target.mkdir(parents=True, exist_ok=True)

    pattern = str(target / f"{stem}_%05d.png")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video)]

    if fps is not None:
        cmd += ["-vf", f"fps={fps}"]
    elif every is not None and every > 1:
        cmd += ["-vf", f"select=not(mod(n\\,{every}))", "-vsync", "vfr"]
    # else: extract every frame (default)

    cmd += ["-q:v", "1", pattern]
    subprocess.run(cmd, check=True)
    return len(list(target.glob(f"{stem}_*.png")))


def main():
    parser = argparse.ArgumentParser(description="Extract frames from videos for LoRA training prep")
    parser.add_argument("input", nargs="?", default=str(DEFAULT_INPUT),
                        help=f"Video file or folder (default: {DEFAULT_INPUT.relative_to(PROJECT_ROOT)})")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT),
                        help=f"Output folder (default: {DEFAULT_OUTPUT.relative_to(PROJECT_ROOT)})")
    parser.add_argument("--every", type=int, help="Extract every Nth frame")
    parser.add_argument("--fps", type=float, help="Extract N frames per second")
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        sys.exit("ERROR: ffmpeg/ffprobe not on PATH. Install with: brew install ffmpeg")

    if args.every and args.fps:
        sys.exit("ERROR: use --every OR --fps, not both")

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()

    if not input_path.exists():
        sys.exit(f"ERROR: input not found: {input_path}")

    videos = find_videos(input_path)
    if not videos:
        sys.exit(f"ERROR: no videos found in {input_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(videos)} video(s)")
    print(f"Output: {out_dir}\n")

    total_frames = 0
    for video in videos:
        info = probe_video(video)
        size_mb = video.stat().st_size / 1024 / 1024
        print(f"  {video.name}")
        print(f"    {info['width']}x{info['height']}  {info['fps']:.1f} fps  "
              f"{info['duration']:.1f}s  ~{info['frames']} frames  {size_mb:.1f} MB")

        count = extract(video, out_dir, args.every, args.fps)
        total_frames += count
        print(f"    -> extracted {count} frames\n")

    print(f"Done. {total_frames} total frames in {out_dir}")


if __name__ == "__main__":
    main()
