# PixVerse Lip-Sync Integration

Phase 3 video pipeline component for lip-sync: video + audio → lip-synced output.

## Components

### `shared/pixverse.py`
Shared PixVerse API client. Handles:
- Media upload (video + audio)
- Lip-sync job submission
- Status polling
- Result download
- Experiment logging

### `shared/scripts/scene_01_lipsync.py`
Scene 01–oriented consumer that calls the shared client. Wires the PixVerse client for the Scene 01 (Apartment Origin) workflow.

## Setup

### 1. Get API Key
Sign up at [PixVerse Platform](https://platform.pixverse.ai/) and get an API key from the dashboard.

### 2. Add to Doppler
Store the key in Doppler as `PIXVERSE_API_KEY`:

```bash
doppler secrets set PIXVERSE_API_KEY="your-key-here"
```

The key is injected at runtime — **never commit it to the repo**.

## Usage

### Basic Lip-Sync (shared client)
```bash
doppler run -- uv run shared/pixverse.py video.mp4 audio.mp3 --out synced.mp4
```

### Scene 01 Workflow
```bash
# Full pipeline for Scene 01 shot 11 (Drone POV):
doppler run -- uv run shared/scripts/scene_01_lipsync.py \
    --video data/scenes/in_progress/scene_01_shot_11_drone_pov.mp4 \
    --audio data/scenes/in_progress/scene_01_line_3_flo_voice.mp3 \
    --out data/scenes/in_progress/scene_01_shot_11_synced.mp4
```

### Help
```bash
python3 shared/pixverse.py --help
python3 shared/scripts/scene_01_lipsync.py --help
```

## API Details

- **Endpoint**: `https://app-api.pixverse.ai/openapi/v2/video/lip_sync/generate`
- **Docs**: [PixVerse Lip-Sync Docs](https://docs.platform.pixverse.ai/speechlip-sync-1268530m0)
- **Max video**: 100MB, 1920px resolution, 60s duration
- **Max audio**: 100MB, 60s duration
- **Formats**: Video (mp4/mov/webm), Audio (mp3/wav/m4a/aac)

## Logging

Successful runs are logged to `data/experiment_log.jsonl` with:
- Tool: `pixverse`
- Date, timestamp (ISO format)
- Input/output filenames
- PixVerse video_id
- Output URL

Use `--no-log` to skip logging (e.g., for testing).

## Error Handling

The client exits with status 1 when:
- `PIXVERSE_API_KEY` is not set
- Input files don't exist
- Upload fails
- Generation fails (status 8)
- Content moderation blocks video (status 7)
- Timeout after 10 minutes

## Phase 3 Pipeline

Scene 01 full workflow:
1. **Generate video clip** — Midjourney/Grok Aurora
2. **Record dialogue** — Human performance with emotion
3. **Voice swap** — `voice_swap.py` (ElevenLabs speech-to-speech)
4. **Lip-sync** — `scene_01_lipsync.py` (PixVerse) ← this integration

## Cards

- **#5434**: PixVerse lip-sync API (shared client) — `shared/pixverse.py`
- **#5953**: Scene 01 consumer — `shared/scripts/scene_01_lipsync.py`
