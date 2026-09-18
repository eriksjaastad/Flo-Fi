#!/usr/bin/env python3
"""
Auto-log generation experiments to experiment_log.jsonl.
Called by Claude Code hook after any mission_control.py generate command.

Reads the last entry from generations.jsonl and appends a JSONL entry to experiment_log.jsonl
with all technical details. Intention/strategy/result columns are left as "pending"
for the agent to fill in during conversation.

Usage:
    python3 log_experiment.py [--intention "what we're trying"] [--strategy "approach used"]
    python3 log_experiment.py --tool midjourney --id "flo_mj_001" --prompt "..." [options]
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE = PROJECT_ROOT / "data" / "generation_logs" / "generations.jsonl"
EXPERIMENT_LOG = PROJECT_ROOT / "data" / "experiment_log.jsonl"


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


def ensure_experiment_log_exists():
    """Create experiment_log.jsonl parent directory if needed."""
    if not EXPERIMENT_LOG.exists():
        EXPERIMENT_LOG.parent.mkdir(parents=True, exist_ok=True)


def check_already_logged(experiment_id):
    """Check if this experiment ID was already logged."""
    if not EXPERIMENT_LOG.exists():
        return False
    
    with open(EXPERIMENT_LOG, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("id") == experiment_id:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def log_comfyui_generation(intention="pending", strategy="pending"):
    """Append the latest ComfyUI generation to experiment_log.jsonl."""
    entry = get_last_generation()
    if not entry:
        print("No generation found in log.")
        return

    ensure_experiment_log_exists()

    prefix = entry.get("filename_prefix", "unknown")
    
    # Check if already logged
    if check_already_logged(prefix):
        print(f"Already logged: {prefix}")
        return

    resolution = entry.get("resolution", [0, 0])
    res_str = f"{resolution[0]}x{resolution[1]}" if isinstance(resolution, list) else str(resolution)
    
    lora = entry.get("lora", "")
    lora_strength = entry.get("lora_strength", "")
    
    experiment_entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "id": prefix,
        "tool": "comfyui",
        "intention": intention,
        "strategy": strategy,
        "expectation": "",
        "result_quality": "",
        "result_notes": "",
        "lesson_learned": "",
        "fix_for_next_time": "",
        "keeper": "",
        "settings": {
            "model": entry.get("checkpoint", "unknown"),
            "lora": f"{lora} @ {lora_strength}" if lora else "",
            "lora_strength": lora_strength,
            "seed": entry.get("seed", ""),
            "positive_prompt": entry.get("prompt", "")[:200] + "..." if len(entry.get("prompt", "")) > 200 else entry.get("prompt", ""),
            "negative_prompt": entry.get("negative_prompt", "")[:200] + "..." if len(entry.get("negative_prompt", "")) > 200 else entry.get("negative_prompt", ""),
            "resolution": res_str,
            "cfg_scale": entry.get("cfg_scale", "pending"),
            "steps": entry.get("steps", "pending"),
            "sampler": entry.get("sampler", "pending"),
        }
    }

    with open(EXPERIMENT_LOG, "a") as f:
        f.write(json.dumps(experiment_entry) + "\n")

    print(f"Logged: {prefix} | {entry.get('checkpoint', '?')} | seed {entry.get('seed', '?')}")


def log_midjourney(
    experiment_id,
    prompt,
    stylize=None,
    weird=None,
    aspect_ratio=None,
    anchor_image=None,
    intention="pending",
    strategy="pending",
    expectation="",
    result_quality="",
    result_notes="",
    keeper=""
):
    """Log a Midjourney generation to experiment_log.jsonl."""
    ensure_experiment_log_exists()
    
    if check_already_logged(experiment_id):
        print(f"Already logged: {experiment_id}")
        return
    
    settings = {
        "prompt": prompt,
        "stylize": stylize or "",
        "weird": weird or "",
        "aspect_ratio": aspect_ratio or "",
        "anchor_image": anchor_image or "",
    }
    
    experiment_entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "id": experiment_id,
        "tool": "midjourney",
        "intention": intention,
        "strategy": strategy,
        "expectation": expectation,
        "result_quality": result_quality,
        "result_notes": result_notes,
        "lesson_learned": "",
        "fix_for_next_time": "",
        "keeper": keeper,
        "settings": settings
    }
    
    with open(EXPERIMENT_LOG, "a") as f:
        f.write(json.dumps(experiment_entry) + "\n")
    
    print(f"Logged Midjourney: {experiment_id}")


if __name__ == "__main__":
    args = sys.argv[1:]
    
    # Parse args
    tool = None
    experiment_id = None
    prompt = None
    stylize = None
    weird = None
    aspect_ratio = None
    anchor_image = None
    intention = "pending"
    strategy = "pending"
    expectation = ""
    result_quality = ""
    result_notes = ""
    keeper = ""
    
    i = 0
    while i < len(args):
        if args[i] == "--tool" and i + 1 < len(args):
            tool = args[i + 1]
            i += 2
        elif args[i] == "--id" and i + 1 < len(args):
            experiment_id = args[i + 1]
            i += 2
        elif args[i] == "--prompt" and i + 1 < len(args):
            prompt = args[i + 1]
            i += 2
        elif args[i] == "--stylize" and i + 1 < len(args):
            stylize = args[i + 1]
            i += 2
        elif args[i] == "--weird" and i + 1 < len(args):
            weird = args[i + 1]
            i += 2
        elif args[i] == "--ar" and i + 1 < len(args):
            aspect_ratio = args[i + 1]
            i += 2
        elif args[i] == "--anchor" and i + 1 < len(args):
            anchor_image = args[i + 1]
            i += 2
        elif args[i] == "--intention" and i + 1 < len(args):
            intention = args[i + 1]
            i += 2
        elif args[i] == "--strategy" and i + 1 < len(args):
            strategy = args[i + 1]
            i += 2
        elif args[i] == "--expectation" and i + 1 < len(args):
            expectation = args[i + 1]
            i += 2
        elif args[i] == "--result-quality" and i + 1 < len(args):
            result_quality = args[i + 1]
            i += 2
        elif args[i] == "--result-notes" and i + 1 < len(args):
            result_notes = args[i + 1]
            i += 2
        elif args[i] == "--keeper" and i + 1 < len(args):
            keeper = args[i + 1]
            i += 2
        else:
            i += 1
    
    if tool == "midjourney":
        if not experiment_id or not prompt:
            print("Error: --id and --prompt required for Midjourney logging")
            sys.exit(1)
        log_midjourney(
            experiment_id=experiment_id,
            prompt=prompt,
            stylize=stylize,
            weird=weird,
            aspect_ratio=aspect_ratio,
            anchor_image=anchor_image,
            intention=intention,
            strategy=strategy,
            expectation=expectation,
            result_quality=result_quality,
            result_notes=result_notes,
            keeper=keeper
        )
    else:
        # Default: log from generations.jsonl (ComfyUI)
        log_comfyui_generation(intention=intention, strategy=strategy)
