#!/usr/bin/env python3
"""
Speech-to-speech voice replacement via ElevenLabs.
Takes a recording of you performing a line, returns the same performance
in a target voice. Preserves inflection, pace, and emotion.

Usage:
    doppler run -- uv run shared/scripts/voice_swap.py INPUT.m4a [--voice NAME] [--out PATH]

    # List available stock voices:
    doppler run -- uv run shared/scripts/voice_swap.py --list-voices
"""

import argparse
import os
import sys
from pathlib import Path

import requests

# Curated stock voices worth trying for Flo (young, warm, American/English).
# Full library: https://elevenlabs.io/app/voice-library
STOCK_VOICES = {
    "rachel":  ("21m00Tcm4TlvDq8ikWAM", "Calm, young, warm American female"),
    "bella":   ("EXAVITQu4vr4xnSDxMaL", "Soft, young American female"),
    "domi":    ("AZnzlk1XvdvUeBnXmlld", "Strong, confident young American female"),
    "freya":   ("jsCqWAovK2LkecY7zXl4", "Expressive young American female"),
    "grace":   ("oWAxZDx7w5VEj9dCyTzz", "Gentle, warm Southern American female"),
    "matilda": ("XrExE9yKIg1WjnnlVkGX", "Friendly, warm American female"),
}

DEFAULT_VOICE = "matilda"
MODEL_ID = "eleven_multilingual_sts_v2"  # multilingual sts handles m4a well
API_URL = "https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}"


def list_voices():
    print("Curated stock voices for Flo testing:\n")
    for name, (vid, desc) in STOCK_VOICES.items():
        marker = " (default)" if name == DEFAULT_VOICE else ""
        print(f"  {name:10s}{marker}")
        print(f"    id:   {vid}")
        print(f"    desc: {desc}")
    print(f"\nUsage: --voice {DEFAULT_VOICE}")


def swap(input_path: Path, voice_name: str, out_path: Path) -> Path:
    api_key = os.environ.get("ELEVEN_LABS_API_KEY")
    if not api_key:
        sys.exit("ERROR: ELEVEN_LABS_API_KEY not set. Run via: doppler run -- uv run ...")

    if voice_name not in STOCK_VOICES:
        sys.exit(f"ERROR: unknown voice '{voice_name}'. Try --list-voices.")
    voice_id, desc = STOCK_VOICES[voice_name]

    if not input_path.exists():
        sys.exit(f"ERROR: input file not found: {input_path}")

    print(f"Input:  {input_path}")
    print(f"Voice:  {voice_name} ({desc})")
    print(f"Model:  {MODEL_ID}")
    print("Uploading and processing...")

    with open(input_path, "rb") as f:
        response = requests.post(
            API_URL.format(voice_id=voice_id),
            headers={"xi-api-key": api_key, "accept": "audio/mpeg"},
            data={
                "model_id": MODEL_ID,
                "voice_settings": '{"stability": 0.5, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": true}',
            },
            files={"audio": (input_path.name, f, "audio/mp4")},
            timeout=180,
        )

    if response.status_code != 200:
        sys.exit(f"ERROR: ElevenLabs API returned {response.status_code}: {response.text}")

    out_path.write_bytes(response.content)
    size_kb = len(response.content) / 1024
    print(f"\nSaved: {out_path} ({size_kb:.1f} KB)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Voice swap via ElevenLabs speech-to-speech")
    parser.add_argument("input", nargs="?", help="Input audio file (.m4a, .mp3, .wav)")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Target voice name (default: {DEFAULT_VOICE})")
    parser.add_argument("--out", help="Output path (default: <input>_<voice>.mp3)")
    parser.add_argument("--list-voices", action="store_true", help="List curated stock voices and exit")
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return

    if not args.input:
        parser.print_help()
        sys.exit("\nERROR: input file required (or use --list-voices)")

    input_path = Path(args.input).expanduser().resolve()
    if args.out:
        out_path = Path(args.out).expanduser().resolve()
    else:
        out_path = input_path.parent / f"{input_path.stem}_{args.voice}.mp3"

    swap(input_path, args.voice, out_path)


if __name__ == "__main__":
    main()
