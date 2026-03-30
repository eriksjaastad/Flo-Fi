# Flo-Fi Roadmap

## Core Constraint: Fully Agentic

**Every step in the pipeline must be 100% agentic.** Zero human interaction with creation tools. No GUIs. Everything runs via CLI, API, or headless scripts. An agent writes the prompts, submits jobs, reviews output, and posts to social media.

---

## Phase 1 — Toolchain Setup (COMPLETE)

Get the creation pipeline working end-to-end.

| Task | Status |
|------|--------|
| Set up ComfyUI + models | **Done** — MPS backend, M4 Pro, PyTorch 2.11 |
| Install ControlNet models | **Done** — Depth + canny (4.3GB) |
| End-to-end pipeline test | **Done** — First image generated via API |
| Create Doppler project | **Done** — R2 credentials stored |
| Copy 3d-pose-factory infra | **Done** — Mission Control, setup_pod.sh |
| Create social accounts | **Pending** — Requires Erik (browser + CAPTCHAs) |

**Milestone:** One AI-stylized character image produced through the fully agentic pipeline. **ACHIEVED.**

---

## Phase 2 — Flo (IN PROGRESS)

Create and lock Flo's character. All design is agentic — agents craft prompts, generate variations, and iterate.

| Task | Status |
|------|--------|
| Style exploration | **Done** — Found RealCartoon-Pony V3 as the right model |
| Define the Flo-Fi style | **In progress** — v20_04 is baseline, needs fresh-eyes confirmation |
| Character bible | **Done** — Flo's personality, backstory, drone companion locked |
| Scene presets | **Done** — 7 scenes in `--scene` flag (#5432) |
| Train Flo LoRA | **In progress** — SimpleTuner installed, need 20-30 training images (#5400) |
| Produce hero images | Blocked on LoRA training |
| Character sheets | Blocked on face lock |
| Design Characters 2 & 3 | Backlog |
| Define brand color palette | Backlog |
| Design logo/wordmark | Backlog |

**Key style findings:**
- Target: 3D character illustration / semi-realistic anime 3D (NOT Pixar)
- RealCartoon-Pony V3 nails this aesthetic out of the box
- Juggernaut-XL = photorealistic soul, wrong style. Pixar LoRAs = wrong category entirely.
- IPAdapter fights with RealCartoon-Pony; custom LoRA is the real consistency solution

**Milestone:** Flo's face locked, LoRA trained, 15+ hero images across scenes.

---

## Phase 3 — Content Pipeline + Launch

Build the fully agentic video pipeline and launch on social media.

### Video Pipeline (all API-driven)

| Step | Tool | API | Cost | Card |
|------|------|-----|------|------|
| Images → video | Grok Aurora | Multi-image storyboard, up to 7 images → 15sec video | $0.05/sec | #5433 |
| Script → voice | ElevenLabs | Speech-to-speech voice replacement (NOT text-to-speech) | $5/mo | #5435 |
| Video + voice → lip sync | PixVerse | Pass video + audio → lip-synced output | TBD | #5434 |
| Orchestration | mission_control.py | End-to-end pipeline script | Local | #5436 |

**Critical note on voice:** Use speech-to-speech, not text-to-speech. Someone performs lines with real emotion, ElevenLabs replaces the voice. TTS sounds flat. (From Daisy Studios creator.)

### Social Launch

| Task | Description |
|------|-------------|
| Set up Buffer/scheduling | Cross-posting via API |
| Prepare launch batch | 2-3 posts per platform |
| Write platform bios | Consistent voice across accounts |
| Launch on Twitter/X, Instagram, TikTok, Reddit, Facebook | Simultaneous |
| Behind-the-scenes content | Process shots build trust |

**Milestone:** Fully autonomous content pipeline: write a script → agents handle the rest → TikTok-ready video. All 5 platforms live.

---

## Phase 4 — Growth

Sustain, iterate, expand. Ongoing.

| Task | Description |
|------|-------------|
| Posting cadence | 4-5 posts/week, content calendar |
| Content series | Character of the Week, Outfit Swap |
| Engagement | Reply to comments, engage with anime community |
| Analytics | Weekly review, double down on winners |
| Expand roster | New characters based on audience response |
| Animation | AI-generated loops for TikTok/Reels |
| Monetization | Merch, prints, Patreon when audience hits critical mass |

**Milestone:** Consistent posting with growing follower counts.

---

## Open Questions

- Do characters have connected lore / a shared universe?
- What's the posting cadence sweet spot for agentic capacity?
- At what follower count does monetization make sense?
- Do we want a Flo-Fi website/portfolio eventually?
