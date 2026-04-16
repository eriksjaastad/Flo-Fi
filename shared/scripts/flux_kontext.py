#!/usr/bin/env python3
"""
Flux Kontext Pro — Reference-based character consistency via fal.ai API.
Feed it a reference image of Flo + a text instruction → get a variation that preserves her face.

Usage:
    uv run shared/scripts/flux_kontext.py --reference tools/ComfyUI/output/v20_04_realcartoon_warm_00001_.png \
        --prompt "same girl wearing an orange hoodie, close-up portrait, golden hour lighting" \
        --output tools/ComfyUI/output/v26_01_kontext_hoodie.png

    # Batch mode:
    uv run shared/scripts/flux_kontext.py --reference v20_04.png --prompt-file prompts.txt --prefix v26
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / "data" / "generation_logs"
LOG_FILE = LOG_DIR / "generations.jsonl"

FAL_API_KEY = os.environ.get("FAL_AI_API_KEY")
KONTEXT_ENDPOINT = "https://fal.run/fal-ai/flux-pro/kontext"

# Cost per image (fal.ai pricing)
COST_PER_IMAGE = 0.04


def upload_image_to_fal(image_path):
    """Upload a local image to fal.ai storage and return the URL."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    suffix = path.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(suffix, "image/png")

    with open(path, "rb") as f:
        image_data = f.read()

    # Use fal.ai REST upload endpoint
    req = urllib.request.Request(
        f"https://fal.run/fal-ai/fal-file-upload/upload",
        data=image_data,
        headers={
            "Content-Type": mime,
            "Authorization": f"Key {FAL_API_KEY}",
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    url = result.get("url") or result.get("file_url") or result.get("access_url")
    if not url:
        # Some endpoints return the URL directly as a string
        if isinstance(result, str):
            url = result
        else:
            raise ValueError(f"No URL in upload response: {result}")
    print(f"Uploaded reference image: {url[:80]}...")
    return url


def encode_image_to_data_url(image_path):
    """Convert a local image file to a data URL for the API (fallback)."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    suffix = path.suffix.lower()
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(suffix, "image/png")
    return f"data:{mime};base64,{data}"


def submit_generation(reference_image, prompt, seed=None, guidance_scale=None, output_format="png"):
    """Submit a Kontext generation request to fal.ai queue."""
    if not FAL_API_KEY:
        print("Error: FAL_AI_API_KEY not set. Get it from Doppler: doppler secrets get FAL_AI_API_KEY --project flo-fi --config prd --plain")
        sys.exit(1)

    # Encode reference image as data URL
    print(f"Encoding reference image: {reference_image}")
    image_url = encode_image_to_data_url(reference_image)

    payload = {
        "prompt": prompt,
        "image_url": image_url,
        "output_format": output_format,
    }

    if seed is not None:
        payload["seed"] = seed
    if guidance_scale is not None:
        payload["guidance_scale"] = guidance_scale

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        KONTEXT_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Key {FAL_API_KEY}",
        },
    )

    print("Submitting to Flux Kontext Pro (sync — may take 30-60s)...")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = json.loads(resp.read())
        print("Generation complete!")
        return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {error_body[:500]}")
        return None


def poll_result(request_id, timeout=120):
    """Poll for generation result."""
    base = "https://queue.fal.run/fal-ai/flux-pro/kontext/requests"
    status_url = f"{base}/{request_id}/status"
    result_url = f"{base}/{request_id}"

    # Debug: try both URL patterns
    print(f"Polling: {status_url}")

    start = time.time()
    while time.time() - start < timeout:
        req = urllib.request.Request(
            status_url,
            headers={"Authorization": f"Key {FAL_API_KEY}"},
            method="GET",
        )
        try:
            resp = urllib.request.urlopen(req)
            status_data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            print(f"Poll error HTTP {e.code}: {error_body[:200]}")
            time.sleep(3)
            continue

        status = status_data.get("status")

        if status == "COMPLETED":
            # Fetch the actual result
            req = urllib.request.Request(
                result_url,
                headers={"Authorization": f"Key {FAL_API_KEY}"},
                method="GET",
            )
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        elif status in ("FAILED", "CANCELLED"):
            print(f"Generation failed: {status_data}")
            return None

        time.sleep(2)

    print(f"Timeout after {timeout}s")
    return None


def download_image(url, output_path):
    """Download generated image."""
    import subprocess
    result = subprocess.run(["curl", "-sL", "-o", str(output_path), url], capture_output=True)
    if result.returncode == 0:
        print(f"Saved: {output_path}")
    else:
        print(f"Download failed: {result.stderr.decode()}")


def log_generation(entry):
    """Append to the shared generation log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry["logged_at"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def generate(reference_image, prompt, output_path, seed=None, guidance_scale=None):
    """Full generation flow: submit (sync), download, log."""
    result = submit_generation(reference_image, prompt, seed=seed, guidance_scale=guidance_scale)
    if not result:
        return False

    images = result.get("images", [])
    if not images:
        print("No images in result")
        return False

    image_url = images[0].get("url")
    if not image_url:
        print("No URL in result")
        return False

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    download_image(image_url, output_path)

    # Log it
    log_entry = {
        "prompt_id": result.get("request_id", "sync"),
        "target": "flux-kontext-pro",
        "filename_prefix": output_path.stem,
        "prompt": prompt,
        "reference_image": str(reference_image),
        "checkpoint": "flux-pro-kontext",
        "seed": seed or "random",
        "cost_usd": COST_PER_IMAGE,
        "resolution": [1024, 1024],  # Kontext default
    }
    log_generation(log_entry)

    print(f"Cost: ${COST_PER_IMAGE:.3f}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Flux Kontext Pro — reference-based character generation")
    parser.add_argument("--reference", required=True, help="Path to reference image (Flo's face)")
    parser.add_argument("--prompt", help="Text instruction for what to generate/change")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--prefix", help="Output prefix (auto-generates filename)")
    parser.add_argument("--seed", type=int, help="Optional seed for reproducibility")
    parser.add_argument("--guidance-scale", type=float, help="Guidance scale (default: model default)")
    parser.add_argument("--prompt-file", help="File with one prompt per line for batch mode")

    args = parser.parse_args()

    if args.prompt_file:
        # Batch mode
        prompts = Path(args.prompt_file).read_text().strip().split("\n")
        prefix = args.prefix or "kontext"
        output_dir = PROJECT_ROOT / "tools" / "ComfyUI" / "output"

        total_cost = 0
        for i, prompt in enumerate(prompts, 1):
            prompt = prompt.strip()
            if not prompt or prompt.startswith("#"):
                continue
            output_path = output_dir / f"{prefix}_{i:02d}.png"
            print(f"\n[{i}/{len(prompts)}] {prompt[:80]}...")
            if generate(args.reference, prompt, output_path, seed=args.seed, guidance_scale=args.guidance_scale):
                total_cost += COST_PER_IMAGE

        print(f"\nBatch complete. Total cost: ${total_cost:.2f}")

    elif args.prompt:
        output_path = args.output or str(PROJECT_ROOT / "tools" / "ComfyUI" / "output" / f"{args.prefix or 'kontext'}_01.png")
        generate(args.reference, args.prompt, output_path, seed=args.seed, guidance_scale=args.guidance_scale)

    else:
        parser.error("Either --prompt or --prompt-file is required")


if __name__ == "__main__":
    main()
