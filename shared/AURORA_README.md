# Aurora / Grok Imagine Video Integration

xAI video generation client for flo-fi. Generates videos from text prompts or starting images.

## Setup

Set your xAI API key via Doppler:

```bash
doppler secrets set XAI_API_KEY
```

Or export directly:

```bash
export XAI_API_KEY='your-key-here'
```

For cloud agents, you can optionally add it to Cursor Cloud Agent secrets in the dashboard.

## Usage

### Text-to-Video

Generate video from a text prompt only:

```bash
./shared/scripts/mission_control.py aurora-video \
  --prompt "Cinematic aerial drone shot over beach at sunset" \
  --duration 10 \
  --resolution 1080p \
  --aspect-ratio 16:9 \
  --output output/aurora/drone_shot.mp4
```

### Image-to-Video

Animate a still image:

```bash
./shared/scripts/mission_control.py aurora-video \
  --image data/scenes/desert-sunset/flo_frame_001.png \
  --prompt "Slow camera push-in, embers drift across frame, hair stirs in wind" \
  --duration 12 \
  --resolution 720p \
  --output output/aurora/flo_scene_01.mp4
```

### Storyboard → Video

For multi-image storyboards, run image-to-video on each keyframe separately. The client doesn't support multi-image input (xAI API limitation).

### Dry Run

Test without API key or making real calls:

```bash
./shared/scripts/mission_control.py aurora-video \
  --prompt "Test prompt" \
  --duration 5 \
  --dry-run
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--prompt` | Text describing motion/action | Required (or `--image`) |
| `--image` | Starting image path (for I2V) | None |
| `--model` | Model name | `grok-imagine-video-1.5` |
| `--duration` | Video length in seconds (1-15) | 8 |
| `--resolution` | Output quality (480p/720p/1080p) | 720p |
| `--aspect-ratio` | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3 | None |
| `--output` | Local save path | None (URL only) |
| `--no-wait` | Submit and return immediately | False |
| `--poll-interval` | Seconds between status checks | 5 |
| `--max-wait` | Max wait time in seconds | 300 |
| `--dry-run` | Validate without API calls | False |

## Architecture

- `shared/aurora.py` — Thin wrapper around xAI's REST API
- `mission_control.py aurora-video` — CLI integration
- All generations logged to `data/experiment_log.jsonl` with tool `aurora`

## Experiment Logging

Every successful generation (including dry runs) appends to `data/experiment_log.jsonl`:

```json
{
  "date": "2026-09-18",
  "id": "3f23cc64",
  "timestamp": "2026-09-18T05:23:13.080856+00:00",
  "tool": "aurora",
  "model": "grok-imagine-video-1.5",
  "prompt": "Cinematic aerial drone shot over beach at golden hour",
  "image": null,
  "duration": 8,
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "request_id": "req_abc123",
  "video_url": "https://...",
  "local_path": "output/aurora/test.mp4",
  "dry_run": false
}
```

## Safety

- Client exits with error if `XAI_API_KEY` is missing (unless `--dry-run`)
- No secrets are committed to the repo
- Dry-run mode validates all inputs without API calls
- File path validation before upload attempts

## xAI API Reference

- Endpoint: `https://api.x.ai/v1/videos/generations`
- Docs: https://docs.x.ai/developers/model-capabilities/video/generation
- Model: `grok-imagine-video-1.5`
- Native 1080p on text-to-video and image-to-video
- Duration range: 1-15 seconds
- Async polling: POST → `request_id` → GET `/videos/{request_id}` until `status: "done"`

## Fallback Strategy

Per PROGRESS.md, Midjourney is the primary generator. Aurora is the fallback for:

- Video generation (Midjourney doesn't do video)
- Storyboard keyframe animation
- Testing video pipeline before committing to paid API runs

PixVerse integration comes next (separate PR) for multi-tool video redundancy.
