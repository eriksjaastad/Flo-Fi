# Antigravity Rules for flo-fi

<!-- AUTO-GENERATED from .agentsync/rules/ - Do not edit directly -->
<!-- Run: uv run $TOOLS_ROOT/agentsync/sync_rules.py flo-fi -->

# AGENTS.md - Source of Truth for AI Agents

## 🎯 Project Overview
{project_description}

## 🛠 Tech Stack
- Language: {language}
- Frameworks: {frameworks}
- AI Strategy: {ai_strategy}

## 📋 Definition of Done (DoD)
- [ ] Code is documented with type hints.
- [ ] Technical changes are logged to `project-tracker/data/WARDEN_LOG.yaml`.
- [ ] `00_Index_*.md` is updated with recent activity.
- [ ] Code validated (no hardcoded paths, no secrets exposed).
- [ ] Code review completed (if significant architectural changes).
- [ ] [Project-specific DoD item]

## 🚀 Execution Commands
- Environment: `{venv_activation}`
- Run: `{run_command}`
- Test: `{test_command}`

## ⚠️ Critical Constraints
- NEVER hard-code API keys, secrets, or credentials in script files. Use `.env` and `os.getenv()`.
- NEVER use absolute paths (e.g., machine-specific paths). ALWAYS use relative paths or `PROJECT_ROOT` env var.
- ALWAYS run validation before considering work complete: `python "./scripts/validate_project.py" [project-name]`
- {constraint_1}
- {constraint_2}

**Code Review Standards:** See `./REVIEWS_AND_GOVERNANCE_PROTOCOL.md` for full review process.

## 📖 Reference Links
- `00_Index_*.md`
- [[Project Philosophy]]
