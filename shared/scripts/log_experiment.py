#!/usr/bin/env python3
"""
Auto-log generation experiments to experiment_log.csv.
Called by Claude Code hook after any mission_control.py generate command.

Reads the last entry from generations.jsonl and appends a row to experiment_log.csv
with all technical details. Intention/strategy/result columns are left as "pending"
for the agent to fill in during conversation.

Usage:
    python3 log_experiment.py [--intention "what we're trying"] [--strategy "approach used"]
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE = PROJECT_ROOT / "data" / "generation_logs" / "generations.jsonl"
CSV_FILE = PROJECT_ROOT / "data" / "experiment_log.csv"

CSV_HEADERS = [
    "date", "version", "intention", "strategy", "model", "lora", "seed",
    "key_prompt_changes", "negative_changes", "resolution",
    "result_quality", "result_notes", "lesson_learned"
]


def get_last_generation():
    """Read the most recent entry from generations.jsonl."""
    if not LOG_FILE.exists():
        return None

    last_line = None
    with open(LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                last_line = line

    if last_line:
        return json.loads(last_line)
    return None


def ensure_csv_exists():
    """Create CSV with headers if it doesn't exist."""
    if not CSV_FILE.exists():
        CSV_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def extract_lora_info(entry):
    """Extract LoRA name and strength from generation entry."""
    lora = entry.get("lora")
    if lora:
        strength = entry.get("lora_strength", "?")
        return f"{lora} @ {strength}"
    return "none"


def extract_notable_prompt_changes(prompt):
    """Pull out non-standard elements from the prompt for quick scanning."""
    if len(prompt) > 300:
        return prompt[:300] + "..."
    return prompt


def log_generation(intention="pending", strategy="pending"):
    """Append the latest generation to experiment_log.csv."""
    entry = get_last_generation()
    if not entry:
        print("No generation found in log.")
        return

    ensure_csv_exists()

    # Check if this prompt_id was already logged (prevent duplicates)
    prompt_id = entry.get("prompt_id", "")
    if CSV_FILE.exists() and prompt_id:
        with open(CSV_FILE, "r") as f:
            content = f.read()
            if prompt_id in content:
                print(f"Already logged: {prompt_id}")
                return

    prefix = entry.get("filename_prefix", "unknown")
    resolution = entry.get("resolution", [0, 0])

    row = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "version": prefix,
        "intention": intention,
        "strategy": strategy,
        "model": entry.get("checkpoint", entry.get("target", "unknown")),
        "lora": extract_lora_info(entry),
        "seed": entry.get("seed", "N/A"),
        "key_prompt_changes": extract_notable_prompt_changes(entry.get("prompt", "")),
        "negative_changes": entry.get("negative_prompt", "")[:200],
        "resolution": f"{resolution[0]}x{resolution[1]}" if isinstance(resolution, list) else str(resolution),
        "result_quality": "pending",
        "result_notes": "pending",
        "lesson_learned": "pending"
    }

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)

    print(f"Logged: {prefix} | {entry.get('checkpoint', '?')} | seed {entry.get('seed', '?')} | LoRA: {extract_lora_info(entry)}")


if __name__ == "__main__":
    intention = "pending"
    strategy = "pending"

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--intention" and i + 1 < len(args):
            intention = args[i + 1]
            i += 2
        elif args[i] == "--strategy" and i + 1 < len(args):
            strategy = args[i + 1]
            i += 2
        else:
            i += 1

    log_generation(intention=intention, strategy=strategy)
