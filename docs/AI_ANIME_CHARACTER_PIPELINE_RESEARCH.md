# Flo-Fi: AI-Generated Anime Character Creation Pipeline Research

**Date:** 2026-03-28
**Purpose:** Comprehensive research report for building an anime character brand using hybrid 3D modeling + AI generation workflows.

---

## Table of Contents

1. [3D Modeling Pipeline](#1-3d-modeling-pipeline)
2. [AI Image Generation for Anime](#2-ai-image-generation-for-anime)
3. [AI Video and Animation](#3-ai-video-and-animation)
4. [Hybrid Workflows (3D + AI)](#4-hybrid-workflows-3d--ai)
5. [Content Policy Analysis](#5-content-policy-analysis)
6. [Recommended Pipeline](#6-recommended-pipeline)

---

## 1. 3D Modeling Pipeline

### VRoid Studio (Primary Recommendation for Base Models)

- **Cost:** Free (Windows, Mac, iOS, Android)
- **URL:** https://vroid.com/en/studio
- **What it does:** Purpose-built for anime character creation. Slider-based controls for face, body, hair, and clothing. Supports painting textures directly on the 3D model.
- **Export:** VRM format (imports into Blender via VRM Importer addon)
- **Strengths:**
  - Fastest path from zero to a fully rigged anime character
  - Native anime aesthetic -- no shader tinkering needed
  - Large community with shared assets, hair presets, clothing templates
  - Characters come pre-rigged with facial blendshapes/visemes
- **Limitations:**
  - Stylistically constrained to its built-in aesthetic (think VTuber style)
  - Limited clothing complexity without external editing
  - Not ideal for highly unique or non-standard body types
- **Blender Integration:** Export VRM from VRoid, import into Blender with the VRM Importer addon. For advanced rigging, the ARP (Auto-Rig Pro) Quick Rig addon can one-click convert VRoid characters to fully rigged Blender models with facial animation support.

### Blender (Core Modeling + Rendering Tool)

- **Cost:** Free, open source
- **Version:** 4.x / 5.0 (current)
- **Role in pipeline:** Central hub for everything -- modeling, rigging, shading, rendering, animation, and exporting to AI workflows.

#### Anime Shader Setups in Blender

Several approaches for achieving anime/toon look:

| Shader | Engine | Cost | Notes |
|--------|--------|------|-------|
| **Built-in Toon BSDF** | Cycles/Eevee | Free | Basic but functional. Diffuse BSDF > Shader to RGB > ColorRamp (Constant interpolation) for cel shading. |
| **LSCherry Toon Shader** | Eevee | Free (GitHub) | Framework compatible with contemporary anime game styles. GitHub: `lvoxx/LSCherry` |
| **Erito Toon Shader v4** | Eevee | Free (Gumroad) | Popular community shader with good anime results |
| **Komikaze** | Eevee | Paid (~$30) | Professional NPR toon shader pack with stylized assets |
| **Blender NPR** | Various | Free | Community resource at blendernpr.org with downloadable shader files and tutorials |

**Outline technique:** Create a separate material with Backface Culling enabled, apply a Solidify modifier with thin thickness (0.01) and flipped normals. This gives the characteristic anime outline look.

### Meshmixer Status and Alternatives

**Meshmixer is discontinued.** Autodesk stopped active development in 2023. If you had issues with it, there is no reason to continue using it.

**Replacements:**

| Tool | Cost | Best For |
|------|------|----------|
| **Blender Sculpt Mode** | Free | General sculpting, already in your pipeline |
| **SculptGL** | Free (browser) | Quick sculpting experiments |
| **Daz Studio** | Free | Pre-made character bases, extensive marketplace |
| **MeshLab** | Free | Mesh cleanup and repair (what Meshmixer was often used for) |

### MB-Lab (Blender Addon)

- Community-maintained fork of ManuelbastioniLAB
- Creates humanoid characters directly inside Blender
- **24 anime-specific facial morphs** plus 40 realistic morphs
- Good for creating base meshes that you then customize

### Tripo AI (AI-Powered 3D Generation)

- **URL:** https://www.tripo3d.ai/
- **What it does:** Generates 3D models from text or images in ~10 seconds (Algorithm 3.0, released August 2025)
- **Relevance:** Can generate anime character base meshes from 2D reference art, with automatic T-pose and skeleton rigging
- **Workflow:** Generate base > export > refine in Blender
- **Pricing:** Free tier available; paid plans for higher quality and volume

---

## 2. AI Image Generation for Anime

### Model Landscape (Ranked by Anime Quality)

#### Tier 1: Best for Anime (Local/Self-Hosted)

**IllustriousXL**
- Architecture: SDXL-based
- Trained on Danbooru2023 dataset
- Best-in-class line work, color consistency, anatomy for anime
- Huge character knowledge base
- Spawned an ecosystem of fine-tunes and LoRAs

**NoobAI-XL**
- Architecture: SDXL-based (built on IllustriousXL early release)
- Trained on ~13 million images (Danbooru + e621 datasets)
- Slightly better overall output quality than IllustriousXL in recent comparisons
- More stylistic range and improved composition
- Current community favorite for raw effectiveness

**Pony Diffusion V6/V7**
- Architecture: SD 1.5 (V6) / SDXL (V7)
- The original anime powerhouse
- V6 still relevant for limited hardware (SD 1.5 base)
- V7 competes directly with IllustriousXL
- Strong LoRA ecosystem

**FLUX Anime Models**
- Architecture: FLUX (latest generation)
- NTR Mix FLUX, Hassaku FLUX -- sharper, more coherent than SDXL
- Best overall quality but requires more VRAM (16GB+ recommended)
- LoRA training has matured: Kohya-ss/sd-scripts or ai-toolkit by Ostris

#### Tier 2: Cloud Platforms

**Midjourney**
- Excellent anime output quality with `--niji` mode
- Consistent style but limited control
- **Strict PG-13 policy** -- see Content Policy section
- $10-60/month subscription

**DALL-E (ChatGPT / API)**
- Can produce anime-style images
- Less consistent anime aesthetic than dedicated models
- **Very strict content filtering** -- overly conservative for the Flo-Fi use case
- Integrated into ChatGPT Plus ($20/month)

**Stable Diffusion via Cloud (RunComfy, Civitai, SeaArt)**
- Run community models without local hardware
- Variable policies depending on platform
- Good middle ground for experimentation

#### Character Consistency Techniques

This is critical for a brand with recurring characters:

1. **LoRA Training** -- Train a character-specific LoRA on 15-30 reference images of your character. Cost: $1-3 on cloud GPU (RunPod, Vast.ai). Training time: 45-90 minutes.
2. **PuLID Adapter** -- Locks in precise facial features. Use at 0.8 strength alongside a low-strength LoRA (0.6) for body/hair.
3. **ControlNet OpenPose** -- Forces consistent posture across generations.
4. **IP-Adapter** -- Reference image conditioning for style and face consistency without training.
5. **ComfyUI Workflows** -- Node-based pipeline that chains all of the above together reproducibly.

**Production stack for character consistency (2026 best practice):**
- LoRA (0.6 strength) for general body shape and hair
- PuLID Adapter (0.8) for precise facial features
- ControlNet (OpenPose) for posture
- This combination enables frame-identical characters across hundreds of images.

### Hardware Requirements

| Setup | VRAM | Best Models |
|-------|------|-------------|
| Budget (GTX 1660, etc.) | 6GB | Pony V6 (SD 1.5 base) |
| Mid-range (RTX 3060/4060) | 8-12GB | IllustriousXL, NoobAI-XL, Pony V7 |
| High-end (RTX 4080/4090) | 16GB+ | FLUX models, full LoRA training |
| Mac (M1/M2/M3/M4) | Unified memory | All SDXL models via ComfyUI; FLUX with 32GB+ |

---

## 3. AI Video and Animation

### 2D Animation

**Live2D Cubism**
- **URL:** https://www.live2d.com/
- **Cost:** Free tier (limited); Pro ~$25/month
- Industry standard for 2D character animation (500+ commercial titles)
- Animates original 2D art with rigging -- eye blinks, breathing, head turns, lip sync
- Perfect for social media character posts (talking head videos, reaction content)
- **AI integration:** KomikoAI's Layer Splitter can auto-separate flat character art into animation-ready layers

**VTube Studio**
- Free (with watermark) / paid ($25 one-time)
- Real-time Live2D model animation via webcam tracking
- Good for creating "VTuber-style" content for TikTok/Instagram

### AI Video Generation

**WAN 2.2**
- Current leader for anime video generation
- Can animate still images into short clips
- Motion control capabilities for directing movement

**Kling**
- Image-to-video with good anime style support
- Short clip generation (5-15 seconds)

**GoEnhance**
- Free Live 2D animation generator
- Converts single character images to animated clips with natural eye blinks, breathing, head turns

**Projection:** By end of 2026, models are expected to generate consistent 30-second anime clips from a single image in one pass.

### 3D Animation

**Blender (Direct)**
- Full animation suite built in
- Keyframe, physics, particle systems
- Can render anime-style animations with toon shaders

**DeepMotion**
- AI-powered motion capture from video
- Import motions onto VRoid/Blender characters

**Mixamo (Adobe)**
- Free auto-rigging and animation library
- Upload character mesh > auto-rig > apply animations
- Works well with VRoid exports after cleanup

**Reallusion AI Render (Open Beta, 2025)**
- Free tool bridging 3D animation with AI-powered rendering
- ComfyUI integration for stylized output
- Supports ControlNet depth, canny, pose, and IPAdapter inputs

---

## 4. Hybrid Workflows (3D + AI)

This is the key section for the Flo-Fi use case. The hybrid approach gives you control (from 3D) plus style (from AI).

### Core Workflow: Blender Render to AI Stylization

```
[VRoid Studio] --> [Blender] --> [Render Passes] --> [ComfyUI + ControlNet] --> [Final Image]
     |                |              |                        |
  Base model    Pose/Scene     Depth map              Anime checkpoint
  creation      composition    Canny edges            + Character LoRA
                Toon shader    Normal map             + Style LoRA
                setup          Color render
```

**Step-by-step:**

1. **Create base character** in VRoid Studio (or model from scratch in Blender)
2. **Import into Blender**, apply anime toon shaders, set up scene/lighting/pose
3. **Render multiple passes from Blender:**
   - Depth pass (Z-depth)
   - Canny/edge pass (using Freestyle or Solidify outline)
   - Normal map pass
   - Base color render (optional -- for img2img reference)
4. **Feed passes into ComfyUI:**
   - Depth map --> ControlNet Depth model (spatial fidelity)
   - Canny edges --> ControlNet Canny model (clean composition, anime outlines)
   - Optionally: OpenPose data for character pose
5. **Generate with anime checkpoint** (IllustriousXL or NoobAI-XL) + your character's LoRA
6. **Result:** AI-generated anime art that follows your 3D scene's exact composition, pose, and lighting

### Why This Works for Flo-Fi

- **Consistency:** Same 3D model = same proportions every time. LoRA locks the face/style.
- **Control:** You decide the exact pose, camera angle, lighting, and composition in Blender.
- **Speed:** Once the pipeline is set up, new content is: pose model > render passes > generate in ComfyUI.
- **Iteration:** Don't like the AI output? Adjust the 3D pose and re-render. The feedback loop is tight.

### Key Tools for the Hybrid Pipeline

**ComfyUI** (not Automatic1111 / SDUI)
- Node-based workflow builder
- Better for reproducible, complex pipelines
- Save and share workflows as JSON
- URL: https://github.com/comfyanonymous/ComfyUI

**ControlNet Preprocessors**
- `comfyui_controlnet_aux` (GitHub: Fannovel16) -- all preprocessors in one package
- Key preprocessors: Depth (MiDaS/Zoe), Canny, Lineart Anime (`kataragi/ControlNet-LineartXL`), OpenPose

**AI-Render Blender Addon**
- Direct Blender-to-ComfyUI bridge
- Renders 3D scenes with AI in real-time
- Open beta as of 2025

**StableGen Blender Addon**
- GitHub: `sakalond/StableGen`
- AI-powered texturing directly within Blender

### Animation Hybrid Workflow

For animated content (short clips, social media videos):

1. Animate character in Blender (keyframe or motion capture via DeepMotion)
2. Render frame sequence with depth + canny passes
3. Process entire sequence through ComfyUI with ControlNet
4. Use temporal consistency techniques (frame interpolation, AnimateDiff) to maintain coherence between frames
5. Output: AI-stylized anime animation with 3D-accurate motion

---

## 5. Content Policy Analysis

### The "Slightly Edgy SFW Anime" Line

The Flo-Fi aesthetic (Kill la Kill / Evangelion confidence level) involves:
- Confident female characters
- Form-fitting or revealing (but not explicit) clothing
- Battle suits, plugsuits, sailor uniforms with stylistic liberties
- Cleavage, thigh-highs, short skirts -- staple anime tropes
- Attitude and energy, not nudity

Here is how each platform handles this:

### Platform-by-Platform Breakdown

#### OpenAI / DALL-E (ChatGPT Image Generation)

| Aspect | Status |
|--------|--------|
| **Policy** | Strict. No nudity, no "sexual" content. |
| **Anime clothing** | Problematic. Reports of prompts specifying women's clothing or hairstyles being blocked. |
| **Kill la Kill-style** | Very likely blocked. Even non-explicit form-fitting outfits trigger filters. |
| **"Adult mode"** | Announced but pushed back to Q1 2026 or later. |
| **Documented issue** | Community reports a gap between written policy (which technically allows mature art themes) and actual model behavior (which aggressively blocks them). |
| **Verdict for Flo-Fi** | **Not recommended.** Too restrictive for the target aesthetic. Basic anime portraits work; anything with attitude or revealing clothing will hit walls. |

#### Midjourney

| Aspect | Status |
|--------|--------|
| **Policy** | PG-13 standard. No nudity, sexual content, or graphic material. |
| **Anime support** | Excellent via `--niji` mode. |
| **Kill la Kill-style** | Partially possible. Confident poses and fitted clothing can work, but terms like "provocative," "intimate," or anything suggesting lack of clothing are banned. |
| **Filter behavior** | Automated word filters + AI content moderation. Expanded in 2025 to catch more subtle suggestive terms. |
| **Enforcement** | Images blocked at generation time. Repeat violations lead to temp/permanent bans. |
| **Verdict for Flo-Fi** | **Limited use.** Good for face shots, portraits, and conservative poses. Will struggle with the full Kill la Kill aesthetic. Useful for concept art and mood boards but not primary generation. |

#### Stability AI (Official API / DreamStudio)

| Aspect | Status |
|--------|--------|
| **Policy** | As of July 31, 2025, Stability AI prohibits sexually explicit content in their Acceptable Use Policy. |
| **Impact** | All R+ rated images created with Stability AI Core Models or derivatives were removed from Civitai and similar platforms. |
| **Kill la Kill-style** | The official API will block explicit content, but "edgy SFW" should generally pass. |
| **Verdict for Flo-Fi** | **Usable for the official API** if you stay clearly SFW. But the real power is in local deployment (see below). |

#### Local Stable Diffusion (Self-Hosted)

| Aspect | Status |
|--------|--------|
| **Policy** | None. You control the hardware, you control the output. |
| **Content filters** | None by default. Optional safety checker can be disabled. |
| **Kill la Kill-style** | Fully possible. No restrictions on clothing, poses, attitude, or style. |
| **Models available** | IllustriousXL, NoobAI-XL, Pony -- all trained on uncensored datasets (Danbooru, e621). |
| **Legal considerations** | Legal in most jurisdictions for fictional characters. Do not generate content depicting real people or minors. |
| **Verdict for Flo-Fi** | **Primary recommendation.** Full creative freedom for the target aesthetic. |

#### Civitai (Model Hosting + On-Site Generation)

| Aspect | Status |
|--------|--------|
| **Policy (2025-2026)** | Tightened significantly under payment processor pressure (Visa/Mastercard). |
| **Current state** | SFW content is allowed. Mature content requires metadata tagging. Reports of aggressive moderation flagging bare shoulders as "explicit nudity." |
| **For model downloads** | Still the primary source for anime checkpoints and LoRAs. Free to download models for local use. |
| **On-site generation** | More restricted than local. Mature content toggle exists but enforcement is inconsistent. |
| **Verdict for Flo-Fi** | **Use for downloading models.** Do generation locally, not on-platform. |

#### Grok (xAI)

| Aspect | Status |
|--------|--------|
| **Policy** | Fewer restrictions than competitors. |
| **Anime support** | Limited compared to dedicated anime models. |
| **Verdict for Flo-Fi** | Not ideal for anime specifically, but worth monitoring as the platform evolves. |

### Content Policy Summary Matrix

| Platform | Basic Anime | Fitted Clothing | Cleavage | Battle Suits | Kill la Kill Level |
|----------|-------------|-----------------|----------|--------------|-------------------|
| DALL-E | Yes | Sometimes | No | Risky | No |
| Midjourney | Yes (niji) | Usually | Risky | Sometimes | No |
| Stability API | Yes | Yes | Borderline | Yes | Borderline |
| Local SD | Yes | Yes | Yes | Yes | Yes |
| Civitai (on-site) | Yes | Yes | Flagged | Sometimes | Risky |

### Bottom Line

**For the Flo-Fi aesthetic, local Stable Diffusion is the only reliable option.** Cloud platforms are too restrictive or too unpredictable for "slightly edgy SFW" anime content. Use cloud tools (Midjourney, DALL-E) for concept exploration and mood boards, but do production generation locally.

---

## 6. Recommended Pipeline for Flo-Fi

### Phase 1: Character Design (Week 1-2)

**Tools:** VRoid Studio + Blender + Local Stable Diffusion (ComfyUI)

1. **Concept art** -- Use IllustriousXL or NoobAI-XL locally to generate character concept sheets. Iterate on design, clothing, color palette, personality.
2. **3D base model** -- Build in VRoid Studio. Export VRM.
3. **Import to Blender** -- Apply toon shader (LSCherry or manual Shader-to-RGB setup). Add custom clothing/accessories.
4. **Train character LoRA** -- Select 15-30 of the best concept images. Train on local GPU or cloud (RunPod). ~$2 and 60 minutes.

### Phase 2: Content Production Pipeline

**Tools:** Blender + ComfyUI + ControlNet

```
For each social media post:
1. Pose the 3D character in Blender (adjust scene, lighting, camera)
2. Render depth + canny passes (one click with saved render settings)
3. Run through ComfyUI workflow:
   - ControlNet Depth + Canny
   - Character LoRA
   - Anime checkpoint (NoobAI-XL recommended)
   - Style prompt
4. Pick best output, light touch-up if needed
5. Post to social media
```

**Time per image (once pipeline is set up):** 10-20 minutes including posing.

### Phase 3: Animation and Video Content

**Tools:** Blender + Live2D Cubism + WAN 2.2

- **Short-form video (TikTok/Reels):** Animate 3D model in Blender, render through AI pipeline for stylized anime clips. Or use Live2D for talking-head content.
- **Character introduction posts:** AI-animated still images via GoEnhance or WAN 2.2 (eye blinks, hair movement, breathing).
- **VTuber-style content:** VRoid model in VTube Studio for live/recorded content.

### Recommended Software Stack

| Component | Tool | Cost | Priority |
|-----------|------|------|----------|
| 3D Character Base | VRoid Studio | Free | Must-have |
| 3D Scene/Render | Blender | Free | Must-have |
| AI Generation Engine | ComfyUI | Free | Must-have |
| Primary Anime Model | NoobAI-XL or IllustriousXL | Free | Must-have |
| Character Consistency | Custom LoRA (trained) | ~$2-3 | Must-have |
| Pose/Composition Control | ControlNet (Depth + Canny) | Free | Must-have |
| Face Consistency | PuLID Adapter | Free | Recommended |
| 2D Animation | Live2D Cubism | Free tier | Nice-to-have |
| Video Generation | WAN 2.2 | Free (local) | Nice-to-have |
| Concept Exploration | Midjourney (niji mode) | $10/month | Optional |
| 3D from 2D Reference | Tripo AI | Free tier | Optional |
| Motion Capture | DeepMotion | Free tier | Optional |

### Hardware Recommendations

**Minimum viable:**
- Mac with 16GB+ unified memory (M1/M2/M3/M4) -- runs SDXL models via ComfyUI
- Or PC with RTX 3060 12GB

**Recommended:**
- PC with RTX 4070 Ti or better (16GB VRAM)
- Enables FLUX models and fast LoRA training locally

**Budget option:**
- Use cloud GPU (RunPod: ~$0.50/hour) for generation and training
- Local machine for Blender work only

### Social Media Strategy Notes

- AI virtual influencer market projected to exceed $8 billion by 2026
- Serialized content (recurring characters/episodes) drives engagement on TikTok and Reels
- Brands that disclose AI use and keep humans in creative control maintain audience trust
- Character consistency is the #1 technical challenge -- the LoRA + PuLID + ControlNet stack solves this
- Postcrest and similar tools can schedule AI character content across platforms from one dashboard

---

## Sources

### 3D Modeling
- [VRoid Studio](https://vroid.com/en/studio)
- [VRoid + Blender Pipeline](https://gamefromscratch.com/easy-anime-character-creation-with-vroid-studio-and-blender/)
- [VRoid to Blender via ARP Quick Rig](https://blenderartists.org/t/vroid-avatars-to-blender-via-arp-quick-rig/1598623)
- [LSCherry Toon Shader](https://github.com/lvoxx/LSCherry)
- [Blender Toon BSDF Manual](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/toon.html)
- [Free Anime Shaders for Blender](https://www.pixcores.com/2022/08/free-anime-shader-blender)
- [Meshmixer Status and Alternatives](https://meshmixer.org/is-meshmixer-still-worth-it-in-2025-the-case-for-blender-meshlab-others/)
- [Tripo AI](https://www.tripo3d.ai/)

### AI Image Generation
- [Best SD Anime Models 2026](https://www.aiarty.com/stable-diffusion-guide/best-stable-diffusion-anime-model.htm)
- [Best SD Models 2026 Guide](https://www.aiphotogenerator.net/blog/2026/02/best-stable-diffusion-models-2026)
- [IllustriousXL vs NoobAI-XL Comparison](https://civitai.com/articles/8642/ilxl-illustrious-xl-nai-xl-noobai-xl-model-comparison)
- [Pony V7 vs Illustrious Comparison](https://apatero.com/blog/pony-diffusion-v7-vs-illustrious-models-comparison-2025)
- [FLUX 2 Pro LoRA Training Guide](https://apatero.com/blog/flux-2-pro-lora-training-character-consistency-2026)
- [Best LoRAs for Consistent Characters 2026](https://thinkpeak.ai/best-loras-consistent-characters-2026/)
- [AI Waifu Generators: Consistent Anime Characters](https://apatero.com/blog/best-ai-waifu-generators-consistent-anime-2026)

### AI Video and Animation
- [AI Anime Video Generation Guide 2026](https://apatero.com/blog/ai-anime-video-generation-still-to-animation-2026)
- [Best AI 2D Puppet Animation Tools](https://neta.art/use-cases/en/the-best-AI-2D-puppet-animation-free-tools)
- [Live2D Cubism](https://www.live2d.com/)
- [VRoid + DeepMotion Animation](https://gamefromscratch.com/creating-animated-anime-characters-with-vroid-studio-and-deepmotion/)

### Hybrid Workflows
- [Blender + ComfyUI AI Rendering](https://www.runcomfy.com/comfyui-workflows/ai-rendering-3d-animations-with-blender-and-comfyui)
- [Blender as Pipeline Engine with ComfyUI](https://shahriyarshahrabi.medium.com/blender-as-a-pipeline-engine-make-rigged-characters-with-comfyui-3a1e81a3e623)
- [Reallusion AI Render Open Beta](https://magazine.reallusion.com/2025/07/28/ai-render-for-iclone-character-creator-enters-open-beta-with-comfyui-workflow/)
- [ControlNet Complete Guide](https://stable-diffusion-art.com/controlnet/)
- [Anime Adaptation with ControlNet](https://civitai.com/articles/24071/two-step-artists-anime-adaptation-with-controlnet)
- [Consistent Characters in ComfyUI](https://www.runcomfy.com/comfyui-workflows/create-consistent-characters-within-comfyui)
- [StableGen Blender Addon](https://github.com/sakalond/StableGen)

### Content Policy
- [Do Any AI Image Generators Allow NSFW?](https://blog.republiclabs.ai/2025/02/do-any-ai-image-generators-allow-nsfw.html)
- [Midjourney NSFW Policy 2026](https://zypa.in/midjourney-nsfw/)
- [Midjourney Community Guidelines](https://docs.midjourney.com/hc/en-us/articles/32013696484109-Community-Guidelines)
- [Midjourney Banned Words](https://cabina.ai/blog/midjourney-banned-words-what-users-need-to-know/)
- [Stability AI AUP Change (Civitai)](https://civitai.com/articles/17499/update-on-stability-ai-acceptable-use-policy-change)
- [Civitai Policy Adjustments](https://civitai.com/articles/13632/policy-and-content-adjustments)
- [Civitai Safety Center](https://civitai.com/safety)
- [OpenAI Adult Mode Discussion](https://community.openai.com/t/openai-the-policy-says-yes-the-model-says-no-stop-sterilizing-art-implement-age-verified-adult-mode/1361089)
- [AI NSFW Art: Tools, Rules & Legal Reality 2026](https://ai-art-studio.com/blog/can-ai-generate-nsfw-art-tools-limits-and-reality/)

### Social Media and Brand
- [AI Virtual Influencer Trends 2026](https://youmind.com/blog/ai-virtual-influencer-trends-2026)
- [Rise of Synthetic Personalities Report](https://o-mega.ai/articles/ais-going-viral-the-rise-of-synthetic-personalities-full-report-2025)
- [Postcrest AI Characters](https://postcrest.com/ai-characters)
