# Flo-Fi Style Guide

## Locked Style DNA

**Model:** Juggernaut-XL v9 (RunDiffusion) — `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`
**Sampler:** DPM++ 2M Karras
**CFG:** 6.0
**Steps:** 30
**Resolution:** 832x1216 (portrait, social media optimized)

## Base Prompt Formula

```
highly stylized 3d character, [character description], exaggerated anime-inspired proportions,
very large detailed eyes, small face, smooth matte skin like a vinyl figure,
collectible figure aesthetic, 3d character art, octane render, sharp details
```

## Negative Prompt

```
photorealistic, photograph, real person, real skin pores, flat 2d anime, cartoon, sketch,
deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, text, watermark,
nsfw, nude, oversized breasts, uncanny valley
```

## What Works (Rules)

1. **One strong character concept per image** — one outfit, one mood, one lighting setup
2. **Vibrant color** — bold hair colors, colorful outfits, saturated environments
3. **Clear lighting** — either warm natural light OR bold colored neon. Not dark/moody
4. **Vinyl figure aesthetic** — smooth matte skin, slightly exaggerated proportions, collectible quality
5. **Fashion-forward outfits** — streetwear, tactical, fantasy armor, casual — the outfit is part of the character
6. **Confident expressions** — smirk, fierce gaze, relaxed cool, gentle smile. Never blank

## What Doesn't Work (Anti-patterns)

1. **Overly complex prompts** — heterochromia + holographic + multiple screens = anatomy breaks
2. **Too dark/moody** — dark rooms, dim lighting, editorial fashion photography feel
3. **Too realistic** — drops into uncanny valley. Need "vinyl figure" and "stylized" to keep it grounded
4. **Too many tech elements** — cyberpunk can work (v6_01, v6_02) but not when overloaded

## Approved Winners (Session 2026-03-28)

| File | Character | Prompt DNA |
|------|-----------|-----------|
| v3_03 | Red sci-fi warrior | Futuristic bodysuit, glowing accents, red neon, fierce |
| v4_01 | Streetwear girl | Black hoodie, ripped jeans, graffiti wall, warm casual |
| v6_01 | Cyber red | Chrome bodysuit, red glow, close-up portrait, intense |
| v6_02 | Street punk purple | Purple bomber jacket, chains, neon alley, attitude |
| v6_03 | Gold warrior | Black and gold ornate armor, sunset, heroic |
| v6_04 | Cozy casual | White sweater, plants, window light, lo-fi girl energy |
| v6_07 | Nature mystic | Teal-green hair, enchanted forest, gold accessories, ethereal |

## Style Spectrum

The Flo-Fi look spans a range but stays within these bounds:

```
Too 2D Anime ←——— [v6_04 casual] ——— [v6_02 street] ——— [v3_03 sci-fi] ———→ Too Photorealistic
                    ↑ warmest                                    ↑ most stylized
```

## Competitive Reference

- **@daisystudios.ai** (TikTok) — One consistent character, different outfits/scenes, Pixar-quality 3D. Slightly more Disney-stylized than our current output. Strong engagement (30K-243K views). Uses LoRA for character consistency.

## Next Steps

1. Pick one character face as the "anchor" — v6_04 (cozy girl) is the leading candidate
2. Train a LoRA on that face for character consistency across scenes
3. Generate outfit/scene variations with consistent identity
4. Explore slightly more Pixar-level stylization (bigger eyes, more exaggerated) per the Daisy Studios reference
