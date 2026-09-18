#!/usr/bin/env python3
"""
PixVerse API client for lip-sync video generation.
Takes video + audio (or TTS script) and generates lip-synced output.

Usage:
    doppler run -- uv run shared/pixverse.py VIDEO.mp4 AUDIO.mp3 --out OUTPUT.mp4
    doppler run -- uv run shared/pixverse.py --help

API documentation:
    https://docs.platform.pixverse.ai/speechlip-sync-1268530m0
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import requests

# API endpoints
BASE_URL = "https://app-api.pixverse.ai/openapi/v2"
UPLOAD_URL = f"{BASE_URL}/media/upload"
LIPSYNC_URL = f"{BASE_URL}/video/lip_sync/generate"
STATUS_URL = f"{BASE_URL}/video/result"  # /{video_id}
TTS_LIST_URL = f"{BASE_URL}/video/lip_sync/tts_list"

# Polling configuration
POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 120  # 10 minutes max


def get_api_key() -> str:
    """Get PixVerse API key from environment via Doppler."""
    api_key = os.environ.get("PIXVERSE_API_KEY")
    if not api_key:
        sys.exit(
            "ERROR: PIXVERSE_API_KEY not set.\n"
            "Run via: doppler run -- uv run shared/pixverse.py ...\n"
            "Or add the key to Doppler: https://dashboard.doppler.com/"
        )
    return api_key


def generate_trace_id() -> str:
    """Generate unique trace ID for each API request."""
    return str(uuid.uuid4())


def upload_media(file_path: Path, api_key: str) -> Tuple[int, str]:
    """
    Upload video or audio file to PixVerse.
    
    Returns:
        Tuple of (media_id, media_type)
    """
    if not file_path.exists():
        sys.exit(f"ERROR: file not found: {file_path}")
    
    print(f"Uploading {file_path.name}...")
    
    with open(file_path, "rb") as f:
        response = requests.post(
            UPLOAD_URL,
            headers={
                "API-KEY": api_key,
                "Ai-trace-id": generate_trace_id(),
            },
            files={"file": (file_path.name, f)},
            timeout=300,
        )
    
    if response.status_code != 200:
        sys.exit(f"ERROR: Upload failed ({response.status_code}): {response.text}")
    
    data = response.json()
    if data.get("ErrCode") != 0:
        sys.exit(f"ERROR: Upload failed: {data.get('ErrMsg', 'Unknown error')}")
    
    resp = data["Resp"]
    media_id = resp["media_id"]
    media_type = resp["media_type"]
    print(f"  Uploaded: {media_type} media_id={media_id}")
    
    return media_id, media_type


def generate_lipsync(
    video_media_id: int,
    audio_media_id: int,
    api_key: str,
) -> int:
    """
    Submit lip-sync generation job.
    
    Returns:
        video_id for polling status
    """
    print("Submitting lip-sync job...")
    
    payload = {
        "video_media_id": video_media_id,
        "audio_media_id": audio_media_id,
    }
    
    response = requests.post(
        LIPSYNC_URL,
        headers={
            "API-KEY": api_key,
            "Ai-trace-id": generate_trace_id(),
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    
    if response.status_code != 200:
        sys.exit(f"ERROR: Lip-sync generation failed ({response.status_code}): {response.text}")
    
    data = response.json()
    if data.get("ErrCode") != 0:
        sys.exit(f"ERROR: Lip-sync generation failed: {data.get('ErrMsg', 'Unknown error')}")
    
    resp = data["Resp"]
    video_id = resp["video_id"]
    credits = resp.get("credits", 0)
    
    print(f"  Job submitted: video_id={video_id} (cost: {credits} credits)")
    return video_id


def poll_status(video_id: int, api_key: str) -> str:
    """
    Poll video generation status until complete.
    
    Returns:
        URL of the generated video
    """
    print(f"Polling status for video_id={video_id}...")
    
    for attempt in range(MAX_POLL_ATTEMPTS):
        response = requests.get(
            f"{STATUS_URL}/{video_id}",
            headers={
                "API-KEY": api_key,
                "Ai-trace-id": generate_trace_id(),
            },
            timeout=30,
        )
        
        if response.status_code != 200:
            print(f"  WARNING: Status check failed ({response.status_code}), retrying...")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue
        
        data = response.json()
        if data.get("ErrCode") != 0:
            print(f"  WARNING: {data.get('ErrMsg', 'Unknown error')}, retrying...")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue
        
        resp = data["Resp"]
        status = resp["status"]
        
        # Status codes: 1=success, 5=in-progress, 7=moderation-fail, 8=generation-fail
        if status == 1:
            url = resp["url"]
            print(f"  ✓ Generation complete!")
            return url
        elif status == 7:
            sys.exit("ERROR: Content moderation failed. Video blocked by PixVerse.")
        elif status == 8:
            sys.exit("ERROR: Generation failed. Try different video/audio.")
        elif status == 5:
            elapsed = (attempt + 1) * POLL_INTERVAL_SECONDS
            print(f"  [{elapsed}s] Still generating...")
            time.sleep(POLL_INTERVAL_SECONDS)
        else:
            print(f"  WARNING: Unknown status {status}, retrying...")
            time.sleep(POLL_INTERVAL_SECONDS)
    
    sys.exit(f"ERROR: Generation timed out after {MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s")


def download_video(url: str, output_path: Path) -> None:
    """Download generated video to local path."""
    print(f"Downloading {output_path.name}...")
    
    response = requests.get(url, timeout=300, stream=True)
    if response.status_code != 200:
        sys.exit(f"ERROR: Download failed ({response.status_code})")
    
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Saved: {output_path} ({size_mb:.2f} MB)")


def log_experiment(entry: dict, log_file: Path) -> None:
    """Append an experiment record to the JSONL log."""
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def lipsync(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    no_log: bool = False,
) -> Path:
    """
    Full pipeline: upload video + audio, generate lip-sync, download result.
    
    Returns:
        Path to the generated video
    """
    api_key = get_api_key()
    
    print(f"Video: {video_path}")
    print(f"Audio: {audio_path}")
    print(f"Output: {output_path}\n")
    
    # Upload media
    video_media_id, video_type = upload_media(video_path, api_key)
    if video_type != "video":
        sys.exit(f"ERROR: Expected video media_type, got '{video_type}'")
    
    audio_media_id, audio_type = upload_media(audio_path, api_key)
    if audio_type != "audio":
        sys.exit(f"ERROR: Expected audio media_type, got '{audio_type}'")
    
    # Generate lip-sync
    video_id = generate_lipsync(video_media_id, audio_media_id, api_key)
    
    # Poll until complete
    video_url = poll_status(video_id, api_key)
    
    # Download result
    download_video(video_url, output_path)
    
    # Log to experiment log
    if not no_log:
        project_root = Path(__file__).parent.parent
        log_file = project_root / "data" / "experiment_log.jsonl"
        
        video_slug = video_path.stem[:20].replace(" ", "_").replace("-", "_")
        log_id = f"pixverse_{video_slug}_{int(time.time())}"
        
        log_entry = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "id": log_id,
            "tool": "pixverse",
            "video_input": str(video_path.name),
            "audio_input": str(audio_path.name),
            "output_file": str(output_path.name),
            "video_id": video_id,
            "output_url": video_url,
        }
        log_experiment(log_entry, log_file)
        print(f"\nLogged to {log_file.relative_to(project_root)}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="PixVerse lip-sync: video + audio → lip-synced video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage:
  doppler run -- uv run shared/pixverse.py video.mp4 audio.mp3 --out synced.mp4
  
  # Scene 01 workflow:
  doppler run -- uv run shared/pixverse.py \\
      data/scenes/in_progress/scene_01_shot_11.mp4 \\
      data/scenes/in_progress/scene_01_line_3.mp3 \\
      --out data/scenes/in_progress/scene_01_shot_11_synced.mp4

Environment:
  Requires PIXVERSE_API_KEY from Doppler.
  Add key at: https://dashboard.doppler.com/
        """,
    )
    parser.add_argument("video", nargs="?", help="Input video file (.mp4, .mov, .webm, max 100MB)")
    parser.add_argument("audio", nargs="?", help="Input audio file (.mp3, .wav, .m4a, .aac, max 100MB)")
    parser.add_argument("--out", help="Output video path (default: <video>_synced.mp4)")
    parser.add_argument("--no-log", action="store_true", help="Skip logging to experiment_log.jsonl")
    
    args = parser.parse_args()
    
    if not args.video or not args.audio:
        parser.print_help()
        sys.exit("\nERROR: Both video and audio files are required")
    
    video_path = Path(args.video).expanduser().resolve()
    audio_path = Path(args.audio).expanduser().resolve()
    
    if args.out:
        output_path = Path(args.out).expanduser().resolve()
    else:
        output_path = video_path.parent / f"{video_path.stem}_synced.mp4"
    
    lipsync(video_path, audio_path, output_path, no_log=args.no_log)
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
