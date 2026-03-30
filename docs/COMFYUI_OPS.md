# ComfyUI Operations Guide

## 1. Starting ComfyUI

```bash
./shared/scripts/start_comfyui.sh
```

- Runs on `http://127.0.0.1:8188`
- Uses `--force-fp16` for Apple Silicon performance
- Blocks the terminal — run in a background tab or use `&`

Verify it's up:

```bash
curl -s http://127.0.0.1:8188/queue && echo "ComfyUI is running" || echo "ComfyUI is not running"
```

## 2. Adding Prompts to the Queue

### Via mission_control.py (preferred)

```bash
./shared/scripts/mission_control.py generate-local \
  --prompt "your prompt here" \
  --prefix "v10_05_description" \
  --steps 30 --cfg 5.5
```

Each call queues one image. To queue multiple, run the command multiple times with different prefixes/seeds:

```bash
./shared/scripts/mission_control.py generate-local --prompt "prompt A" --prefix "v11_01_name" --seed 11111
./shared/scripts/mission_control.py generate-local --prompt "prompt B" --prefix "v11_02_name" --seed 22222
./shared/scripts/mission_control.py generate-local --prompt "prompt C" --prefix "v11_03_name" --seed 33333
```

They queue up and process one at a time.

### Via raw API (if you need more control)

```bash
curl -s -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": { ... workflow JSON ... }}'
```

The workflow JSON structure is in `mission_control.py` `cmd_generate_local()` — it maps ComfyUI nodes (KSampler, CheckpointLoader, CLIPTextEncode, etc.).

### Key flags

| Flag | Default | Notes |
|------|---------|-------|
| `--prompt` | required | Positive prompt |
| `--negative` | built-in | Override negative prompt |
| `--prefix` | `flofi` | Filename prefix — use version naming like `v10_05_name` |
| `--steps` | 30 | Sampling steps |
| `--cfg` | 5.5 | CFG scale (5.0-5.5 is our range) |
| `--seed` | timestamp | Set for reproducibility |
| `--host` | 127.0.0.1 | ComfyUI host |
| `--port` | 8188 | ComfyUI port |

## 3. Checking Status

### Is it working on something?

```bash
curl -s http://127.0.0.1:8188/queue | python3 -c "
import sys,json
q=json.load(sys.stdin)
running=len(q['queue_running'])
pending=len(q['queue_pending'])
print(f'Running: {running} | Pending: {pending}')
if running == 0 and pending == 0: print('Queue empty — idle.')
"
```

### What was the last image generated?

```bash
ls -t tools/ComfyUI/output/*.png | head -5
```

### How many generations this session?

```bash
curl -s http://127.0.0.1:8188/history | python3 -c "import sys,json; print(f'{len(json.load(sys.stdin))} generations in history')"
```

## 4. Stopping Early (Cancel/Interrupt)

### Stop the current generation (let pending jobs continue)

```bash
curl -s -X POST http://127.0.0.1:8188/interrupt
```

This aborts the image currently rendering. The next queued job will start automatically.

### Clear all pending jobs (keep the current one running)

```bash
curl -s -X POST http://127.0.0.1:8188/queue \
  -H "Content-Type: application/json" \
  -d '{"clear": true}'
```

### Stop everything (abort current + clear queue)

```bash
curl -s -X POST http://127.0.0.1:8188/interrupt
curl -s -X POST http://127.0.0.1:8188/queue \
  -H "Content-Type: application/json" \
  -d '{"clear": true}'
```

### Delete a specific queued job

```bash
curl -s -X POST http://127.0.0.1:8188/queue \
  -H "Content-Type: application/json" \
  -d '{"delete": ["PROMPT_ID_HERE"]}'
```

## 5. Shutting Down ComfyUI

First make sure the queue is empty (or clear it — see above), then:

```bash
pkill -f "main.py --force-fp16"
```

Verify it's down:

```bash
curl -s http://127.0.0.1:8188/queue 2>/dev/null || echo "ComfyUI is down"
```

## Output & Logs

- **Generated images:** `tools/ComfyUI/output/`
- **Naming convention:** `{version}_{number}_{description}_{sequence}_.png` (e.g. `v10_04_blend_cfg55_00001_.png`)
- **Generation logs:** `data/generation_logs/generations.jsonl` (every prompt, every time)

## Current Style Settings

See `docs/STYLE_GUIDE.md` for full details. Quick version:

- **Model:** Juggernaut-XL v9
- **Sampler:** DPM++ 2M Karras
- **CFG:** 5.0-5.5
- **Steps:** 30
- **Resolution:** 832x1216
