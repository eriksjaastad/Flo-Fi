# flo-fi

## To future me: I see you.

### LoRA v2 Training — Pick up here (2026-04-06)

Training images are DONE. 47 curated + v20_04 = 48 images, sitting on the MacBook at `tools/ComfyUI/output/`. Here's exactly what to do:

```bash
# 1. Connect to Mac Mini
ssh eriks-mac-mini.local

# 2. Clear old v1 training images (87 junk images from the failed v1 run)
cd ~/Flo-Fi/tools/ComfyUI/training/flo/
# Trash everything in here. All of it. The old image*.jpg files, the old comfy_* files, the bucket indices. All of it.

# 3. Back on the MacBook — SCP the curated images over
scp /Users/eriksjaastad/projects/flo-fi/tools/ComfyUI/output/flo_train_*_00001_.png eriks-mac-mini.local:~/Flo-Fi/tools/ComfyUI/training/flo/
scp /Users/eriksjaastad/projects/flo-fi/tools/ComfyUI/output/v20_04_realcartoon_warm_00001_.png eriks-mac-mini.local:~/Flo-Fi/tools/ComfyUI/training/flo/

# 4. Create caption .txt files (one per image, NOT the same caption for all)
#    Each file: flo_character, score_9, score_8_up, 3d character illustration, semi-realistic 3d render,
#    young adult woman age 23, auburn brown curly hair, warm hazel eyes, freckles, [expression], wearing [outfit], [lighting]
#    The trigger word is: flo_character

# 5. Fix config.json on Mac Mini: ~/Flo-Fi/config/config.json
#    Change lora_alpha from 8 to 16. That's it. Everything else stays.

# 6. Run training — SimpleTuner is a PIP PACKAGE in ~/Flo-Fi/.venv/, NOT a directory
#    Check training.log for the exact launch command. Last run used:
#    accelerate launch --mixed_precision=bf16 --num_processes=1 --num_machines=1 --dynamo_backend=no \
#      .venv/lib/python3.13/site-packages/simpletuner/train.py

# 7. Test with 5 images per the plan in memory/project_lora_v2_training_plan.md
```

**DO NOT** install anything on the Mac Mini. It's all already there.
**DO NOT** look for a SimpleTuner directory. It's `pip install`ed in `.venv/`.
**DO NOT** skip the caption files. v1 used instance_prompt only. v2 needs per-image captions.

---

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
