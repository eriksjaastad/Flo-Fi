# Flo-Fi Style Guide

## Current Model & Settings

**Model:** RealCartoon-Pony V3 — `realcartoonPony_v3.safetensors`
**Style:** 3D character illustration / semi-realistic anime 3D
**Sampler:** DPM++ 2M Karras (`dpmpp_2m` / `karras`)
**CFG:** 6.0
**Steps:** 30
**Resolution:** 832x1216 (portrait, social media optimized)
**Seed:** 66603 (Flo's seed — use for consistency, vary for training data)

Pony-based model — requires `score_9, score_8_up, score_7_up` quality tags at the start of every prompt.

## Flo's Face Block (locked in mission_control.py as FLO_FACE)

```
score_9, score_8_up, score_7_up, 3d character illustration, semi-realistic 3d render,
young adult woman age 23, big expressive sparkling eyes with clear iris and round pupils,
symmetrical close-set eyes, warm golden tanned skin, sun-kissed complexion,
stylized semi-realistic proportions, beautiful detailed face, warm friendly smile,
approachable expression, sharp details, high quality render, warm hazel eyes,
freckles across nose and cheeks, thick expressive eyebrows
```

## Flo's Negative Prompt (locked in mission_control.py as FLO_NEGATIVE)

```
photorealistic, photograph, real person, flat 2d anime, cartoon, sketch,
deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, text, watermark,
nsfw, nude, chibi, score_4, score_3, score_2, score_1, crossed eyes, asymmetrical eyes,
wonky eyes, wide-set eyes, child, teenager, pale skin, pallid, dark circles, gothic,
vampire, angry, serious, brooding
```

## Current Baseline

**v20_04** (`v20_04_realcartoon_warm_00001_.png`) — The reference render. Warm, friendly, sun-kissed, correct style. Use `--scene desert-sunset` to regenerate this vibe.

## Target Aesthetic

**3D character illustration / semi-realistic anime 3D** — like @daisystudios.ai. NOT Pixar.

Key visual rules:
- Eyes ~40% bigger than realistic, clear iris, round pupils
- Warm subsurface scattering skin, sun-kissed/tanned
- Hair in stylized clumps, not individual strands
- Head-to-body ratio ~1:5
- Strong rim lighting + bokeh backgrounds
- Thick expressive eyebrows
- Friendly, approachable, never brooding

## What Doesn't Work (Hard-Won Lessons)

### Wrong models
- **Juggernaut-XL v9** — locked into photorealism. No amount of prompt engineering or LoRAs can push it into the right style category. Produces Flo's "soul" but wrong aesthetic.
- **DreamShaper XL v2 Turbo** — goes too far into generic cartoon with any LoRA.

### Wrong LoRAs
- **pixar-style.safetensors** (8MB) — too small to move any SDXL model. Useless.
- **DJ_Pixar_SDXL_2** (97MB) — effective but pushes toward WRONG style (Pixar = round cheeks, baby face).
- **Any Pixar LoRA** — Pixar is the wrong target entirely. Round cheeks, puffy faces, childlike proportions.

### Wrong prompt strategies
- Face structure keywords ("defined jawline, angular cheekbones") made Flo look vampiric
- Age-up attempts ("adult, mature") made her pale and gothic
- IPAdapter + RealCartoon-Pony = style clash, produces completely different drawing style

### The fundamental lesson
Style is a **model problem**, not a prompt or LoRA problem. You can't prompt-engineer your way out of the wrong foundation.

## Historical Winners (Juggernaut era, archived for reference)

These renders were on the wrong model but captured Flo's personality:
- **v8_02** — Neon arcade, competitive grin. Great energy, wrong style category.
- **v9_02** — Arcade animated film. Too Pixar but great personality.
- **v10_01** — Blend at CFG 5.25. Closest on Juggernaut. Still photorealistic.
- **v11_13** — Desert sunset. Flo's soul. The personality reference even though the style is wrong.

## Prompt Log

All generation prompts logged to `data/generation_logs/generations.jsonl`. Every generation via mission_control.py is automatically logged.

## Competitive Reference

- **@daisystudios.ai** — One consistent character, different outfits/scenes. Semi-realistic 3D (not Pixar). Uses Midjourney + Omni Reference for consistency. We use ComfyUI + LoRA (in progress). Full tool analysis in memory: `reference_daisy_pipeline_tools.md`.
