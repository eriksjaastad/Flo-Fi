# Flo-Fi Roadmap

## Core Constraint: Fully Agentic

**Every step in the pipeline must be 100% agentic.** Zero human interaction with creation tools. No GUIs. Everything runs via CLI, API, or headless scripts. An agent writes the prompts, submits jobs, reviews output, and posts to social media.

---

## Phase 1 — Toolchain Setup (COMPLETE)

Get the creation pipeline working end-to-end.

| Task | Status |
|------|--------|
| ~~Install VRoid Studio~~ | **Cancelled** — GUI tool, violates agentic constraint |
| Set up ComfyUI + NoobAI-XL | **Done** — MPS backend, 24GB VRAM, PyTorch 2.11 |
| Install ControlNet models | **Done** — Depth + canny (4.3GB) |
| Blender anime shader setup | **Done** — VRM Importer + LSCherry toon shader |
| End-to-end pipeline test | **Done** — First anime image generated via API |
| Create Doppler project | **Done** — R2 credentials stored |
| Copy 3d-pose-factory infra | **Done** — Mission Control, setup_pod.sh, cost calculator |
| Create social accounts | **Pending** — Requires Erik (browser + CAPTCHAs) |
| X Premium subscription | **Pending** — Requires Erik (payment) |

**Milestone:** One AI-stylized character image produced through the fully agentic pipeline. **ACHIEVED.**

---

## Phase 2 — First Characters

Create the founding cast. All character design is agentic — agents craft prompts, generate variations, select best outputs, and iterate.

| Task | Description |
|------|-------------|
| Style exploration | Agent batch-generates with different prompt strategies, samplers, CFG values to find "the Flo-Fi look" |
| Define the Flo-Fi style | Lock in the prompt template, negative prompt, and generation parameters that produce our signature aesthetic |
| Design Character 1 | First named character — personality doc + 5-10 hero images via ComfyUI API |
| Design Character 2 | Second character — contrasting aesthetic |
| Design Character 3 | Third character — rounds out the cast |
| Train character LoRA | Train a style LoRA on best outputs for visual consistency |
| Produce hero images | 10-15 high-quality images across all 3 characters |
| Character sheets | Expression/outfit variations generated via prompt engineering |
| Define brand color palette | Extract from the best outputs |
| Design logo/wordmark | Agent-generated via ComfyUI or text-to-image |

**Milestone:** 3 named characters with 15+ production-quality images and a locked visual identity. All generated agentically.

---

## Phase 3 — First Content Drop

Launch day. All platforms go live simultaneously.

| Task | Description |
|------|-------------|
| Set up Buffer/scheduling | Cross-posting tool for managing 5 platforms (agent-operable via API) |
| Prepare launch batch | 2-3 posts per platform, scheduled for optimal times |
| Write platform bios | Final bios with consistent voice across all accounts |
| Update social avatars | Logo/character avatar on all platforms |
| Launch on Twitter/X | First posts — hero images + character introductions |
| Launch on Instagram | Carousel posts with character reveals |
| Launch on TikTok | Short-form video content — character card reveals with audio |
| Launch on Reddit | Post to r/StableDiffusion, r/AIArtLounge, r/AnimeArt (AI-friendly subs only) |
| Launch on Facebook | Page setup + initial posts |
| Behind-the-scenes content | Process shots from Blender/ComfyUI — builds trust and engagement |

**Milestone:** All 5 platforms live with initial content. Flo-Fi exists publicly.

---

## Phase 4 — Growth

Sustain, iterate, expand. This phase is ongoing.

| Task | Description |
|------|-------------|
| Establish posting cadence | 4-5 posts/week across platforms. Weekly content calendar |
| Content series: Character of the Week | Deep-dive on one character per week — lore, outfits, expressions |
| Content series: Outfit Swap | Characters in each other's outfits. High engagement format |
| Engagement strategy | Reply to comments, engage with other anime accounts, join conversations |
| Analytics review | Weekly check on what's performing. Double down on winners |
| Expand character roster | New characters based on audience response |
| Explore animation | AI-generated animation loops for TikTok/Reels (must be agentic) |
| Monetization exploration | When audience hits critical mass — merch, prints, Patreon |

**Milestone:** Consistent posting cadence with growing follower counts across platforms.

---

## Open Questions (Revisit as we go)

- What is "the Flo-Fi style"? — Needs style exploration (Phase 2, first task)
- Do characters have connected lore / a shared universe?
- What's the posting cadence sweet spot for agentic capacity?
- When do we invest in animation (Phase 4 or later)?
- At what follower count does monetization make sense?
- Do we want a Flo-Fi website/portfolio eventually?
- Can social media posting be fully agentic? (Buffer API, Twitter API, etc.)
