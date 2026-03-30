
<!-- SCAFFOLD:START - Do not edit between markers -->
# flo-fi

AI-generated 3D stylized character brand for social media.

## Quick Start

```bash
# Start ComfyUI
./shared/scripts/start_comfyui.sh    # runs on http://127.0.0.1:8188, blocks terminal

# Verify it's up
curl -s http://127.0.0.1:8188/queue && echo "up"

# Generate with a scene preset
./shared/scripts/mission_control.py generate-local --scene desert-sunset --prefix "v20_10_desert" --seed 66603

# Generate with a custom prompt
./shared/scripts/mission_control.py generate-local \
  --prompt "your prompt" --prefix "v20_10_name" --cfg 6.0 --steps 30

# List available scenes
./shared/scripts/mission_control.py generate-local --list-scenes

# Stop ComfyUI
pkill -f "main.py --force-fp16"
```

## Status

- **Current Phase:** Phase 2 — Style exploration + character lock
- **Status:** #status/active
- **Model:** RealCartoon-Pony V3 (semi-realistic 3D character illustration)
- **Baseline render:** v20_04 — warm, friendly, sun-kissed Flo at desert sunset

<!-- SCAFFOLD:END - Custom content below is preserved -->

## The Character

**Flo** — Early 20s AI developer who lives in a van and travels full-time. Natural confidence, outdoorsy, genuinely cool without knowing it. Auburn messy hair, freckles, hazel eyes, purple scrunchie. A companion drone films everything (she never films herself).

Full character bible is in memory: `~/.claude/projects/.../memory/project_flo_character_bible.md`

## The Style

Target aesthetic: **3D character illustration / semi-realistic anime 3D** (like @daisystudios.ai). NOT Pixar (too round/childlike), NOT photorealistic. Think: eyes 40% bigger than realistic, warm subsurface scattering skin, stylized hair clumps, strong rim lighting + bokeh.

- **RealCartoon-Pony V3** is the working model (Pony-based SDXL variant, needs `score_9, score_8_up` tags)
- **Juggernaut-XL v9** produces Flo's personality but is locked into photorealism
- CFG 6.0, 30 steps, DPM++ 2M Karras, 832x1216

## The Pipeline

Fully agentic. Zero GUI. Everything CLI/API.

### Image Generation (working now)
```
ComfyUI (local, M4 Pro) → mission_control.py → renders
```

### Full Content Pipeline (Phase 3)
```
ComfyUI renders  →  Grok Aurora API (images → video, $0.05/sec)
                 →  ElevenLabs API (speech-to-speech voice, $5/mo)
                 →  PixVerse API (lip sync)
                 →  TikTok-ready video
```

All tools have APIs. See `memory/reference_daisy_pipeline_tools.md` for full tool analysis.

## Project Structure

```
shared/scripts/
  mission_control.py     # Generation pipeline CLI (--scene, --prompt, --model, etc.)
  start_comfyui.sh       # ComfyUI launcher
tools/ComfyUI/
  models/checkpoints/    # Juggernaut-XL v9, RealCartoon-Pony V3
  models/loras/          # Custom LoRAs (Flo LoRA coming soon)
  models/ipadapter/      # IPAdapter Plus (for face consistency)
  models/clip_vision/    # CLIP-ViT-H-14
  input/                 # Reference images (flo_v20_04_ref.png)
  output/                # All generated images land here
data/generation_logs/
  generations.jsonl      # Every generation logged with full params
docs/
  ROADMAP.md             # Phase progress and where we're headed
  STYLE_GUIDE.md         # Winning prompts and generation settings
  COMFYUI_OPS.md         # Detailed ComfyUI operations reference
tutorials/               # External tutorials (Daisy Studios workflow, etc.)
```

## Scene Presets

The `--scene` flag loads Flo's locked face + a scene template:

| Scene | Description |
|-------|-------------|
| `desert-sunset` | Golden hour in the desert (the original v20_04 vibe) |
| `van-beach` | Sitting on van tailgate at the beach |
| `forest-camp` | Morning at a forest campsite |
| `coastal-cliff` | Windswept on a coastal cliff at sunset |
| `neon-arcade` | Neon-lit arcade (the original v8_02 energy) |
| `coffee-shop` | Cozy morning in a coffee shop |
| `rainy-van` | Rainy day inside the van, cozy vibes |

Add extra prompt terms on top: `--scene coastal-cliff --prompt "laughing, windswept hair"`

## Generation Naming Convention

`v{batch}_{number}_{description}` — e.g., `v20_04_realcartoon_warm`

- v1-v11: Juggernaut-XL exploration (v11_13 desert sunset = soul reference)
- v12-v19: LoRA and model experiments (dead ends, documented in memory)
- v20+: RealCartoon-Pony V3 era (current)

## What's Next

See `docs/ROADMAP.md` for the full phase breakdown. Immediate next steps:
1. Confirm v20_04 face with fresh eyes
2. Batch render 20-30 training images across scenes
3. Train custom Flo LoRA via SimpleTuner (installed, Python 3.13 venv)
4. Lock character consistency, then move to Phase 3 (video pipeline)
