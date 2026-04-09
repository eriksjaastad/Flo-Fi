"""
Leonardo AI API Client — Nano Banana family

Handles image generation via Leonardo's v2 API with:
- Reference image upload and guidance
- Cost tracking per generation
- Result polling and download

USAGE:
    from leonardo import LeonardoClient

    client = LeonardoClient()
    result = client.generate(
        prompt="3d character, young woman, auburn hair",
        reference_images=["path/to/ref.png"],
        reference_strength="MID",
    )
    print(result)  # {'generation_id': ..., 'images': [...], 'cost': ...}
"""

import json
import os
import subprocess
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


# Leonardo v2 model IDs
MODELS = {
    "nano-banana": "gemini-2.5-flash-image",
    "nano-banana-pro": "gemini-image-2",
    "nano-banana-2": "gemini-3.1-flash-image-preview",
}

# Valid dimensions for v2 API
VALID_DIMENSIONS = [
    0, 672, 768, 848, 896, 928, 1024, 1152, 1200, 1264,
    1376, 1536, 1696, 1792, 1856, 2048, 2304, 2400, 2528,
    2752, 2688, 3072, 3392, 3584, 3712, 4096,
]

V2_ENDPOINT = "https://cloud.leonardo.ai/api/rest/v2/generations"
V1_ENDPOINT = "https://cloud.leonardo.ai/api/rest/v1"


def _get_api_key() -> str:
    """Get Leonardo API key. Injected via: doppler run -- <command>"""
    return os.environ["LEONARDO_API_KEY"]


class LeonardoClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or _get_api_key()
        self._headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }
        # Running cost tally for the session
        self.session_cost = 0.0
        self.session_images = 0
        self._cost_log: list[dict] = []

    def _request(self, url: str, data: Optional[dict] = None, method: str = "GET") -> dict:
        """Make an API request."""
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=self._headers, method=method)
        resp = urllib.request.urlopen(req, timeout=60)
        return json.loads(resp.read())

    def _upload_image(self, image_path: str) -> str:
        """Upload a local image and return its Leonardo image ID."""
        path = Path(image_path)
        ext = path.suffix.lstrip(".").lower()
        if ext == "jpg":
            ext = "jpeg"

        # Step 1: Get presigned upload URL
        init_resp = self._request(
            f"{V1_ENDPOINT}/init-image",
            data={"extension": ext},
            method="POST",
        )
        upload_info = init_resp["uploadInitImage"]
        image_id = upload_info["id"]
        presigned_url = upload_info["url"]
        fields = upload_info["fields"]

        # Step 2: Upload file via multipart form to S3
        # Build multipart form data manually
        boundary = "----LeonardoUpload"
        body_parts = []
        for key, value in json.loads(fields).items():
            body_parts.append(f"--{boundary}\r\n")
            body_parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n')
            body_parts.append(f"{value}\r\n")

        # Add file
        body_parts.append(f"--{boundary}\r\n")
        body_parts.append(
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        )
        content_type = f"image/{ext}"
        body_parts.append(f"Content-Type: {content_type}\r\n\r\n")

        preamble = "".join(body_parts).encode("utf-8")
        file_data = path.read_bytes()
        epilogue = f"\r\n--{boundary}--\r\n".encode("utf-8")

        full_body = preamble + file_data + epilogue

        req = urllib.request.Request(
            presigned_url,
            data=full_body,
            method="POST",
        )
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        urllib.request.urlopen(req, timeout=120)

        return image_id

    def generate(
        self,
        prompt: str,
        model: str = "nano-banana-pro",
        width: int = 1024,
        height: int = 1024,
        quantity: int = 1,
        reference_images: Optional[list[str]] = None,
        reference_strength: str = "MID",
        prompt_enhance: str = "OFF",
        seed: Optional[int] = None,
        wait: bool = True,
        poll_interval: int = 5,
        max_wait: int = 120,
    ) -> dict:
        """
        Generate images via Leonardo v2 API.

        Args:
            prompt: Text prompt
            model: Model name (nano-banana, nano-banana-pro, nano-banana-2)
            width: Image width (must be in VALID_DIMENSIONS)
            height: Image height (must be in VALID_DIMENSIONS)
            quantity: Number of images (1-4)
            reference_images: List of local file paths to use as reference
            reference_strength: LOW, MID, or HIGH
            prompt_enhance: ON or OFF
            seed: Optional seed for reproducibility
            wait: If True, poll until generation completes
            poll_interval: Seconds between polls
            max_wait: Max seconds to wait

        Returns:
            {
                'generation_id': str,
                'status': str,
                'cost': float,
                'images': [{'url': str, 'id': str}],
            }
        """
        model_id = MODELS.get(model, model)

        # Upload reference images if provided
        uploaded_ids = []
        if reference_images:
            for img_path in reference_images:
                print(f"  Uploading reference: {Path(img_path).name}")
                img_id = self._upload_image(img_path)
                uploaded_ids.append(img_id)
                print(f"  Uploaded: {img_id}")

        # Build request
        params: dict = {
            "width": width,
            "height": height,
            "prompt": prompt,
            "quantity": quantity,
            "prompt_enhance": prompt_enhance,
        }

        if seed is not None:
            params["seed"] = seed

        if uploaded_ids:
            params["guidances"] = {
                "image_reference": [
                    {
                        "image": {"id": img_id, "type": "UPLOADED"},
                        "strength": reference_strength,
                    }
                    for img_id in uploaded_ids
                ]
            }

        body = {
            "model": model_id,
            "parameters": params,
            "public": False,
        }

        # Submit
        resp = self._request(V2_ENDPOINT, data=body, method="POST")
        gen_data = resp.get("generate", resp)
        generation_id = gen_data["generationId"]
        cost = float(gen_data.get("cost", {}).get("amount", 0))

        # Track cost
        self.session_cost += cost
        self.session_images += quantity
        self._cost_log.append({
            "generation_id": generation_id,
            "model": model,
            "cost": cost,
            "quantity": quantity,
            "prompt": prompt[:80],
        })

        print(f"  Queued: {generation_id} (${cost:.4f})")

        result = {
            "generation_id": generation_id,
            "status": "PENDING",
            "cost": cost,
            "images": [],
        }

        if wait:
            result = self._poll_generation(generation_id, result, poll_interval, max_wait)

        return result

    def _poll_generation(
        self, generation_id: str, result: dict, poll_interval: int, max_wait: int
    ) -> dict:
        """Poll until generation completes."""
        elapsed = 0
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval

            resp = self._request(f"{V1_ENDPOINT}/generations/{generation_id}")
            gen = resp.get("generations_by_pk", {})
            status = gen.get("status", "UNKNOWN")

            if status == "COMPLETE":
                images = [
                    {"url": img["url"], "id": img["id"]}
                    for img in gen.get("generated_images", [])
                ]
                result["status"] = "COMPLETE"
                result["images"] = images
                print(f"  Complete: {len(images)} image(s)")
                return result

            if status == "FAILED":
                result["status"] = "FAILED"
                print(f"  FAILED: {gen.get('failReason', 'unknown')}")
                return result

        result["status"] = "TIMEOUT"
        print(f"  Timeout after {max_wait}s")
        return result

    def download_images(self, images: list[dict], output_dir: str, prefix: str = "leo") -> list[str]:
        """
        Download generated images to local directory.

        Args:
            images: List of {'url': str, 'id': str} from generate()
            output_dir: Directory to save images
            prefix: Filename prefix

        Returns:
            List of saved file paths
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        saved = []

        for i, img in enumerate(images):
            url = img["url"]
            ext = Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
            filename = f"{prefix}_{i}{ext}"
            filepath = out / filename
            # Use curl for CDN downloads (handles redirects and auth better)
            subprocess.run(
                ["curl", "-sL", "-o", str(filepath), url],
                check=True, timeout=60,
            )
            saved.append(str(filepath))
            print(f"  Saved: {filepath}")

        return saved

    def cost_report(self) -> str:
        """Return a summary of session costs."""
        lines = [
            f"Leonardo Session Cost Report",
            f"  Total: ${self.session_cost:.4f}",
            f"  Images: {self.session_images}",
            f"  Avg per image: ${self.session_cost / max(self.session_images, 1):.4f}",
            f"  Generations:",
        ]
        for entry in self._cost_log:
            lines.append(
                f"    {entry['generation_id'][:8]}... "
                f"${entry['cost']:.4f} x{entry['quantity']} "
                f"({entry['model']}) {entry['prompt']}"
            )
        return "\n".join(lines)
