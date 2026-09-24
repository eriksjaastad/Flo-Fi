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

import argparse
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
        print("Error: No generation found in log.", file=sys.stderr)
        sys.exit(1)

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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
    reaction=None,
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "id": experiment_id,
        "tool": "midjourney",
        "intention": intention,
        "strategy": strategy,
        "expectation": expectation,
        "result_quality": result_quality,
        "result_notes": result_notes,
        "reaction": reaction or "",
        "lesson_learned": "",
        "fix_for_next_time": "",
        "keeper": keeper,
        "settings": settings
    }
    
    with open(EXPERIMENT_LOG, "a") as f:
        f.write(json.dumps(experiment_entry) + "\n")
    
    print(f"Logged Midjourney: {experiment_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Log generation experiments to experiment_log.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log last ComfyUI generation
  python3 log_experiment.py --intention "test v20_04" --strategy "locked prompt"
  
  # Log Midjourney generation
  python3 log_experiment.py --tool midjourney --id flo_mj_001 --prompt "flo at sunset" \\
    --ow 50 --ar 16:9 --reaction "eyes too wide" --keeper yes
"""
    )
    
    parser.add_argument("--tool", choices=["comfyui", "midjourney"], 
                        help="Generation tool (default: comfyui)")
    parser.add_argument("--id", help="Experiment ID (required for Midjourney)")
    parser.add_argument("--prompt", help="Generation prompt (required for Midjourney)")
    parser.add_argument("--stylize", help="Midjourney stylize value")
    parser.add_argument("--weird", "--ow", dest="weird", help="Midjourney weird/ow value")
    parser.add_argument("--ar", dest="aspect_ratio", help="Midjourney aspect ratio (e.g. 16:9)")
    parser.add_argument("--anchor", dest="anchor_image", help="Midjourney anchor/reference image path")
    parser.add_argument("--reaction", help="Initial reaction notes")
    parser.add_argument("--intention", default="pending", help="What we're trying to achieve")
    parser.add_argument("--strategy", default="pending", help="Approach being used")
    parser.add_argument("--expectation", default="", help="Expected outcome")
    parser.add_argument("--result-quality", default="", help="Quality rating")
    parser.add_argument("--result-notes", default="", help="Result notes")
    parser.add_argument("--keeper", default="", help="Keep this result? (yes/no)")
    
    args = parser.parse_args()
    
    # Validate tool-specific requirements
    tool = args.tool or "comfyui"
    
    if tool not in ["comfyui", "midjourney"]:
        print(f"Error: Unknown tool '{tool}'. Must be 'comfyui' or 'midjourney'.", file=sys.stderr)
        sys.exit(1)
    
    if tool == "midjourney":
        if not args.id or not args.prompt:
            print("Error: --id and --prompt required for Midjourney logging", file=sys.stderr)
            sys.exit(1)
        log_midjourney(
            experiment_id=args.id,
            prompt=args.prompt,
            stylize=args.stylize,
            weird=args.weird,
            aspect_ratio=args.aspect_ratio,
            anchor_image=args.anchor_image,
            reaction=args.reaction,
            intention=args.intention,
            strategy=args.strategy,
            expectation=args.expectation,
            result_quality=args.result_quality,
            result_notes=args.result_notes,
            keeper=args.keeper
        )
    else:
        # Default: log from generations.jsonl (ComfyUI)
        log_comfyui_generation(intention=args.intention, strategy=args.strategy)
