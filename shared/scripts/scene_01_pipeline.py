#!/usr/bin/env python3
"""
End-to-End Content Pipeline Orchestrator for Scene 01 (Apartment Origin).

Full pipeline: ComfyUI → Aurora → ElevenLabs → PixVerse → TikTok-ready video

This orchestrator wires together existing clients in the correct order for
one Scene 01 shot path. Runs in DRY-RUN mode by default — pass --live to
execute actual paid API calls.

Usage:
    # Dry-run (default): validate inputs and show step plan without API calls
    doppler run -- uv run shared/scripts/scene_01_pipeline.py \\
        --shot 11 \\
        --prompt "Flo at desk with drone" \\
        --line 3

    # Live mode: execute full pipeline with actual API calls
    doppler run -- uv run shared/scripts/scene_01_pipeline.py \\
        --shot 11 \\
        --prompt "Flo at desk with drone" \\
        --line 3 \\
        --live

    # Custom paths:
    doppler run -- uv run shared/scripts/scene_01_pipeline.py \\
        --still data/scenes/in_progress/scene_01_shot_11_base.png \\
        --audio-input data/scenes/in_progress/recorded_line_3.m4a \\
        --output data/scenes/in_progress/scene_01_shot_11_final.mp4 \\
        --live

Environment variables required for --live mode:
    XAI_API_KEY          - xAI Aurora API key (for image-to-video)
    ELEVEN_LABS_API_KEY  - ElevenLabs API key (for voice swap)
    PIXVERSE_API_KEY     - PixVerse API key (for lip-sync)

Scene 01 details: data/scenes/backlog/scene_01_apartment_origin.md
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add parent directory to path for shared modules
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "shared"))
sys.path.insert(0, str(PROJECT_ROOT / "shared" / "scripts"))

from aurora import AuroraClient
from pixverse import lipsync
from voice_swap import swap as voice_swap

# Scene 01 dialogue lines
DIALOGUE_LINES = {
    1: "Oh hi, Mom. I was just about to call you — I've been working on this project, let me show you.",
    2: "Okay Mom, I'm sending you a text link. Just click on it and it'll switch you to the drone camera.",
    3: "I can automatically send you a text link through the drone when I say the trigger phrase. It'll start recording and send you a link, and you can click it whenever you want — it'll start the video right where I triggered it.",
}

# Default paths for Scene 01
SCENES_DIR = PROJECT_ROOT / "data" / "scenes" / "in_progress"
OUTPUT_DIR = PROJECT_ROOT / "output" / "scene_01"


class PipelineOrchestrator:
    """Orchestrates the full content pipeline with dry-run support."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.steps_executed = []
        self.artifacts = {}

    def validate_env_keys(self) -> dict[str, bool]:
        """
        Validate required environment variables for live mode.

        Returns:
            Dict mapping key names to whether they exist
        """
        required_keys = {
            "XAI_API_KEY": os.environ.get("XAI_API_KEY") is not None,
            "ELEVEN_LABS_API_KEY": os.environ.get("ELEVEN_LABS_API_KEY") is not None,
            "PIXVERSE_API_KEY": os.environ.get("PIXVERSE_API_KEY") is not None,
        }
        return required_keys

    def print_header(self, title: str):
        """Print a section header."""
        print()
        print("=" * 70)
        print(f"  {title}")
        print("=" * 70)
        print()

    def print_step(self, step_num: int, title: str, details: dict):
        """Print a pipeline step with details."""
        print(f"\n[Step {step_num}] {title}")
        print("-" * 50)
        for key, value in details.items():
            print(f"  {key}: {value}")

    def step_comfyui_generate(
        self, prompt: str, output_path: Path
    ) -> Optional[Path]:
        """
        Step 1: Generate base still image using ComfyUI.

        NOTE: This is a dry-run stub. Full ComfyUI job requires the server
        running and proper workflow submission via mission_control.py.
        For CI/testing, we accept a pre-generated still via --still flag.

        Args:
            prompt: Image generation prompt
            output_path: Where to save the generated image

        Returns:
            Path to generated image (or None in dry-run)
        """
        self.print_step(
            1,
            "ComfyUI Still Generation",
            {
                "Tool": "mission_control.py generate-local",
                "Prompt": prompt,
                "Output": str(output_path),
                "Status": "DRY-RUN STUB" if self.dry_run else "Would invoke ComfyUI API",
            },
        )

        if self.dry_run:
            print("\n  DRY-RUN: ComfyUI step would execute:")
            print(f"    ./shared/scripts/mission_control.py generate-local \\")
            print(f"      --prompt \"{prompt}\" \\")
            print(f"      --scene desert-sunset \\")  # Example, adjust for Scene 01
            print(f"      --output {output_path}")
            print("\n  For actual generation, ensure ComfyUI server is running:")
            print("    ./shared/scripts/start_comfyui.sh")
            self.steps_executed.append(("comfyui", "dry_run"))
            return None

        # Live mode: would need to invoke ComfyUI
        # For now, this is a stub — full implementation needs ComfyUI server
        print("\n  ERROR: ComfyUI live generation not yet implemented in orchestrator.")
        print("  Provide a pre-generated still via --still flag.")
        sys.exit(1)

    def step_aurora_video(
        self, still_path: Path, motion_prompt: str, output_path: Path
    ) -> Optional[Path]:
        """
        Step 2: Generate video from still using xAI Aurora.

        Args:
            still_path: Path to base still image
            motion_prompt: Text describing desired motion
            output_path: Where to save the generated video

        Returns:
            Path to generated video (or None in dry-run)
        """
        self.print_step(
            2,
            "Aurora Image-to-Video",
            {
                "Tool": "aurora.py (xAI Grok Imagine Video)",
                "Image": str(still_path),
                "Prompt": motion_prompt,
                "Duration": "10s",
                "Resolution": "720p",
                "Output": str(output_path),
            },
        )

        # Initialize Aurora client
        client = AuroraClient(dry_run=self.dry_run)

        if self.dry_run:
            # Dry-run: validate image path format, but don't require file to exist
            # (it might be generated in Step 1)
            print("\n  DRY-RUN: Would submit to Aurora API with:")
            print(f"    Image: {still_path}")
            print(f"    Prompt: {motion_prompt}")
            print(f"    Duration: 10s")
            print(f"    Resolution: 720p")
            print(f"    Aspect ratio: 16:9")
            # Validate but don't execute
            result = client.generate_video(
                prompt=motion_prompt,
                image_path=str(still_path),
                duration=10,
                resolution="720p",
                wait=False,
            )
            self.steps_executed.append(("aurora", "dry_run"))
            return None

        # Live mode: verify still exists before proceeding
        if not still_path.exists():
            print(f"\n  ERROR: Input still not found: {still_path}")
            sys.exit(1)

        # Live mode: full Aurora I2V generation
        print("\n  Submitting to Aurora API...")
        result = client.generate_video(
            prompt=motion_prompt,
            image_path=str(still_path),
            duration=10,
            resolution="720p",
            aspect_ratio="16:9",
            wait=True,
            max_wait=300,
        )

        if result["status"] == "done":
            print(f"\n  Downloading video...")
            client.download_video(result["video_url"], str(output_path))
            self.steps_executed.append(("aurora", "completed", result["request_id"]))
            self.artifacts["aurora_video"] = output_path
            return output_path
        else:
            print(f"\n  ERROR: Aurora generation failed: {result['status']}")
            sys.exit(1)

    def step_voice_swap(
        self, recorded_audio: Path, voice_name: str, output_path: Path
    ) -> Optional[Path]:
        """
        Step 3: Replace voice using ElevenLabs speech-to-speech.

        Args:
            recorded_audio: Path to human-performed audio
            voice_name: Target voice (e.g., 'matilda')
            output_path: Where to save voice-swapped audio

        Returns:
            Path to voice-swapped audio (or None in dry-run)
        """
        self.print_step(
            3,
            "ElevenLabs Voice Swap",
            {
                "Tool": "voice_swap.py (ElevenLabs speech-to-speech)",
                "Input": str(recorded_audio),
                "Voice": voice_name,
                "Model": "eleven_multilingual_sts_v2",
                "Output": str(output_path),
            },
        )

        if not recorded_audio.exists() and not self.dry_run:
            print(f"\n  ERROR: Input audio not found: {recorded_audio}")
            sys.exit(1)

        if self.dry_run:
            print("\n  DRY-RUN: Would execute:")
            print(f"    doppler run -- uv run shared/scripts/voice_swap.py \\")
            print(f"      {recorded_audio} \\")
            print(f"      --voice {voice_name} \\")
            print(f"      --out {output_path}")
            self.steps_executed.append(("voice_swap", "dry_run"))
            return None

        # Live mode: full voice swap
        print("\n  Processing voice swap...")
        result_path = voice_swap(
            input_path=recorded_audio,
            voice_name=voice_name,
            out_path=output_path,
            no_log=True,  # We'll log at the pipeline level
        )
        self.steps_executed.append(("voice_swap", "completed"))
        self.artifacts["voice_audio"] = result_path
        return result_path

    def step_lipsync(
        self, video_path: Path, audio_path: Path, output_path: Path
    ) -> Optional[Path]:
        """
        Step 4: Generate lip-synced video using PixVerse.

        Args:
            video_path: Path to video from Aurora
            audio_path: Path to voice-swapped audio
            output_path: Where to save lip-synced video

        Returns:
            Path to final lip-synced video (or None in dry-run)
        """
        self.print_step(
            4,
            "PixVerse Lip-Sync",
            {
                "Tool": "pixverse.py (PixVerse lip-sync API)",
                "Video": str(video_path),
                "Audio": str(audio_path),
                "Output": str(output_path),
            },
        )

        if not self.dry_run:
            if not video_path.exists():
                print(f"\n  ERROR: Input video not found: {video_path}")
                sys.exit(1)
            if not audio_path.exists():
                print(f"\n  ERROR: Input audio not found: {audio_path}")
                sys.exit(1)

        if self.dry_run:
            print("\n  DRY-RUN: Would execute:")
            print(f"    doppler run -- uv run shared/pixverse.py \\")
            print(f"      {video_path} \\")
            print(f"      {audio_path} \\")
            print(f"      --out {output_path}")
            self.steps_executed.append(("pixverse", "dry_run"))
            return None

        # Live mode: full lip-sync
        print("\n  Processing lip-sync...")
        result_path = lipsync(
            video_path=video_path,
            audio_path=audio_path,
            output_path=output_path,
            no_log=True,  # We'll log at the pipeline level
        )
        self.steps_executed.append(("pixverse", "completed"))
        self.artifacts["final_video"] = result_path
        return result_path

    def log_pipeline_run(self, args: argparse.Namespace, success: bool):
        """Log the full pipeline run to experiment_log.jsonl."""
        log_file = PROJECT_ROOT / "data" / "experiment_log.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "id": f"pipeline_scene01_shot{args.shot or 'custom'}_{int(time.time())}",
            "tool": "scene_01_pipeline",
            "scene": "scene_01_apartment_origin",
            "shot": args.shot,
            "dry_run": self.dry_run,
            "success": success,
            "steps_executed": self.steps_executed,
            "artifacts": {k: str(v) for k, v in self.artifacts.items()},
            "config": {
                "comfyui_prompt": args.prompt,
                "motion_prompt": args.motion_prompt,
                "dialogue_line": args.line,
                "voice": args.voice,
            },
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"\n✓ Logged to {log_file.relative_to(PROJECT_ROOT)}")

    def run(self, args: argparse.Namespace):
        """Execute the full pipeline."""
        self.print_header("Scene 01 Content Pipeline Orchestrator")

        # Mode banner
        if self.dry_run:
            print("🔍 DRY-RUN MODE (default)")
            print("   Validating inputs and showing step plan — no API calls will be made.")
            print("   Pass --live to execute actual pipeline with paid API calls.\n")
        else:
            print("⚡ LIVE MODE")
            print("   Executing full pipeline with actual API calls.\n")

        # Validate environment keys
        if not self.dry_run:
            print("\n[Validating Environment Keys]")
            print("-" * 50)
            keys_status = self.validate_env_keys()
            missing_keys = [k for k, v in keys_status.items() if not v]

            if missing_keys:
                print("\n  ERROR: Missing required environment variables:")
                for key in missing_keys:
                    print(f"    - {key}")
                print("\n  Set them via Doppler or export them manually:")
                print("    doppler run -- uv run shared/scripts/scene_01_pipeline.py ...")
                print("\n  Or add them in Cursor Dashboard: Cloud Agents > Secrets")
                sys.exit(1)

            print("  ✓ All required keys present:")
            for key in keys_status.keys():
                print(f"    - {key}")

        # Set up paths
        output_dir = OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        shot_suffix = f"shot{args.shot:02d}" if args.shot else "custom"

        # Step 1: ComfyUI still (or use provided still)
        if args.still:
            still_path = Path(args.still).resolve()
            print(f"\n[Using Provided Still]")
            print(f"  Path: {still_path}")
            if not still_path.exists() and not self.dry_run:
                print(f"\n  ERROR: Provided still not found: {still_path}")
                sys.exit(1)
        else:
            still_path = output_dir / f"scene_01_{shot_suffix}_base.png"
            self.step_comfyui_generate(args.prompt, still_path)

        # Step 2: Aurora I2V
        aurora_video = output_dir / f"scene_01_{shot_suffix}_video.mp4"
        self.step_aurora_video(still_path, args.motion_prompt, aurora_video)

        # Step 3: Voice swap (or use provided audio)
        if args.audio_input:
            recorded_audio = Path(args.audio_input).resolve()
            print(f"\n[Using Provided Audio]")
            print(f"  Path: {recorded_audio}")
            if not recorded_audio.exists() and not self.dry_run:
                print(f"\n  ERROR: Provided audio not found: {recorded_audio}")
                sys.exit(1)
            # Still do voice swap
            voice_audio = output_dir / f"scene_01_{shot_suffix}_voice.mp3"
            self.step_voice_swap(recorded_audio, args.voice, voice_audio)
        else:
            # Would need recorded audio - fail if not provided
            print(f"\n  ERROR: --audio-input required (pre-recorded dialogue line)")
            print(f"  Record dialogue line {args.line} and pass via --audio-input")
            sys.exit(1)

        # Step 4: PixVerse lip-sync
        final_output = Path(args.output) if args.output else output_dir / f"scene_01_{shot_suffix}_final.mp4"
        self.step_lipsync(
            aurora_video if not self.dry_run else Path("placeholder_video.mp4"),
            voice_audio if not self.dry_run else Path("placeholder_audio.mp3"),
            final_output,
        )

        # Summary
        self.print_header("Pipeline Summary")
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        print(f"Steps executed: {len(self.steps_executed)}")
        for step in self.steps_executed:
            print(f"  - {step[0]}: {step[1]}")

        if not self.dry_run:
            print(f"\nArtifacts:")
            for name, path in self.artifacts.items():
                print(f"  - {name}: {path}")
            print(f"\n✓ Final video: {final_output}")

            # Log the run
            self.log_pipeline_run(args, success=True)
        else:
            print("\n✓ Dry-run complete. All inputs validated.")
            print("  To execute the pipeline, re-run with --live flag.")

        print()


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end content pipeline: ComfyUI → Aurora → ElevenLabs → PixVerse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default): validate and show plan
  doppler run -- uv run shared/scripts/scene_01_pipeline.py \\
      --shot 11 \\
      --prompt "Flo at desk with drone, silhouette against window" \\
      --audio-input data/scenes/in_progress/recorded_line_3.m4a

  # Live mode: execute full pipeline
  doppler run -- uv run shared/scripts/scene_01_pipeline.py \\
      --shot 11 \\
      --prompt "Flo at desk with drone" \\
      --audio-input data/scenes/in_progress/recorded_line_3.m4a \\
      --live

  # Use pre-generated still:
  doppler run -- uv run shared/scripts/scene_01_pipeline.py \\
      --still data/scenes/in_progress/scene_01_shot_11_base.png \\
      --audio-input data/scenes/in_progress/recorded_line_3.m4a \\
      --live

Required Environment Variables (for --live):
  XAI_API_KEY          - xAI Aurora API key
  ELEVEN_LABS_API_KEY  - ElevenLabs API key
  PIXVERSE_API_KEY     - PixVerse API key

Set via Doppler:
  doppler run -- uv run shared/scripts/scene_01_pipeline.py ...

Or via Cursor Dashboard:
  Cloud Agents > Secrets
        """,
    )

    # Pipeline configuration
    parser.add_argument(
        "--shot",
        type=int,
        help="Scene 01 shot number (1-11, see scene_01_apartment_origin.md)",
    )
    parser.add_argument(
        "--prompt",
        default="Flo at desk in apartment, backlit by window",
        help="ComfyUI generation prompt for base still",
    )
    parser.add_argument(
        "--motion-prompt",
        default="Slow push-in, camera moves toward subject",
        help="Aurora motion prompt for I2V generation",
    )
    parser.add_argument(
        "--line",
        type=int,
        choices=[1, 2, 3],
        default=3,
        help="Dialogue line number (1-3, see Scene 01 doc)",
    )
    parser.add_argument(
        "--voice",
        default="matilda",
        help="ElevenLabs voice name (default: matilda)",
    )

    # Input overrides
    parser.add_argument(
        "--still",
        help="Path to pre-generated still image (skips ComfyUI step)",
    )
    parser.add_argument(
        "--audio-input",
        required=True,
        help="Path to recorded audio (human performance, pre-voice-swap)",
    )

    # Output
    parser.add_argument(
        "--output",
        help="Final output video path (default: output/scene_01/scene_01_shotXX_final.mp4)",
    )

    # Execution mode
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute pipeline with actual API calls (default: dry-run)",
    )

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = PipelineOrchestrator(dry_run=not args.live)

    try:
        orchestrator.run(args)
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Pipeline failed: {e}")
        if not orchestrator.dry_run:
            orchestrator.log_pipeline_run(args, success=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
