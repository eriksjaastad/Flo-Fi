#!/usr/bin/env python3
"""
Generate the 50-image training batch for LoRA v2.
Following the outside reviewer's structured plan exactly.

All images use:
- realcartoonPony_v3.safetensors
- CFG 4.5
- DPM++ 2M Karras
- Steps 30
- Random seeds
- Locked core prompt + locked negative
- Individual variation per image

Run: uv run shared/scripts/generate_training_batch.py
"""

import random
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Locked prompt components
CORE_FACE = (
    "score_9, score_8_up, score_7_up, 3d character illustration, "
    "semi-realistic 3d render, young adult woman, age 23, "
    "auburn brown curly hair, warm hazel eyes, freckles across nose and cheeks, "
    "soft round face"
)

LOCKED_NEGATIVE = (
    "photorealistic, photograph, real person, flat 2d anime, cartoon, sketch, "
    "deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, "
    "text, watermark, nsfw, nude, chibi, score_4, score_3, score_2, score_1, "
    "denim jacket, jean jacket, bun hairstyle, updo, large breasts, busty, "
    "mature, old, wrinkles, neck tendons, veins"
)

# Fixed settings
CHECKPOINT = "realcartoonPony_v3.safetensors"
CFG = 4.5
STEPS = 30
SAMPLER = "dpmpp_2m"

# Shot list — each entry: (prefix, prompt_additions, width, height, category)
SHOTS = [
    # === CATEGORY 1: Face Angles (12 images) — 1024x1024 ===
    ("flo_train_01_face_front_neutral", "neutral relaxed expression, front facing, looking at camera, golden hour lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_02_face_front_smile", "warm friendly smile, front facing, looking at camera, golden hour lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_03_face_front_laugh", "laughing with eyes crinkled, front facing, looking at camera, warm natural lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_04_face_3q_right_cam", "gentle smile, three quarter view facing right, looking at camera, golden hour lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_05_face_3q_right_away", "calm expression, three quarter view facing right, looking away from camera, soft natural lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_06_face_3q_left_cam", "playful grin, three quarter view facing left, looking at camera, golden hour lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_07_face_3q_left_away", "thoughtful expression, three quarter view facing left, looking away from camera, soft overcast lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_08_face_profile_right", "serene expression, profile view facing right, golden hour rim lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_09_face_profile_left", "slight smile, profile view facing left, warm backlit lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_10_face_looking_up", "looking up slightly, expression of wonder, warm lighting from above, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_11_face_looking_down", "looking down slightly, shy soft smile, warm diffused lighting, bokeh background, high quality", 1024, 1024, "face_angle"),
    ("flo_train_12_face_surprised", "surprised expression, wide eyes, mouth slightly open, natural lighting, bokeh background, high quality", 1024, 1024, "face_angle"),

    # === CATEGORY 2: Lighting Variations (10 images) — 1024x1024 ===
    ("flo_train_13_light_golden1", "warm smile, front facing, golden hour sunset lighting, warm orange tones, desert background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_14_light_golden2", "gentle smile, three quarter view, golden hour lighting, strong rim lighting, outdoor background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_15_light_overcast", "relaxed expression, front facing, soft overcast diffused lighting, muted tones, outdoor background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_16_light_bluehour", "calm expression, front facing, blue hour dusk lighting, cool blue tones, twilight sky background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_17_light_indoor", "warm smile, front facing, indoor warm lamp light, cozy interior, soft warm tones, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_18_light_neon", "playful smirk, front facing, neon purple and blue light, colorful reflections on face, dark background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_19_light_midday", "squinting slightly, front facing, bright midday sun, harsh highlights and shadows, outdoor background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_20_light_campfire", "warm relaxed expression, front facing, warm campfire light, orange flickering glow on face, dark night background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_21_light_cloudy", "neutral expression, three quarter view, flat cloudy light, even soft lighting, overcast sky background, bokeh background, high quality", 1024, 1024, "lighting"),
    ("flo_train_22_light_backlit", "silhouette rim light, front facing, strong backlit lighting, golden rim light around hair, sunset background, bokeh background, high quality", 1024, 1024, "lighting"),

    # === CATEGORY 3: Outfits + Settings (20 images) — 832x1216 ===
    ("flo_train_23_outfit_hoodie_desert", "warm smile, wearing oversized orange hoodie, upper body portrait, desert landscape background, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_24_outfit_flannel_desert", "relaxed expression, wearing open plaid flannel shirt over white tee, upper body portrait, desert road background, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_25_outfit_tee_desert", "confident smile, wearing fitted earth-tone tee shirt, upper body portrait, desert sunset background, warm golden lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_26_outfit_tank_desert", "casual relaxed expression, wearing olive green tank top, upper body portrait, desert mesa background, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_27_outfit_sweater_indoor", "cozy warm smile, wearing oversized cream knit sweater, upper body portrait, cozy interior background, warm lamp lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_28_outfit_denim_open", "playful grin, wearing open denim jacket over band tee, upper body portrait, desert background, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_29_outfit_rain_jacket", "determined expression, wearing bright rain jacket, upper body portrait, rainy overcast background, diffused grey lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_30_outfit_knit_cozy", "sleepy warm smile, wearing cozy knit cardigan, upper body portrait, van interior background, soft warm lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_31_outfit_hoodie_van", "casual relaxed expression, wearing burgundy hoodie, upper body portrait, van interior with fairy lights, warm cozy lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_32_outfit_tee_coffee", "gentle smile, wearing vintage graphic tee, upper body portrait, coffee shop window seat, soft morning light, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_33_outfit_tank_sunset", "looking off to side, wearing white tank top, upper body portrait, desert sunset background, strong warm backlighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_34_outfit_flannel_forest", "peaceful expression, wearing oversized flannel pajama top, upper body portrait, forest campsite background, morning sunlight through trees, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_35_outfit_sweater_night", "wonder expression looking up, wearing forest green sweater, upper body portrait, night sky stars background, cool moonlight, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_36_outfit_tee_desert2", "laughing, wearing rust colored band tee, upper body portrait, desert rock formation background, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_37_outfit_hoodie_desert2", "warm smile, wearing faded blue hoodie, upper body portrait, desert highway background, late afternoon warm lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_38_outfit_tank_van", "casual grin, wearing fitted tank top, upper body portrait, van doorway background, warm evening lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_39_outfit_flannel_cliff", "windswept hair, wearing plaid flannel with sleeves rolled up, upper body portrait, coastal cliff background, strong wind, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_40_outfit_sweater_rain", "thoughtful expression, wearing oversized wool sweater, upper body portrait, rainy window background, soft grey diffused lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_41_outfit_tee_desert3", "confident relaxed pose, wearing plain white tee shirt, upper body portrait, badlands desert background, golden hour lighting, bokeh background, high quality", 832, 1216, "outfit"),
    ("flo_train_42_outfit_hoodie_coffee", "warm smile holding mug, wearing oversized orange hoodie, upper body portrait, coffee shop interior, warm morning window light, bokeh background, high quality", 832, 1216, "outfit"),

    # === CATEGORY 4: Emotion Range (8 images) — 1024x1024 ===
    ("flo_train_43_emo_determined", "determined focused expression, slight furrowed brow, three quarter view, wearing fitted tee, warm natural lighting, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_44_emo_pensive", "pensive thoughtful expression, looking into distance, three quarter view, wearing oversized sweater, soft overcast lighting, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_45_emo_excited", "excited delighted expression, big genuine smile, front facing, wearing orange hoodie, bright warm lighting, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_46_emo_tired", "tired sleepy expression, eyes half closed, slight smile, front facing, wearing cozy knit, soft warm lamp lighting, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_47_emo_skeptical", "skeptical side-eye expression, one eyebrow raised, three quarter view, wearing tank top, natural daylight, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_48_emo_laughing", "laughing hard, head tilted back, eyes closed with joy, front facing, wearing flannel shirt, golden hour lighting, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_49_emo_calm", "calm serene expression, gentle closed-mouth smile, front facing, wearing earth-tone tee, soft diffused lighting, bokeh background, high quality", 1024, 1024, "emotion"),
    ("flo_train_50_emo_surprised", "caught off guard expression, mouth open, wide eyes, three quarter view, wearing hoodie, bright natural lighting, bokeh background, high quality", 1024, 1024, "emotion"),
]


def run():
    mc = str(PROJECT_ROOT / "shared" / "scripts" / "mission_control.py")
    uv = str(Path.home() / ".local" / "bin" / "uv")

    total = len(SHOTS)
    print(f"=== TRAINING BATCH: {total} images ===")
    print(f"Checkpoint: {CHECKPOINT}")
    print(f"CFG: {CFG}, Steps: {STEPS}, Sampler: {SAMPLER}")
    print(f"Seeds: RANDOM (different every image)")
    print()

    for i, (prefix, additions, width, height, category) in enumerate(SHOTS, 1):
        seed = random.randint(10000, 999999)
        full_prompt = f"{CORE_FACE}, {additions}"

        print(f"[{i}/{total}] {prefix} (seed: {seed}, {width}x{height}, {category})")

        cmd = [
            uv, "run", mc, "generate-local",
            "--seed", str(seed),
            "--prefix", prefix,
            "--model", CHECKPOINT,
            "--prompt", full_prompt,
            "--negative", LOCKED_NEGATIVE,
            "--width", str(width),
            "--height", str(height),
            "--steps", str(STEPS),
            "--cfg", str(CFG),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:200]}")
        else:
            # Extract prompt_id from output
            for line in result.stdout.split("\n"):
                if "queued" in line.lower() or "logged" in line.lower():
                    print(f"  {line.strip()}")

    print(f"\n=== ALL {total} QUEUED ===")
    print(f"Images will appear in: tools/ComfyUI/output/flo_train_*.png")
    print(f"Curate against v20_04 before training. Trash anything that doesn't match.")


if __name__ == "__main__":
    run()
