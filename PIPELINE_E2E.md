# End-to-End Content Pipeline

Full orchestration for Scene 01 (Apartment Origin): **ComfyUI → Aurora → ElevenLabs → PixVerse → TikTok-ready video**

## Overview

`shared/scripts/scene_01_pipeline.py` wires together existing API clients to automate the complete content generation workflow:

1. **ComfyUI** — Generate base still image (training-locked character + scene preset)
2. **Aurora** — Image-to-video generation (xAI Grok Imagine Video)
3. **ElevenLabs** — Speech-to-speech voice replacement (human performance → Flo voice)
4. **PixVerse** — Lip-sync video + audio alignment

**Default mode: DRY-RUN.** The pipeline validates inputs, checks environment keys, and prints the full step plan without making any paid API calls. Pass `--live` to execute.

## Usage

### Quick Start (Dry-Run)

```bash
# Validate pipeline with Scene 01 shot 11
doppler run -- uv run shared/scripts/scene_01_pipeline.py --shot 11
```

**Expected output:**
- Full step-by-step plan with exact commands
- Exit 0 with "Dry-run complete" message
- Note about --image-url required for live Aurora

### Live Execution

```bash
# Execute full pipeline with actual API calls
doppler run -- uv run shared/scripts/scene_01_pipeline.py \
    --shot 11 \
    --image-url https://example.com/scene_01_shot_11_base.png \
    --audio-input data/scenes/in_progress/recorded_line_3.m4a \
    --live
```

**Requirements for `--live`:**
- All three API keys set via Doppler
- `--image-url` (HTTPS) for Aurora I2V
- `--audio-input` for recorded dialogue (human performance, not yet voice-swapped)

### Use Pre-Generated Assets

```bash
# Provide HTTPS URL to existing still for live Aurora I2V
doppler run -- uv run shared/scripts/scene_01_pipeline.py \
    --image-url https://r2.example.com/scene_01_shot_11_base.png \
    --audio-input data/scenes/in_progress/recorded_line_3.m4a \
    --live
```

### Custom Output Path

```bash
doppler run -- uv run shared/scripts/scene_01_pipeline.py \
    --shot 11 \
    --image-url https://r2.example.com/still.png \
    --audio-input data/scenes/in_progress/recorded_line_3.m4a \
    --output data/scenes/in_progress/scene_01_shot_11_final.mp4 \
    --live
```

## Pipeline Steps

### Step 1: ComfyUI Still Generation

**Status:** Dry-run stub (live execution requires ComfyUI server).

For CI/testing, provide a pre-generated still via `--still` flag. Full ComfyUI integration requires:
- ComfyUI server running at `localhost:8188` (start via `./shared/scripts/start_comfyui.sh`)
- Workflow submission via `mission_control.py generate-local`

**Workaround for live runs:** Generate stills separately, then pass via `--still`.

### Step 2: Aurora Image-to-Video

**Tool:** `shared/aurora.py` (xAI Grok Imagine Video API)

- Takes HTTPS image URL + motion prompt → 10s video clip at 720p
- **Requires HTTPS URL for live API calls** (pass via `--image-url`)
- Local paths only supported in dry-run mode
- Polls asynchronously until generation completes (default max wait: 5 minutes)

**Cost:** ~$0.10 per 10s video (check xAI pricing)

### Step 3: ElevenLabs Voice Swap

**Tool:** `shared/scripts/voice_swap.py` (speech-to-speech)

- Takes human-performed audio → replaces with target voice (default: `matilda`)
- Preserves inflection, pace, emotion (DO NOT use text-to-speech — TTS sounds flat)
- Model: `eleven_multilingual_sts_v2`

**Required input:** Pre-recorded dialogue line (`.m4a`, `.mp3`, `.wav`)

**Cost:** ~$0.30 per audio minute (check ElevenLabs pricing)

### Step 4: PixVerse Lip-Sync

**Tool:** `shared/pixverse.py` (PixVerse lip-sync API)

- Takes video from Aurora + voice-swapped audio → lip-synced final video
- Uploads both to PixVerse, polls for completion, downloads result
- Typical processing time: 3-8 minutes

**Cost:** Varies by video length (check PixVerse pricing)

## Environment Variables

All API keys required for `--live` mode:

| Variable | Purpose | Set via Doppler |
|----------|---------|----------------|
| `XAI_API_KEY` | xAI Aurora video generation | ✓ |
| `ELEVEN_LABS_API_KEY` | ElevenLabs voice swap | ✓ |
| `PIXVERSE_API_KEY` | PixVerse lip-sync | ✓ |

**Doppler command:**
```bash
doppler run -- uv run shared/scripts/scene_01_pipeline.py ...
```

**Alternative:** Cursor Cloud Agents can read secrets from Cursor Dashboard (Cloud Agents > Secrets) as a secondary option.

## Experiment Logging

Pipeline runs are logged to `data/experiment_log.jsonl` **only on successful completion** in `--live` mode.

**Log entry schema:**
```json
{
  "date": "2026-09-18",
  "timestamp": "2026-09-18T05:40:00Z",
  "id": "pipeline_scene01_shot11_1726635600",
  "tool": "scene_01_pipeline",
  "scene": "scene_01_apartment_origin",
  "shot": 11,
  "dry_run": false,
  "success": true,
  "steps_executed": [
    ["aurora", "completed", "req-abc123"],
    ["voice_swap", "completed"],
    ["pixverse", "completed"]
  ],
  "artifacts": {
    "aurora_video": "output/scene_01/scene_01_shot11_video.mp4",
    "voice_audio": "output/scene_01/scene_01_shot11_voice.mp3",
    "final_video": "output/scene_01/scene_01_shot11_final.mp4"
  },
  "config": {
    "comfyui_prompt": "Flo at desk with drone",
    "motion_prompt": "Slow push-in, camera moves toward subject",
    "dialogue_line": 3,
    "voice": "matilda"
  }
}
```

**Dry-run logging:** None. Dry-runs do NOT write to `experiment_log.jsonl` (avoids log pollution).

## Failure Modes

### Missing API Key (Live Mode)

```
ERROR: Missing required environment variables:
  - XAI_API_KEY

Set them via Doppler:
  doppler run -- uv run shared/scripts/scene_01_pipeline.py ...
```

**Exit code:** 1

### Missing Input File

```
ERROR: --audio-input required for live mode
Record dialogue line and pass via --audio-input
```

**Exit code:** 1

### Missing Image URL for Live Aurora

```
ERROR: --image-url (HTTPS) required for live Aurora I2V.
Aurora API does not accept local file paths.

Options:
  1. Upload still to public/signed HTTPS URL and pass via --image-url
  2. Use --dry-run to test with local paths
```

**Exit code:** 1

### Aurora Generation Timeout

Aurora video generation timed out after waiting max_wait seconds. The video may still be processing.

**Workaround:** Check status manually via `mission_control.py aurora-video --status <request_id>`.

## Integration with Scene 01

Scene 01 (Apartment Origin) has 11 shots. Each shot requires:
- Base still (Midjourney or ComfyUI with v20_04 Omni Reference)
- Motion prompt for Aurora I2V
- Dialogue line (1, 2, or 3 — see `data/scenes/backlog/scene_01_apartment_origin.md`)

**Shots with dialogue:**
- Shot 2: Line 1 ("Oh hi, Mom...")
- Shot 9: Line 2 ("Okay Mom, I'm sending you a text link...")
- Shot 11: Line 3 ("I can automatically send you a text link...")

**Pipeline workflow per shot:**
1. Record dialogue line (human performance with emotion)
2. Run pipeline with `--shot N --audio-input recorded_line_N.m4a --live`
3. Final video → `output/scene_01/scene_01_shotNN_final.mp4`
4. Move to `data/scenes/in_progress/` for review

## See Also

- **Scene 01 storyboard:** `data/scenes/backlog/scene_01_apartment_origin.md`
- **Aurora README:** `shared/AURORA_README.md`
- **PixVerse integration:** `docs/pixverse_integration.md`
- **Voice swap examples:** `shared/scripts/voice_swap.py --list-voices`
- **Experiment log format:** `data/experiment_log.jsonl`
