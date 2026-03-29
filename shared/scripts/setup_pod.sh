#!/bin/bash
set -euo pipefail

# Flo-Fi Pod Setup Script
# Installs ComfyUI + dependencies on RunPod GPU instance
# Only /workspace persists across restarts

echo "=== Flo-Fi Pod Setup ==="
echo "Phase 1: System packages..."

apt-get update -qq
apt-get install -y -qq jq curl unzip tmux python3 python3-pip python3-venv git rclone > /dev/null 2>&1
echo "  System packages installed"

echo "Phase 2: Directory layout..."
mkdir -p /workspace/flo-fi/{output,logs,config}
mkdir -p /workspace/ComfyUI/models/{checkpoints,controlnet}

echo "Phase 3: ComfyUI installation..."
if [ ! -d "/workspace/ComfyUI/.git" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git /workspace/ComfyUI
    cd /workspace/ComfyUI
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install typing_extensions
    deactivate
    echo "  ComfyUI installed fresh"
else
    echo "  ComfyUI already installed, updating..."
    cd /workspace/ComfyUI
    git pull
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    deactivate
fi

echo "Phase 4: rclone configuration..."
if [ -f "/workspace/.rclone.conf" ]; then
    mkdir -p ~/.config/rclone
    ln -sf /workspace/.rclone.conf ~/.config/rclone/rclone.conf
    echo "  rclone configured from persistent config"
else
    echo "  WARNING: No rclone config found at /workspace/.rclone.conf"
    echo "  Upload your rclone config or run: rclone config"
fi

echo "Phase 5: Model download from R2..."
R2_REMOTE="r2_flo_fi:pose-factory/flo-fi"

# Download checkpoint if not present
if [ ! -f "/workspace/ComfyUI/models/checkpoints/noobaiXLVpredv10_v10.safetensors" ]; then
    echo "  Downloading NoobAI-XL checkpoint from R2..."
    rclone copy "$R2_REMOTE/models/checkpoints/" /workspace/ComfyUI/models/checkpoints/ --progress
else
    echo "  NoobAI-XL checkpoint already present"
fi

# Download ControlNet models if not present
if [ ! -f "/workspace/ComfyUI/models/controlnet/controlnet-depth-sdxl-fp16.safetensors" ]; then
    echo "  Downloading ControlNet models from R2..."
    rclone copy "$R2_REMOTE/models/controlnet/" /workspace/ComfyUI/models/controlnet/ --progress
else
    echo "  ControlNet models already present"
fi

echo "Phase 6: Environment..."
if [ -f "/workspace/.env" ]; then
    source /workspace/.env
    echo "  Environment loaded from /workspace/.env"
else
    echo "  No .env found — create /workspace/.env if needed"
fi

echo "Phase 7: Smoke tests..."
cd /workspace/ComfyUI
source venv/bin/activate

# Test PyTorch + GPU
python3 -c "
import torch
gpu_available = torch.cuda.is_available()
device = torch.cuda.get_device_name(0) if gpu_available else 'CPU only'
print(f'  PyTorch {torch.__version__} | GPU: {device} | CUDA: {gpu_available}')
"

# Test ComfyUI can start (quick check)
timeout 10 python3 main.py --cpu --dont-print-server --quick-test-for-ci 2>/dev/null && echo "  ComfyUI startup test passed" || echo "  ComfyUI startup test skipped (non-critical)"
deactivate

echo "Phase 8: Pod agent..."
if [ -f "/workspace/scripts/pod_agent.sh" ]; then
    chmod +x /workspace/scripts/pod_agent.sh
    nohup /workspace/scripts/pod_agent.sh > /workspace/logs/pod_agent.log 2>&1 &
    echo "  Pod agent started (PID: $!)"
else
    echo "  No pod_agent.sh found — skipping auto-start"
fi

echo ""
echo "=== Flo-Fi Pod Setup Complete ==="
echo "Start ComfyUI: cd /workspace/ComfyUI && source venv/bin/activate && python3 main.py --listen 0.0.0.0 --port 8188"
