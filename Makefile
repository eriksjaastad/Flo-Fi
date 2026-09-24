.PHONY: help
help: ## Show this help message
	@echo "Flo-fi — AI Character Generation Pipeline"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "All generation commands require Doppler for API keys:"
	@echo "  doppler run -- make <target>"

.PHONY: comfyui
comfyui: ## Start ComfyUI server (local generation backend)
	./shared/scripts/start_comfyui.sh

.PHONY: generate
generate: ## Generate image using scene preset (use SCENE=desert-sunset)
	./shared/scripts/mission_control.py generate-local --scene $(or $(SCENE),desert-sunset)

.PHONY: train-grind
train-grind: ## Start training grind (continuous batch generation)
	uv run shared/scripts/train_grind.py

.PHONY: voice-swap
voice-swap: ## Speech-to-speech voice swap (use INPUT=file.wav OUTPUT=result.wav)
	@if [ -z "$(INPUT)" ] || [ -z "$(OUTPUT)" ]; then \
		echo "Error: INPUT and OUTPUT required"; \
		echo "Usage: make voice-swap INPUT=input.wav OUTPUT=output.wav"; \
		exit 1; \
	fi
	python3 shared/scripts/voice_swap.py "$(INPUT)" "$(OUTPUT)"

.PHONY: list-scenes
list-scenes: ## Show available scene presets
	./shared/scripts/mission_control.py generate-local --list-scenes

.PHONY: log-experiment
log-experiment: ## Log last generation to experiment_log.jsonl
	python3 shared/scripts/log_experiment.py

.DEFAULT_GOAL := help
