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
from datetime import datetime
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import DEFAULT_JOB_TIMEOUT, R2_REMOTE, R2_BUCKET, R2_PREFIX

# R2 paths
R2_BASE = f"{R2_REMOTE}:{R2_BUCKET}/{R2_PREFIX}"
JOBS_PATH = "jobs"
RESULTS_PATH = "results"


class MissionControl:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

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
        job_id = f"{job_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        manifest = {
            "job_id": job_id,
            "job_type": job_type,
            "created_at": datetime.utcnow().isoformat(),
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
        params = {
            "prompt": args.prompt,
            "negative_prompt": args.negative or "nsfw, nude, realistic, photorealistic, deformed, bad anatomy, blurry",
            "resolution": [1024, 1024],
            "steps": args.steps or 28,
            "cfg_scale": args.cfg or 7.0,
            "sampler": "euler_ancestral",
            "checkpoint": "noobaiXLVpredv10_v10.safetensors",
            "count": args.count or 1,
        }

        print("Preparing generation job...")
        job_id, manifest_file = self.create_job("generate", params)

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

        prompt = args.prompt
        negative = args.negative or "nsfw, nude, realistic, photorealistic, deformed, bad anatomy, blurry"

        workflow = {
            "prompt": {
                "3": {
                    "class_type": "KSampler",
                    "inputs": {
                        "seed": int(time.time()),
                        "steps": args.steps or 28,
                        "cfg": args.cfg or 7.0,
                        "sampler_name": "euler_ancestral",
                        "scheduler": "normal",
                        "denoise": 1.0,
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0],
                    },
                },
                "4": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": "noobaiXLVpredv10_v10.safetensors"},
                },
                "5": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
                },
                "6": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": prompt, "clip": ["4", 1]},
                },
                "7": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": negative, "clip": ["4", 1]},
                },
                "8": {
                    "class_type": "VAEDecode",
                    "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                },
                "9": {
                    "class_type": "SaveImage",
                    "inputs": {"filename_prefix": "flofi", "images": ["8", 0]},
                },
            }
        }

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
            print(f"Generation queued: {result.get('prompt_id', 'unknown')}")
            print("Output will appear in tools/ComfyUI/output/")
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
    gen_parser.add_argument("--wait", action="store_true", help="Wait for completion")

    # Generate local command
    local_parser = subparsers.add_parser("generate-local", help="Generate locally via ComfyUI")
    local_parser.add_argument("--prompt", required=True, help="Generation prompt")
    local_parser.add_argument("--negative", help="Negative prompt")
    local_parser.add_argument("--steps", type=int, help="Sampling steps (default: 28)")
    local_parser.add_argument("--cfg", type=float, help="CFG scale (default: 7.0)")
    local_parser.add_argument("--host", default="127.0.0.1", help="ComfyUI host")
    local_parser.add_argument("--port", type=int, default=8188, help="ComfyUI port")

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
