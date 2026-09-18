#!/usr/bin/env python3
"""
Scene 01 lip-sync consumer.
Wires the PixVerse client for Scene 01 (Apartment Origin) workflow.

Expected Scene 01 asset structure under data/scenes/:
    in_progress/scene_01_shot_11_drone_pov.mp4    # Drone POV video (shot 11)
    in_progress/scene_01_line_3_flo_voice.mp3     # Line 3 with Flo's voice (post-ElevenLabs)
    in_progress/scene_01_shot_11_synced.mp4       # Output: lip-synced result

Usage:
    # Process Scene 01 shot 11 (Drone POV explanation):
    doppler run -- uv run shared/scripts/scene_01_lipsync.py \\
        --video data/scenes/in_progress/scene_01_shot_11_drone_pov.mp4 \\
        --audio data/scenes/in_progress/scene_01_line_3_flo_voice.mp3 \\
        --out data/scenes/in_progress/scene_01_shot_11_synced.mp4

Scene 01 details: data/scenes/backlog/scene_01_apartment_origin.md
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for shared modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixverse import lipsync


def main():
    parser = argparse.ArgumentParser(
        description="Scene 01 lip-sync workflow using PixVerse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scene 01 (Apartment Origin) has 11 shots total.
Shot 11 is the final drone POV shot where Flo explains the feature.

Typical workflow:
  1. Generate video clip (Midjourney/Grok Aurora)
  2. Record dialogue line (human performance)
  3. Voice swap (ElevenLabs speech-to-speech via voice_swap.py)
  4. Lip-sync (PixVerse via this script)

Expected assets under data/scenes/in_progress/:
  - scene_01_shot_11_drone_pov.mp4   (video from Midjourney/Aurora)
  - scene_01_line_3_flo_voice.mp3    (audio from voice_swap.py)

Output:
  - scene_01_shot_11_synced.mp4      (lip-synced final video)

Reference:
  Scene storyboard: data/scenes/backlog/scene_01_apartment_origin.md
  Line 3 text: "I can automatically send you a text link through the 
               drone when I say the trigger phrase. It'll start recording 
               and send you a link, and you can click it whenever you want 
               — it'll start the video right where I triggered it."
        """,
    )
    
    parser.add_argument(
        "--video",
        required=True,
        help="Input video file (e.g., scene_01_shot_11_drone_pov.mp4)",
    )
    parser.add_argument(
        "--audio",
        required=True,
        help="Input audio file (e.g., scene_01_line_3_flo_voice.mp3)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output video path (e.g., scene_01_shot_11_synced.mp4)",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Skip logging to experiment_log.jsonl",
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    video_path = Path(args.video).expanduser().resolve()
    audio_path = Path(args.audio).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()
    
    # Validate scene assets exist
    if not video_path.exists():
        sys.exit(f"ERROR: Video not found: {video_path}")
    if not audio_path.exists():
        sys.exit(f"ERROR: Audio not found: {audio_path}")
    
    # Run lip-sync pipeline
    print("Scene 01 Lip-Sync Pipeline")
    print("=" * 50)
    print(f"Shot: {video_path.name}")
    print(f"Dialogue: {audio_path.name}")
    print(f"Output: {output_path.name}\n")
    
    lipsync(
        video_path=video_path,
        audio_path=audio_path,
        output_path=output_path,
        no_log=args.no_log,
    )
    
    print("\n" + "=" * 50)
    print("✓ Scene 01 lip-sync complete!")
    print(f"  Final video: {output_path}")


if __name__ == "__main__":
    main()
