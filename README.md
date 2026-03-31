# flo-fi

AI-generated 3D character brand for social media. Fully agentic pipeline — images, video, voice, lip sync — all CLI/API, zero GUI.

## Quick Start

```bash
./shared/scripts/start_comfyui.sh                              # ComfyUI at localhost:8188
./shared/scripts/mission_control.py generate-local --scene desert-sunset --seed 66603
./shared/scripts/mission_control.py generate-local --list-scenes  # 7 scene presets
```

## What It Does

- **Image generation** — ComfyUI + RealCartoon-Pony V3 + custom Flo LoRA via `mission_control.py`
- **Scene presets** — 7 locked scenes with Flo's face block (`--scene`)
- **LoRA training** — SimpleTuner on Mac Mini, training data in `tools/ComfyUI/training/flo/`
- **Video pipeline** (Phase 3) — Grok Aurora → ElevenLabs → PixVerse → TikTok-ready video

## Project Structure

```
shared/scripts/
  mission_control.py       # Generation CLI (--scene, --prompt, --lora, --model, etc.)
  start_comfyui.sh         # ComfyUI launcher
tools/ComfyUI/
  models/checkpoints/      # RealCartoon-Pony V3, Juggernaut-XL v9
  models/loras/            # flo_character_v1.safetensors (custom trained)
  training/flo/            # Curated training images (mj_, leo_, comfy_ prefixes)
  input/                   # Reference images
  output/                  # Generated images
config/
  config.json              # SimpleTuner training config
  multidatabackend.json    # Training data backend config
data/generation_logs/
  generations.jsonl        # Every generation logged with full params
docs/
  ROADMAP.md               # Phase progress and where we're headed
  STYLE_GUIDE.md           # Prompts, settings, anti-patterns
  COMFYUI_OPS.md           # Detailed ComfyUI operations
stories/                   # Story ideas and episode scripts
tutorials/                 # External tutorials (Daisy Studios workflow)
```

## Manual Generation (ComfyUI Web UI)

For hands-on exploration without the CLI.

```bash
./shared/scripts/start_comfyui.sh    # leave running in a terminal tab
```

Open `localhost:8188` → folder icon → **Load** → pick a workflow:

| Template | What it does |
|----------|-------------|
| `shared/workflows/flo_basic.json` | Flo's locked prompt + RealCartoon-Pony |
| `shared/workflows/flo_with_reference.json` | Same + IPAdapter face reference (v20_04) |

Edit the prompt in the green CLIP nodes, change the seed, hit **Queue Prompt**.

## Development

```bash
# Python venv (SimpleTuner, training tools)
source .venv/bin/activate

# LoRA training (runs on Mac Mini)
ssh eriks-mac-mini.local
cd /Users/eriksjaastad/Flo-Fi && source .venv/bin/activate && simpletuner train
```

## Reference

Run `pt info -p flo-fi` for models, APIs, seeds, and infrastructure details.
