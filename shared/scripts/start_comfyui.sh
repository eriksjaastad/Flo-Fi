#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMFYUI_DIR="$PROJECT_ROOT/tools/ComfyUI"

if [ ! -d "$COMFYUI_DIR" ]; then
    echo "Error: ComfyUI not found at $COMFYUI_DIR"
    echo "Run the setup first: git clone https://github.com/comfyanonymous/ComfyUI.git $COMFYUI_DIR"
    exit 1
fi

cd "$COMFYUI_DIR"
source venv/bin/activate

# Force FP16 on Apple Silicon for better performance
python3 main.py --force-fp16 --port 8188 "$@"
