# Decisions

Deliberate architectural choices. Read before changing anything structural.
To revisit a decision, don't edit — add a new entry that supersedes it.

---

## 100% Agentic Pipeline — No GUI Allowed
**Accepted 2026-04-04**

Image generation tools like ComfyUI ship with web UIs for human interaction. Flo-fi must be fully autonomous — no human in the loop during generation. All tools must be CLI/API-driven with zero GUI interaction. ComfyUI operations are wrapped as headless API calls in `mission_control.py`.

| Alternative | Why rejected |
|-------------|-------------|
| GUI-assisted workflow | Breaks autonomy — requires a human to click buttons |
| Hybrid mode (GUI for setup, API for runs) | Creates dependency on human availability |
| Alternative tools without API support | Non-automatable, defeats the purpose |

Full automation from prompt to published image. Trade-off: harder initial setup — must reverse-engineer the API for every ComfyUI operation. But this enables unattended generation, which is the entire point.

---

## Locked Character Face Block + Scene Presets
**Accepted 2026-04-04**

Flo is a brand character. Every image must be recognizably "Flo" while allowing scene variation. `FLO_FACE` and `FLO_NEGATIVE` are hardcoded constants in `mission_control.py`. Seven predefined scene presets control clothing and setting while keeping facial features locked. Face constants are NOT parameterized — that is the whole point.

| Alternative | Why rejected |
|-------------|-------------|
| Dynamic face generation | Inconsistent character across images |
| Fully dynamic prompts | Brand drift — Flo stops looking like Flo |
| Single fixed scene | No content variety |

Brand consistency across all generations. Trade-off: adding a new scene requires a code change. This is deliberate friction — it forces intentional scene design rather than random prompt experimentation.

---

## Immutable Generation Log (JSONL) Over Database
**Accepted 2026-04-04**

Need to track every generation with full parameters for reproducibility and training data curation. Append-only JSONL file at `data/generation_logs/generations.jsonl`. Each line captures complete parameters: prompt, model, sampler, seed, CFG, steps, and output path.

| Alternative | Why rejected |
|-------------|-------------|
| SQLite database | Over-engineered for append-only log |
| Structured CSV | Poor for nested data (prompt metadata, sampler configs) |
| No logging | Loses reproducibility — can't recreate or audit generations |

Simple, auditable, reproducible. Any generation can be replayed from its log entry. Trade-off: no indexing or querying without loading the file. Acceptable at current generation volume.
