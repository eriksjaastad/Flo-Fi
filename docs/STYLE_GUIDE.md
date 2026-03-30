# Flo-Fi Style Guide

## Locked Style DNA

**Model:** Juggernaut-XL v9 (RunDiffusion) — `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`
**Sampler:** DPM++ 2M Karras (`dpmpp_2m` / `karras`)
**CFG:** 5.5
**Steps:** 30
**Resolution:** 832x1216 (portrait, social media optimized)

## Winning Prompts

### WINNER 1: v8_02 — Neon Arcade

More grounded/semi-realistic end of the sweet spot. The v8 formula with colored lighting pushing natural stylization.

**Positive:**
```
highly stylized 3d character, young woman, large expressive sparkling eyes with personality,
small nose, smooth flawless skin, stylized semi-realistic proportions, 3d character art,
warm inviting quality, beautiful detailed face, sharp details, high quality render,
shoulder-length pink hair with messy bangs, playful violet eyes, wearing oversized retro
gaming tee and denim shorts, leaning over arcade cabinet excitedly, colorful arcade lights
reflecting on face, competitive excited grin, teal and magenta and yellow neon glow,
fun energetic atmosphere
```

**Negative:**
```
photorealistic, photograph, real person, real skin pores, skin texture, neck tendons,
collarbone detail, veins, individual hair strands, flat 2d anime, cartoon, sketch,
deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, text, watermark,
nsfw, nude, oversized breasts, uncanny valley, dark moody, horror, blank expression, dead eyes
```

**Seed:** 11112 | **CFG:** 5.5

---

### WINNER 2: v9_02 — Arcade Animated Film

More stylized/animated end of the sweet spot. Pushes further into exaggerated features while staying 3D.

**Positive:**
```
3d animated film still, Pixar-style character design, stylized young woman,
large round expressive cartoon eyes, small cute nose, round soft facial features,
smooth matte skin with no texture, slightly exaggerated head proportions, 3d character render,
shoulder-length pink hair with messy bangs, playful violet eyes, wearing oversized retro
gaming tee and denim shorts, leaning over arcade cabinet excitedly, colorful arcade lights
reflecting on face, competitive excited grin, teal and magenta and yellow neon glow,
fun energetic atmosphere, animated movie screenshot
```

**Negative:**
```
photorealistic, photograph, real person, real skin texture, skin pores, wrinkles,
neck tendons, collarbone, veins, realistic hair strands, flat 2d, traditional anime, sketch,
deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, text, watermark,
nsfw, nude, oversized breasts, uncanny valley, dark moody, blank expression
```

**Seed:** 22223 | **CFG:** 5.0

---

### CLOSE: v8_10 — Space Explorer

Close but missing the exaggeration that the two arcade winners have. Good scene/pose reference.

```
highly stylized 3d character, young woman, large expressive sparkling eyes with personality,
small nose, smooth flawless skin, stylized semi-realistic proportions, 3d character art,
warm inviting quality, beautiful detailed face, sharp details, high quality render,
long braided teal hair floating weightlessly, bright cyan eyes, wearing sleek white and blue
space suit with glowing accents, floating in space station with earth visible through window,
curious amazed expression reaching toward stars, blue and white lighting with warm earth glow,
sense of wonder and discovery
```
**Seed:** 11120 | **CFG:** 5.5

## Direction Notes

- **The target lives between Neon Arcade (v8_02) and Arcade Animated Film (v9_02).** Not exactly either one — somewhere in the middle.
- **Key insight:** The arcade scene produces a subtle exaggeration in both winners that Space Explorer doesn't have, despite using similar prompt language. Scene/lighting interaction matters.
- **What pushed too far:** "collectible anime figure aesthetic", "vinyl toy", "chibi proportions" (v9_03) — went too cartoony.
- **CFG range:** 5.0–5.5. Lower = more stylized, higher = more grounded.
- **v10_01 (blend film stylized) is really good.** `3d animated film character` + v8's `highly stylized` descriptors at CFG 5.25. This may be the locked formula. Remaining v10 renders still pending review.

## What Works (Rules)

1. **One strong character concept per image** — one outfit, one mood, one lighting setup
2. **Vibrant color** — bold hair colors, colorful outfits, saturated environments
3. **Clear lighting** — either warm natural light OR bold colored neon. Not dark/moody
4. **Colored light on face** — neon, earth glow, arcade lights. This pushes the eyes into the sweet spot
5. **Vinyl figure aesthetic** — smooth matte skin, slightly exaggerated proportions, collectible quality
6. **Fashion-forward outfits** — streetwear, tactical, fantasy armor, casual — the outfit is part of the character
7. **Confident expressions** — smirk, fierce gaze, relaxed cool, gentle smile. Never blank

## What Doesn't Work (Anti-patterns)

1. **Overly complex prompts** — heterochromia + holographic + multiple screens = anatomy breaks
2. **Too dark/moody** — dark rooms, dim lighting, editorial fashion photography feel
3. **Too realistic** — drops into uncanny valley. Need "stylized" to keep it grounded
4. **Too many tech elements** — cyberpunk can work (v6_01, v6_02) but not when overloaded
5. **Soft/natural light only** — produces more photorealistic results. Colored lighting is better for our style

## Other Notable Outputs

| File | Scene | Notes |
|------|-------|-------|
| v3_03 | Red sci-fi warrior | Vinyl figure aesthetic, dramatic |
| v4_01 | Streetwear casual | Animated movie feel, warm |
| v6_01 | Cyber red close-up | Intense, futuristic |
| v6_02 | Street punk purple | Fashion-forward, attitude |
| v6_03 | Gold warrior | Ornate fantasy armor |
| v6_04 | Cozy casual | Lo-fi girl energy |
| v6_07 | Nature mystic | Enchanted forest, ethereal |
| v7_01 | Coffee shop | Warm, personality in eyes |
| v7_07 | Bookworm | Too Pixar but great personality |
| v8_05 | Studio creative | Close to target but eyes not exaggerated enough |

## Prompt Log

All generation prompts are logged to `data/generation_logs/generations.jsonl` (45 records from sessions 1-2). Every future generation via mission_control.py is automatically logged.

## Competitive Reference

- **@daisystudios.ai** (TikTok) — One consistent character, different outfits/scenes, Pixar-quality 3D. Slightly more Disney-stylized than our current output. Strong engagement (30K-243K views). Uses LoRA for character consistency.

## Next Steps

1. Iterate on the v8 base prompt — nudge slightly more cartoony without losing the 3D quality
2. Once style is locked, pick Flow's face and start LoRA training
3. Generate outfit/scene variations with consistent identity
