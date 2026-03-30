#!/usr/bin/env python3
"""
Mission Control - Unified command center for Flo-Fi generation pipeline
Handles: local generation, RunPod dispatch, job monitoring, result download

USAGE:
    cd "${PROJECTS_ROOT}/flo-fi"
    ./shared/scripts/mission_control.py generate --prompt "1girl, anime style" --wait
    ./shared/scripts/mission_control.py generate-local --prompt "1girl, anime style"
    ./shared/scripts/mission_control.py setup-pod
    ./shared/scripts/mission_control.py status
    ./shared/scripts/mission_control.py download --job JOB_ID
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import DEFAULT_JOB_TIMEOUT, R2_REMOTE, R2_BUCKET, R2_PREFIX

# R2 paths
R2_BASE = f"{R2_REMOTE}:{R2_BUCKET}/{R2_PREFIX}"
JOBS_PATH = "jobs"
RESULTS_PATH = "results"

# Flo's locked character face block (v20_04 baseline)
FLO_FACE = (
    "score_9, score_8_up, score_7_up, 3d character illustration, semi-realistic 3d render, "
    "young adult woman age 23, big expressive sparkling eyes with clear iris and round pupils, "
    "symmetrical close-set eyes, warm golden tanned skin, sun-kissed complexion, "
    "stylized semi-realistic proportions, beautiful detailed face, warm friendly smile, "
    "approachable expression, sharp details, high quality render, warm hazel eyes, "
    "freckles across nose and cheeks, thick expressive eyebrows"
)

FLO_NEGATIVE = (
    "photorealistic, photograph, real person, flat 2d anime, cartoon, sketch, "
    "deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, text, watermark, "
    "nsfw, nude, chibi, score_4, score_3, score_2, score_1, crossed eyes, asymmetrical eyes, "
    "wonky eyes, wide-set eyes, child, teenager, pale skin, pallid, dark circles, gothic, "
    "vampire, angry, serious, brooding"
)

# Scene presets — each has clothing, hair, setting, and lighting
SCENES = {
    "desert-sunset": {
        "description": "Desert sunset golden hour — the original v20_04 vibe",
        "hair": "shoulder-length auburn brown messy hair with flyaway strands",
        "clothing": "wearing denim jacket over band tee",
        "setting": "desert sunset golden hour lighting, strong rim lighting, bokeh background",
        "extras": "colorful purple scrunchie, outdoorsy, warm lighting",
    },
    "van-beach": {
        "description": "Sitting on van tailgate at the beach",
        "hair": "auburn brown hair in messy bun with loose strands falling around face",
        "clothing": "wearing oversized flannel shirt over tank top and cutoff shorts",
        "setting": "sitting on tailgate of vintage van at beach, golden hour sunset lighting, strong rim lighting, bokeh background",
        "extras": "colorful purple scrunchie in hair, outdoorsy, warm lighting",
    },
    "forest-camp": {
        "description": "Morning at a forest campsite",
        "hair": "auburn brown hair in low ponytail with loose bangs",
        "clothing": "wearing vintage band tee and ripped jeans",
        "setting": "leaning against camper van in forest campsite, morning sunlight through trees, strong rim lighting, bokeh background",
        "extras": "colorful purple scrunchie, outdoorsy, warm lighting",
    },
    "coastal-cliff": {
        "description": "Windswept on a coastal cliff at sunset",
        "hair": "auburn brown windswept hair blowing in breeze",
        "clothing": "wearing oversized cozy hoodie",
        "setting": "standing on cliff edge overlooking ocean, dramatic coastal sunset, wind in hair, strong rim lighting, bokeh background",
        "extras": "colorful purple scrunchie on wrist, outdoorsy, warm lighting, adventurous",
    },
    "neon-arcade": {
        "description": "Neon-lit arcade — the original v8_02 energy",
        "hair": "shoulder-length auburn brown hair with messy bangs",
        "clothing": "wearing oversized retro gaming tee and denim shorts",
        "setting": "leaning over arcade cabinet excitedly, colorful arcade lights reflecting on face, teal and magenta and yellow neon glow, fun energetic atmosphere",
        "extras": "competitive excited grin, colorful purple scrunchie",
    },
    "coffee-shop": {
        "description": "Cozy morning in a coffee shop",
        "hair": "auburn brown messy hair tucked behind one ear",
        "clothing": "wearing oversized knit sweater",
        "setting": "sitting in cozy coffee shop window seat, warm morning light streaming in, steam rising from mug, bokeh background",
        "extras": "colorful purple scrunchie on wrist, relaxed, warm lighting",
    },
    "rainy-van": {
        "description": "Rainy day inside the van, cozy vibes",
        "hair": "auburn brown hair in loose messy bun",
        "clothing": "wearing flannel pajama pants and oversized band hoodie",
        "setting": "sitting cross-legged inside camper van, rain on windows, fairy lights, laptop open, cozy warm interior lighting",
        "extras": "colorful purple scrunchie, relaxed candid moment, warm lighting",
    },
}


class MissionControl:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.log_dir = self.project_root / "data" / "generation_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "generations.jsonl"

    def log_generation(self, entry):
        """Append a generation record to the JSONL log. Every prompt, every time."""
        entry["logged_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"Logged to {self.log_file.relative_to(self.project_root)}")

    def run_rclone(self, args, check=True):
        """Run rclone command and return result"""
        cmd = ["rclone"] + args
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result

    def upload_to_r2(self, local_path, r2_path, show_progress=True):
        """Upload file or directory to R2"""
        args = ["copy", str(local_path), f"{R2_BASE}/{r2_path}"]
        if show_progress:
            args.append("--progress")
        print(f"Uploading {local_path} -> R2/{r2_path}")
        result = self.run_rclone(args)
        if result.returncode == 0:
            print("Upload complete")
        return result.returncode == 0

    def download_from_r2(self, r2_path, local_path, show_progress=True):
        """Download file or directory from R2"""
        args = ["copy", f"{R2_BASE}/{r2_path}", str(local_path)]
        if show_progress:
            args.append("--progress")
        print(f"Downloading R2/{r2_path} -> {local_path}")
        result = self.run_rclone(args)
        if result.returncode == 0:
            print(f"Download complete: {local_path}")
        return result.returncode == 0

    def create_job(self, job_type, params):
        """Create a job manifest and upload to R2"""
        job_id = f"{job_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        manifest = {
            "job_id": job_id,
            "job_type": job_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "params": params,
        }

        manifest_dir = self.project_root / "data" / "jobs"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / f"{job_id}.json"

        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"Created job: {job_id}")
        self.upload_to_r2(
            manifest_file, f"{JOBS_PATH}/pending/{job_id}.json", show_progress=False
        )
        return job_id, manifest_file

    def check_job_status(self, job_id):
        """Check if job has completed by looking for result in R2"""
        result = self.run_rclone(
            ["lsf", f"{R2_BASE}/{RESULTS_PATH}/{job_id}/"], check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return "completed"

        result = self.run_rclone(
            ["lsf", f"{R2_BASE}/{JOBS_PATH}/pending/{job_id}.json"], check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return "pending"

        result = self.run_rclone(
            ["lsf", f"{R2_BASE}/{JOBS_PATH}/processing/{job_id}.json"], check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return "processing"

        return "unknown"

    def wait_for_job(self, job_id, timeout=DEFAULT_JOB_TIMEOUT):
        """Wait for job to complete, showing progress"""
        print(f"Waiting for job {job_id}...")
        print("   (Pod agent polls every 30 seconds)")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            status = self.check_job_status(job_id)
            if status != last_status:
                if status == "processing":
                    print("Job is now processing on pod...")
                elif status == "completed":
                    print("Job completed!")
                    return True
                last_status = status
            if status == "completed":
                return True
            time.sleep(30)
            print(f"   ... still waiting ({int(time.time() - start_time)}s elapsed)")

        print(f"Timeout waiting for job after {timeout}s")
        return False

    def cmd_generate(self, args):
        """Submit a generation job to RunPod via R2"""
        negative = args.negative or "photorealistic, photograph, real person, real skin pores, flat 2d anime, cartoon, sketch, deformed, bad anatomy, bad hands, extra fingers, blurry, low quality, text, watermark, nsfw, nude, oversized breasts, uncanny valley"
        params = {
            "prompt": args.prompt,
            "negative_prompt": negative,
            "resolution": [832, 1216],
            "steps": args.steps or 30,
            "cfg_scale": args.cfg or 5.5,
            "sampler": "dpmpp_2m_karras",
            "checkpoint": "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors",
            "count": args.count or 1,
            "filename_prefix": args.prefix or "flofi",
        }

        print("Preparing generation job...")
        job_id, _ = self.create_job("generate", params)

        self.log_generation({
            "job_id": job_id,
            "target": "runpod",
            "filename_prefix": params["filename_prefix"],
            **params,
        })

        if args.wait:
            if self.wait_for_job(job_id):
                output_dir = self.project_root / "output" / job_id
                self.download_from_r2(f"{RESULTS_PATH}/{job_id}/", output_dir)
        else:
            print(f"Job dispatched: {job_id}")
            print(f"   Check status: ./shared/scripts/mission_control.py status --job {job_id}")

    def cmd_generate_local(self, args):
        """Generate locally using ComfyUI API"""
        import urllib.request

        # Handle --list-scenes
        if getattr(args, 'list_scenes', False):
            print("Available scene presets:\n")
            for name, scene in SCENES.items():
                print(f"  {name:20s} {scene['description']}")
            print(f"\nUsage: ./shared/scripts/mission_control.py generate-local --scene {list(SCENES.keys())[0]}")
            return

        # Build prompt from scene preset or raw --prompt
        if args.scene:
            scene = SCENES[args.scene]
            prompt_text = f"{FLO_FACE}, {scene['hair']}, {scene['clothing']}, {scene['setting']}, {scene['extras']}"
            if args.prompt:
                # --prompt adds extra terms on top of the scene
                prompt_text = f"{prompt_text}, {args.prompt}"
            print(f"Scene: {args.scene} — {scene['description']}")
        elif args.prompt:
            prompt_text = args.prompt
        else:
            print("Error: either --prompt or --scene is required")
            return

        negative = args.negative or FLO_NEGATIVE
        steps = args.steps or 30
        cfg = args.cfg or 5.5
        sampler_name = "dpmpp_2m"
        scheduler = "karras"
        width = 832
        height = 1216
        seed = args.seed or int(time.time())
        filename_prefix = args.prefix or "flofi"
        checkpoint = getattr(args, 'model', None) or "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
        lora_name = getattr(args, 'lora', None)
        lora_strength = getattr(args, 'lora_strength', 1.0)
        ipa_image = getattr(args, 'ipadapter', None)
        ipa_strength = getattr(args, 'ipa_strength', 0.8)

        # DreamShaper Turbo uses different settings
        if "DreamShaper" in checkpoint and "Turbo" in checkpoint:
            sampler_name = "dpmpp_sde"
            cfg = args.cfg or 2.0
            steps = args.steps or 6

        # Build workflow nodes
        # Node IDs: 3=KSampler, 4=Checkpoint, 5=LatentImage, 6=PositiveCLIP,
        #           7=NegativeCLIP, 8=VAEDecode, 9=SaveImage
        # Optional: 10=LoraLoader, 20=IPAdapterLoad, 21=CLIPVisionLoad,
        #           22=IPAdapterApply, 23=LoadImage

        # Model output reference — changes if LoRA or IPAdapter is in the chain
        model_ref = ["4", 0]
        clip_ref = ["4", 1]

        workflow_nodes = {
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": filename_prefix, "images": ["8", 0]},
            },
        }

        # Add LoRA if requested
        if lora_name:
            workflow_nodes["10"] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": ["4", 0],
                    "clip": ["4", 1],
                },
            }
            model_ref = ["10", 0]
            clip_ref = ["10", 1]
            print(f"LoRA: {lora_name} (strength: {lora_strength})")

        # Add IPAdapter if requested
        if ipa_image:
            # Use IPAdapterUnifiedLoader (auto-finds CLIP Vision + IPAdapter models)
            workflow_nodes["20"] = {
                "class_type": "IPAdapterUnifiedLoader",
                "inputs": {
                    "model": model_ref,
                    "preset": "PLUS (high strength)",
                },
            }
            workflow_nodes["23"] = {
                "class_type": "LoadImage",
                "inputs": {
                    "image": ipa_image,
                    "upload": "image",
                },
            }
            workflow_nodes["22"] = {
                "class_type": "IPAdapter",
                "inputs": {
                    "weight": ipa_strength,
                    "start_at": 0.0,
                    "end_at": 1.0,
                    "weight_type": "standard",
                    "model": ["20", 0],
                    "ipadapter": ["20", 1],
                    "image": ["23", 0],
                },
            }
            model_ref = ["22", 0]
            print(f"IPAdapter: {ipa_image} (strength: {ipa_strength})")

        # CLIP text encode nodes use the clip_ref (which may come from LoRA)
        workflow_nodes["6"] = {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt_text, "clip": clip_ref},
        }
        workflow_nodes["7"] = {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": clip_ref},
        }

        # KSampler uses model_ref (which may come from LoRA or IPAdapter)
        workflow_nodes["3"] = {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": model_ref,
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        }

        workflow = {"prompt": workflow_nodes}

        host = args.host or "127.0.0.1"
        port = args.port or 8188

        data = json.dumps(workflow).encode("utf-8")
        req = urllib.request.Request(
            f"http://{host}:{port}/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read())
            prompt_id = result.get("prompt_id", "unknown")
            print(f"Generation queued: {prompt_id}")
            print(f"Output will appear in tools/ComfyUI/output/{filename_prefix}_*.png")

            log_entry = {
                "prompt_id": prompt_id,
                "target": "local",
                "filename_prefix": filename_prefix,
                "prompt": prompt_text,
                "negative_prompt": negative,
                "checkpoint": checkpoint,
                "sampler": sampler_name,
                "scheduler": scheduler,
                "steps": steps,
                "cfg": cfg,
                "seed": seed,
                "resolution": [width, height],
            }
            if lora_name:
                log_entry["lora"] = lora_name
                log_entry["lora_strength"] = lora_strength
            if ipa_image:
                log_entry["ipadapter_image"] = ipa_image
                log_entry["ipadapter_strength"] = ipa_strength
            self.log_generation(log_entry)

        except Exception as e:
            print(f"Error connecting to ComfyUI at {host}:{port}: {e}")
            print("Make sure ComfyUI is running: ./shared/scripts/start_comfyui.sh")

    def cmd_setup_pod(self, args):
        """Upload setup scripts to R2 for pod bootstrap"""
        print("Setting up pod...")
        self.upload_to_r2(self.project_root / "shared" / "scripts", "shared/scripts")

        print("\nSetup scripts uploaded to R2")
        print("Next steps:")
        print("   1. Create RunPod A40 instance")
        print("   2. SSH to pod")
        print(f"   3. Run: rclone copy {R2_BASE}/shared/scripts/ /workspace/scripts/ && chmod +x /workspace/scripts/setup_pod.sh && /workspace/scripts/setup_pod.sh")

    def cmd_status(self, args):
        """Check job status"""
        if args.job:
            status = self.check_job_status(args.job)
            print(f"Job {args.job}: {status}")
        else:
            manifest_dir = self.project_root / "data" / "jobs"
            if manifest_dir.exists():
                manifests = sorted(
                    manifest_dir.glob("*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                print("Recent jobs (last 10):\n")
                for manifest_file in manifests[:10]:
                    with open(manifest_file) as f:
                        manifest = json.load(f)
                    status = self.check_job_status(manifest["job_id"])
                    print(f"   {manifest['job_id']}: {status} ({manifest['created_at']})")

    def cmd_download(self, args):
        """Download job results"""
        job_id = args.job
        status = self.check_job_status(job_id)
        if status != "completed":
            print(f"Job {job_id} is not completed (status: {status})")
            if not args.force:
                print("   Use --force to download anyway")
                return
        output_dir = self.project_root / "output" / job_id
        self.download_from_r2(f"{RESULTS_PATH}/{job_id}/", output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Mission Control - Flo-Fi generation pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Generate (RunPod) command
    gen_parser = subparsers.add_parser("generate", help="Submit generation job to RunPod")
    gen_parser.add_argument("--prompt", required=True, help="Generation prompt")
    gen_parser.add_argument("--negative", help="Negative prompt")
    gen_parser.add_argument("--steps", type=int, help="Sampling steps (default: 28)")
    gen_parser.add_argument("--cfg", type=float, help="CFG scale (default: 7.0)")
    gen_parser.add_argument("--count", type=int, help="Number of images (default: 1)")
    gen_parser.add_argument("--prefix", help="Filename prefix (default: flofi)")
    gen_parser.add_argument("--wait", action="store_true", help="Wait for completion")

    # Generate local command
    local_parser = subparsers.add_parser("generate-local", help="Generate locally via ComfyUI")
    local_parser.add_argument("--prompt", help="Generation prompt (optional if --scene is used)")
    local_parser.add_argument("--scene", choices=list(SCENES.keys()), help="Scene preset (use --list-scenes to see all)")
    local_parser.add_argument("--negative", help="Negative prompt")
    local_parser.add_argument("--steps", type=int, help="Sampling steps (default: 30)")
    local_parser.add_argument("--cfg", type=float, help="CFG scale (default: 5.5)")
    local_parser.add_argument("--seed", type=int, help="RNG seed (default: current timestamp)")
    local_parser.add_argument("--prefix", help="Filename prefix (default: flofi)")
    local_parser.add_argument("--host", default="127.0.0.1", help="ComfyUI host")
    local_parser.add_argument("--port", type=int, default=8188, help="ComfyUI port")
    local_parser.add_argument("--model", help="Checkpoint model name (default: Juggernaut-XL)")
    local_parser.add_argument("--lora", help="LoRA filename (e.g. pixar-style.safetensors)")
    local_parser.add_argument("--lora-strength", type=float, default=1.0, help="LoRA strength (default: 1.0)")
    local_parser.add_argument("--ipadapter", help="Reference image path for IPAdapter face lock")
    local_parser.add_argument("--ipa-strength", type=float, default=0.8, help="IPAdapter strength (default: 0.8)")
    local_parser.add_argument("--list-scenes", action="store_true", help="List available scene presets and exit")

    # Setup pod
    subparsers.add_parser("setup-pod", help="Upload setup scripts to R2")

    # Status
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("--job", help="Specific job ID")

    # Download
    dl_parser = subparsers.add_parser("download", help="Download job results")
    dl_parser.add_argument("--job", required=True, help="Job ID")
    dl_parser.add_argument("--force", action="store_true", help="Download even if not completed")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    mc = MissionControl()
    commands = {
        "generate": mc.cmd_generate,
        "generate-local": mc.cmd_generate_local,
        "setup-pod": mc.cmd_setup_pod,
        "status": mc.cmd_status,
        "download": mc.cmd_download,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
