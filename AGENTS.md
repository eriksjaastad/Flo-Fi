<!-- GENERATED FROM: ~/projects/flo-fi/CLAUDE.md -->
<!-- DO NOT EDIT DIRECTLY. Edit CLAUDE.md and run instruction-writer . --changed claude --write from the project directory -->

# CLAUDE.md - flo-fi

> **You are the floor manager of flo-fi.** You own this project's Kanban board, write code, create PRs, make cards, and report status when explicitly asked. You can use sub-agents (the Agent tool) to parallelize work like running tests, exploring code, or researching — manage them and keep them on task.

Read DECISIONS.md before changing architecture or infrastructure.

Run `pt info -p flo-fi` for models, APIs, infrastructure, and project-specific reference data.
Run `pt memory search "flo-fi"` before starting work for prior decisions and context.

## Authorization — Check Doppler First

Before saying "I need to log in" or "credentials are missing," check Doppler. A `doppler.yaml` at repo root pins this project to the `flo-fi` / `dev` config. All API keys are already injected as environment variables when you run commands via `doppler run -- <command>`.

**Available secrets (names only, never print values):**
- `ELEVEN_LABS_API_KEY` — ElevenLabs speech-to-speech voice API
- `FAL_AI_API_KEY` — Fal.ai image/video generation
- `LEONARDO_API_KEY` — Leonardo.ai image generation (legacy)
- `MESHY_API_KEY` — Meshy 3D model generation
- `R2_*` — Cloudflare R2 storage credentials (bucket, endpoint, access keys)

**Usage pattern:**
```bash
doppler run -- ./shared/scripts/mission_control.py generate-local --scene desert-sunset
doppler run -- python3 shared/scripts/voice_swap.py input.wav output.wav
```

If a secret is genuinely missing, add it via Doppler CLI or the Doppler dashboard:
```bash
doppler secrets set ELEVEN_LABS_API_KEY --value "<key>"
# or visit https://dashboard.doppler.com/ → flo-fi project → dev config
```

## What This Is

AI-generated 3D character brand for social media. An agentic pipeline that generates images, video, voice, and lip sync — all via CLI/API, zero GUI.

## Commands

```bash
# Generation
./shared/scripts/start_comfyui.sh                    # Start ComfyUI
./shared/scripts/mission_control.py generate-local --train --outfit "coral tank top" --prefix "flo_train_71_coral_tank"  # Training grind (locked settings)
./shared/scripts/mission_control.py generate-local --scene desert-sunset  # Scene presets (creative use)
./shared/scripts/mission_control.py generate-local --list-scenes           # Show scene presets

# Leonardo AI (Nano Banana family)
doppler run -- ./shared/scripts/mission_control.py generate-leonardo --prompt "3d character portrait" --model nano-banana-pro

# Voice (speech-to-speech only)
doppler run -- uv run shared/scripts/voice_swap.py input.m4a --voice matilda --out output.mp3
doppler run -- uv run shared/scripts/voice_swap.py --list-voices  # Show available voices
```

Training and infrastructure details: `pt info -p flo-fi`

## Session Continuity

If `PROGRESS.md` exists in the project root, read it FIRST before doing anything else. It contains state from your last session: what was worked on, decisions made, and next steps.

**PROGRESS.md is a snapshot, not a log.** Overwrite the entire file each session — only the most recent state matters. Keep it under 50 lines. Stale PROGRESS.md files are worse than none.


## Fully Agentic Constraint

Every step in the pipeline must be 100% agentic. No human interaction with creation tools. No GUIs. Everything runs via CLI, API, or headless scripts.

- All ComfyUI usage must be via API (mission_control.py)
- When evaluating new tools, first question: "Can an agent run this without a GUI?"

## Blender character work

When creating, editing, or evaluating Blender character assets, read
[docs/BLENDER_WORKFLOW.md](docs/BLENDER_WORKFLOW.md). Establish Flo's facial
likeness in neutral head views before finishing hair, clothing, or presentation.
Use the available headless `bpy` route when MCP is absent. The September 22,
2026 portrait was rejected; do not use it as an approved baseline. Keep technical
file checks, visual quality, and user acceptance distinct in reports and logs.

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

<!-- BEGIN scaffold:hygiene -->
## Locked Hygiene Contract

This project participates in the portfolio-wide locked hygiene contract.
Hygiene guidance now lives in agent-runtime-config; the contract is still enforced by user-scope
hooks in `~/.claude/` and by `pt` CLI commands in project-tracker. **Treat this block as the portfolio hygiene contract.** Markers are author-owned (not auto-rewritten). Prefer updates guided by agent-runtime-config docs; add project-specific notes outside the markers.

### What the contract requires

1. **No direct edits on `main`/`master`/`trunk`.** A Stop-event hook blocks
   `Edit`/`Write`/`MultiEdit`/`NotebookEdit` on tracked files while HEAD is the
   default branch. Work happens on feature branches; PRs are how changes land.
2. **No dirty session exits.** A session-end gate refuses to close while any of
   four conditions hold:
   - dirty working tree (PROGRESS.md is ignored),
   - commits ahead of upstream unpushed,
   - branch with no PR opened,
   - an authored PR still open against this repo.
3. **Audit trail for bulk changes.** Multi-file refactors, renames, and doc
   reorgs run inside `pt migration start <name>` … `pt migration finish <name>`
   so they are reversible (`--revert` uses `git restore` for tracked paths and
   `send2trash` for untracked — never raw `rm`).
4. **Handoffs are first-class.** If a session must end dirty (mid-rebase, mid-
   investigation), record it: `pt handoff create <card-pk> --branch <b> --intent
   <s> --status <s> --next <s> --guidance preserve|discard`. The session-end
   gate honors an open handoff covering the current branch.

### Safety valves

- **`.scratch/`** — every project has a gitignored `.scratch/` at its repo root.
  The branch-on-first-edit hook lets edits under any `.scratch/` subdir through
  unconditionally. Use it for throwaway notes, probe scripts, and reading-mode
  poking. Files there never reach a PR. If `.scratch/` work turns into real work,
  move it out before committing.
- **`PT_ALLOW_MAIN_EDIT=1`** — one-shot env var to bypass the main-edit hook.
  Use sparingly; intended for emergency fixes and tooling that must touch the
  default branch.
- **`PT_ALLOW_DIRTY_EXIT=1`** — one-shot env var to bypass the session-end gate.
  Every use is logged to `~/.claude/state/locked_hygiene/bypasses.jsonl`.
- **`pt handoff`** — durable alternative to the env-var bypass: the gate
  recognizes an active handoff record for the current branch and lets the
  session close.

### Quick reference

| Action                          | Command                                       |
| ------------------------------- | --------------------------------------------- |
| Start a recorded bulk migration | `pt migration start <name>`                   |
| Finish + write `MIGRATIONS.md`  | `pt migration finish <name>`                  |
| Revert a migration              | `pt migration finish <name> --revert`         |
| Open a handoff                  | `pt handoff create <card-pk> --branch <b> …`  |
| List open handoffs              | `pt handoff list`                             |
| Resolve a handoff               | `pt handoff resolve <id>`                     |
| Refresh this block portfolio-wide | Manual / agent-runtime-config guidance (scaffold sync CLI retired #6833) |
<!-- END scaffold:hygiene -->

<!-- BEGIN runtime-doctor:shared:code-review-rules -->
## Code Review Rules

> **Authored once, in `agent-runtime-config`. Compiled into every repo's `AGENTS.md` so the
> reviewer sees it in-repo.** Do not hand-copy this into a project file — if it is missing
> from a repo, that is a propagation bug, not a licence to paste.
>
> **This is the condensed block.** Every repo pays its cost on every agent launch, not only
> during review, so it carries only what a reviewer needs in-repo. The full standards —
> judgment checks, reporting format, blast-radius tiers, convergence detail — are in
> `agent-runtime-config/docs/code-review-protocol.md`. Read that when reviewing.

Provider-neutral on purpose: Codex, Claude and any future reviewer read the same list.

### Gate 0 — mechanical scan

A failure prevents a PASS but does not end the review. Finish the other checks and report
together. If a failure prevents a check from running, name that coverage gap.

| ID | Check |
|----|-------|
| M1 | **Portable paths.** Flag machine-specific paths in executable code/config or prescribed setup commands. Illustrative examples and committed evidence are not runtime dependencies. |
| M2 | **No swallowed unexpected failures.** Flag `except: pass` when it hides an operation failure from the caller. Documented best-effort handling is valid. |
| M3 | No real credentials in files. Secrets come from Doppler. Synthetic fixtures are permitted. |
| M4 | No unresolved placeholders in rendered deliverables or runtime config. Templates and fixtures may contain them. |
| M5 | No JS redeclarations in changed `.js` under any `static` directory. Run `npx eslint --no-config-lookup --rule '{"no-redeclare": "error"}' <paths>`. Skip when the diff has none. |

### Scope — the question that ends a review

- **Was this behaviour actually requested?** If not, reject it, however good it is.
- **Does the change stay inside the task it claims?** Scope creep is a finding.
- **Does the code state where its responsibility ends?** When a file declares a contract —
  in its own docstring or header, not the PR body — a finding outside that contract is
  closed by citing it. Judge such a finding by whether the stated user would plausibly hit
  it in normal use, not by whether it is reachable at all.

### Converging — and when to stop

- **Aim for two or three rounds.** If the same defect family returns, reassess the
  implementation rather than applying another narrow patch.
- **A third round is a stop, not a speed limit.** Correctness is never waived; but a third
  round means the PR is the wrong SHAPE, not that the bug is acceptable. Take one of these,
  none of which merges broken code:
  - **Split the PR.** A diff that grew under review is the usual cause. Land what matches
    the cards it was opened for; move the rest.
  - **State the contract** in the artifact, then close out-of-contract findings by citing it.
  - **Escalate.** Only the human waives a finding, naming repo, PR, exact head and gate.
- **Say which kind each finding is.** A pre-existing defect newly uncovered is the review
  working. A defect the PREVIOUS fix introduced is a regression — report it as such.
  **Two introduced regressions in one PR is a stop**: the approach is generating them, and
  a round that both opens and closes holes has negative return.
- **Before requesting review, test what the fix might have BROKEN**, not only what it was
  meant to fix, and name those cases. A fix is finished when the neighbouring legitimate
  cases still pass. Review spent catching this is review spent on work that should not
  have been submitted.
- **Provider review draws on a FIXED SUBSCRIPTION ALLOWANCE.** Exhausting it is a hard stop
  that blocks review on every other repository, not a larger invoice. Consumption scales
  with DIFF SIZE, since each round re-reads the whole diff. Batch a round's findings into
  one fix and one re-request; never fix-one-then-re-request. Run the free local reviewer
  first.
<!-- END runtime-doctor:shared:code-review-rules -->
