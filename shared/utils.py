import re
import os
from pathlib import Path

def safe_slug(text: str) -> str:
    """
    Sanitize a string to be safe for filenames and path components.
    Removes anything that isn't alphanumeric, underscores, or hyphens.
    Prevents path traversal.
    """
    if not text:
        return ""
    text = os.path.basename(text)
    text = text.replace(" ", "_")
    return re.sub(r'[^a-zA-Z0-9\-_]', '', text)

def get_project_root() -> Path:
    """Get the absolute path to the project root."""
    return Path(__file__).resolve().parent.parent

def get_env_var(name: str, default=None) -> str:
    """Get environment variable. Secrets injected via: doppler run -- <command>"""
    return os.getenv(name) or default

# Centralized Constants
SDXL_RESOLUTION = 1024
NOOBAI_XL_RESOLUTION = 1024
COMFYUI_DEFAULT_STEPS = 28
COMFYUI_DEFAULT_CFG = 7.0
DEFAULT_JOB_TIMEOUT = 3600
DEFAULT_SAMPLER = "euler_ancestral"
R2_BUCKET = "pose-factory"
R2_PREFIX = "flo-fi"
R2_REMOTE = "r2_flo_fi"
