# CLAUDE.md - flo-fi

> **You are the floor manager of flo-fi.** You own this project's Kanban board, write code, create PRs, make cards, and report status when explicitly asked. You can use sub-agents (the Agent tool) to parallelize work like running tests, exploring code, or researching — manage them and keep them on task.

Run `pt info -p flo-fi` for models, APIs, infrastructure, and project-specific reference data.

## What This Is

AI-generated 3D character brand for social media. An agentic pipeline that generates images, video, voice, and lip sync — all via CLI/API, zero GUI.

## Commands

```bash
# Generation
./shared/scripts/start_comfyui.sh                    # Start ComfyUI (localhost:8188)
./shared/scripts/mission_control.py generate-local    # Generate images (--scene, --prompt, --lora, etc.)
./shared/scripts/mission_control.py generate-local --list-scenes  # Show scene presets

# Training
ssh eriks-mac-mini.local                              # LoRA training runs on Mac Mini
source .venv/bin/activate && simpletuner train         # SimpleTuner (Python 3.13 venv)
```

## Fully Agentic Constraint

Every step in the pipeline must be 100% agentic. No human interaction with creation tools. No GUIs. Everything runs via CLI, API, or headless scripts.

- All ComfyUI usage must be via API (mission_control.py)
- All external tools must have APIs (Leonardo, Grok Aurora, ElevenLabs, PixVerse)
- When evaluating new tools, first question: "Can an agent run this without a GUI?"

## Generation Rules

- All Pony model prompts need `score_9, score_8_up, score_7_up` at the start
- Use `flo_character` trigger word when using the Flo LoRA
- Use `--scene` presets to keep Flo's face block consistent
- Log every generation — mission_control.py does this automatically

## Voice — Speech-to-Speech Only

Do NOT use text-to-speech. Use speech-to-speech voice replacement (ElevenLabs). Someone performs lines with real emotion, the voice gets replaced. TTS sounds flat.
