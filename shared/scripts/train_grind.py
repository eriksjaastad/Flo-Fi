#!/usr/bin/env python3
"""
Continuous training image grinder.
Queues batches of 10 to ComfyUI, waits for them to render, repeats forever.
Uses --train mode so all settings are locked. Kill with Ctrl+C to stop.

Usage:
    uv run shared/scripts/train_grind.py                    # Run forever, auto-detect start number
    uv run shared/scripts/train_grind.py --start 91         # Start from specific number
"""

import argparse
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE = PROJECT_ROOT / "data" / "generation_logs" / "generations.jsonl"
MISSION_CONTROL = PROJECT_ROOT / "shared" / "scripts" / "mission_control.py"
OUTPUT_DIR = PROJECT_ROOT / "tools" / "ComfyUI" / "output"

BATCH_SIZE = 10

OUTFITS = [
    "coral tank top",
    "white tee",
    "lavender tank top",
    "rust henley",
    "sage green tee",
    "peach tank top",
    "cream tee",
    "dusty rose tank top",
    "terracotta tee",
    "seafoam tank top",
    "sunset orange tee",
    "sky blue tank top",
    "butter yellow tee",
    "warm grey henley",
    "soft pink tee",
    "olive green tank top",
    "faded red tee",
    "lilac tank top",
    "burnt sienna tee",
    "light blue henley",
    "dusty purple tank top",
    "sand colored tee",
    "mauve tank top",
    "golden yellow tee",
    "robin egg blue tank top",
    "muted green tee",
    "rose tank top",
    "slate blue tee",
    "apricot tank top",
    "clay colored tee",
    "periwinkle tank top",
    "moss green tee",
    "blush pink tee",
    "copper tank top",
    "stone grey tee",
    "washed navy tee",
    "faded orange tank top",
    "earth tone tee",
    "pale green tank top",
    "vintage purple tee",
]


def get_last_number():
    """Read generation log and find the highest flo_train number."""
    max_num = 0
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    prefix = entry.get("filename_prefix", "")
                    m = re.match(r"flo_train_(\d+)_", prefix)
                    if m:
                        max_num = max(max_num, int(m.group(1)))
                except json.JSONDecodeError:
                    continue
    return max_num


def outfit_to_name(outfit):
    """Convert 'coral tank top' to 'coral_tank_top'."""
    return outfit.lower().replace(" ", "_")


def generate(num, outfit):
    """Queue one training image via mission_control.py --train."""
    name = outfit_to_name(outfit)
    prefix = f"flo_train_{num}_{name}"
    cmd = [
        sys.executable, str(MISSION_CONTROL),
        "generate-local",
        "--train",
        "--outfit", outfit,
        "--prefix", prefix,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [{num}] Queued: {prefix}")
    else:
        print(f"  [{num}] ERROR: {result.stderr.strip()}")
    return prefix


def wait_for_batch(prefixes):
    """Wait for all images in the batch to appear in the output directory."""
    remaining = set(prefixes)
    while remaining:
        done = set()
        for prefix in remaining:
            # ComfyUI saves as prefix_00001_.png
            matches = list(OUTPUT_DIR.glob(f"{prefix}_*.png"))
            if matches:
                done.add(prefix)
        remaining -= done
        if remaining:
            time.sleep(5)
    print(f"  All {len(prefixes)} rendered.")


def main():
    parser = argparse.ArgumentParser(description="Continuous training image grinder")
    parser.add_argument("--start", type=int, help="Starting number (default: auto from log)")
    args = parser.parse_args()

    start = args.start or (get_last_number() + 1)
    print(f"=== TRAIN GRIND ===")
    print(f"Starting from flo_train_{start}")
    print(f"Outfit pool: {len(OUTFITS)} options")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Ctrl+C to stop")
    print()

    num = start
    batch_num = 1
    used_outfits = []
    total = 0

    try:
        while True:
            print(f"--- Batch {batch_num} (flo_train_{num} - {num + BATCH_SIZE - 1}) ---")
            prefixes = []
            for _ in range(BATCH_SIZE):
                if not used_outfits:
                    used_outfits = random.sample(OUTFITS, len(OUTFITS))
                outfit = used_outfits.pop()
                prefix = generate(num, outfit)
                prefixes.append(prefix)
                num += 1
                total += 1

            print(f"  Waiting for renders...")
            wait_for_batch(prefixes)
            print(f"  Batch {batch_num} complete. Total queued: {total}")
            print()
            batch_num += 1
    except KeyboardInterrupt:
        print(f"\n\nStopped. Generated {total} images (flo_train_{start} through {num - 1})")


if __name__ == "__main__":
    main()
