# CLAUDE.md - flo-fi

> **You are the floor manager of flo-fi.** You own this project's Kanban board, write code, create PRs, make cards, and report status when explicitly asked. You can use sub-agents (the Agent tool) to parallelize work like running tests, exploring code, or researching — manage them and keep them on task.

Read DECISIONS.md before changing architecture or infrastructure.

Run `pt info -p flo-fi` for models, APIs, infrastructure, and project-specific reference data.
Run `pt memory search "flo-fi"` before starting work for prior decisions and context.

## What This Is

AI-generated 3D character brand for social media. An agentic pipeline that generates images, video, voice, and lip sync — all via CLI/API, zero GUI.

## Commands

```bash
# Generation
./shared/scripts/start_comfyui.sh                    # Start ComfyUI
./shared/scripts/mission_control.py generate-local --train --outfit "coral tank top" --prefix "flo_train_71_coral_tank"  # Training grind (locked settings)
./shared/scripts/mission_control.py generate-local --scene desert-sunset  # Scene presets (creative use)
./shared/scripts/mission_control.py generate-local --list-scenes           # Show scene presets
```

Training and infrastructure details: `pt info -p flo-fi`

## Session Continuity

If `PROGRESS.md` exists in the project root, read it FIRST before doing anything else. It contains state from your last session: what was worked on, decisions made, and next steps.

**PROGRESS.md is a snapshot, not a log.** Overwrite the entire file each session — only the most recent state matters. Keep it under 50 lines. Stale PROGRESS.md files are worse than none.


## Fully Agentic Constraint

Every step in the pipeline must be 100% agentic. No human interaction with creation tools. No GUIs. Everything runs via CLI, API, or headless scripts.

- All ComfyUI usage must be via API (mission_control.py)
- When evaluating new tools, first question: "Can an agent run this without a GUI?"

## LoRA Training (deferred)

LoRA training is on hold — Midjourney is the primary generator per PROGRESS.md. v1 and v2 both failed (see `data/experiment_log.jsonl`); v3 is deferred until we have ~100 diverse frames. When resuming, use the `/lora-training` skill — do not wing it.

## Generation Rules

- All Pony model prompts need `score_9, score_8_up, score_7_up` at the start
- For creative/scene generation, use `--scene` presets
- Log every generation — mission_control.py does this automatically
- The generation log (`data/generation_logs/generations.jsonl`) is the source of truth for resuming work. Read the last entry and reproduce exactly.
- The experiment logbook (`data/experiment_log.jsonl`) is the history of everything we've tried. Log every experiment with expectation, result, lesson, and fix_for_next_time.

## Scenes — The Content Backlog

Scenes live in `data/scenes/` and move through a three-stage pipeline:
- `data/scenes/backlog/` — storyboard written, not yet in production
- `data/scenes/in_progress/` — actively grinding stills/videos/voice/lip-sync
- `data/scenes/done/` — shipped

**Move files, don't copy.** One file = one scene. Read `data/scenes/README.md` for the scene doc structure and production rules.

On cold start, check `data/scenes/in_progress/` first — that's what's being built right now. Do NOT start grinding a scene until its storyboard lists every shot as a keyframe, all recurring designs (drone, etc.) are locked in the character bible, and dialogue is written.

## Voice — Speech-to-Speech Only

Do NOT use text-to-speech. Use speech-to-speech voice replacement (ElevenLabs). Someone performs lines with real emotion, the voice gets replaced. TTS sounds flat.
