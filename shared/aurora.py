"""
xAI Aurora / Grok Imagine Video API Client

Handles video generation via xAI's v1 API with:
- Multi-image storyboard → video (image-to-video)
- Text-to-video generation
- Async polling for completion
- Cost tracking per generation

USAGE:
    from aurora import AuroraClient
    
    client = AuroraClient()
    result = client.generate_video(
        prompt="Cinematic slow push-in as embers drift across the battlefield",
        image_path="path/to/frame.png",
        duration=10,
        resolution="720p",
    )
    print(result)  # {'request_id': ..., 'video_url': ..., 'duration': ...}
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional


# xAI API endpoints
XAI_BASE_URL = "https://api.x.ai/v1"
VIDEO_ENDPOINT = f"{XAI_BASE_URL}/videos/generations"

# Valid parameters
VALID_RESOLUTIONS = ["480p", "720p", "1080p"]
VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]
MIN_DURATION = 1
MAX_DURATION = 15
DEFAULT_DURATION = 8
DEFAULT_RESOLUTION = "720p"
DEFAULT_MODEL = "grok-imagine-video-1.5"

# Polling defaults
DEFAULT_POLL_INTERVAL = 5  # seconds
DEFAULT_MAX_WAIT = 300  # 5 minutes


def _get_api_key() -> Optional[str]:
    """
    Get xAI API key from environment.
    Returns None if not set (for dry-run mode).
    """
    return os.environ.get("XAI_API_KEY")


class AuroraClient:
    def __init__(self, api_key: Optional[str] = None, dry_run: bool = False):
        """
        Initialize Aurora client.
        
        Args:
            api_key: xAI API key. If None, reads from XAI_API_KEY env var.
            dry_run: If True, validate inputs but don't make API calls.
        """
        self.api_key = api_key or _get_api_key()
        self.dry_run = dry_run
        
        if not self.dry_run and not self.api_key:
            print("ERROR: XAI_API_KEY environment variable not set.", file=sys.stderr)
            print("Set it with: export XAI_API_KEY='your-key-here'", file=sys.stderr)
            print("Or run in dry-run mode with --dry-run flag.", file=sys.stderr)
            sys.exit(1)
        
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        # Session tracking
        self.session_videos = 0
        self._request_log: list[dict] = []
    
    def _request(self, url: str, data: Optional[dict] = None, method: str = "GET") -> dict:
        """Make an API request."""
        if self.dry_run:
            raise RuntimeError("Cannot make API requests in dry-run mode")
        
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=self._headers, method=method)
        
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"ERROR: API request failed: {e.code} {e.reason}", file=sys.stderr)
            print(f"Response: {error_body}", file=sys.stderr)
            raise
    
    def generate_video(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        duration: int = DEFAULT_DURATION,
        resolution: str = DEFAULT_RESOLUTION,
        aspect_ratio: Optional[str] = None,
        wait: bool = True,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        max_wait: int = DEFAULT_MAX_WAIT,
    ) -> dict:
        """
        Generate a video from a text prompt and optional image.
        
        Args:
            prompt: Text description of desired motion/action
            image_path: Optional path to starting image (for image-to-video)
            model: Model name (default: grok-imagine-video-1.5)
            duration: Video duration in seconds (1-15)
            resolution: Output resolution (480p, 720p, 1080p)
            aspect_ratio: Optional aspect ratio (1:1, 16:9, 9:16, etc.)
            wait: If True, poll until generation completes
            poll_interval: Seconds between status polls
            max_wait: Maximum seconds to wait for completion
        
        Returns:
            {
                'request_id': str,
                'status': str,  # 'pending', 'processing', 'done', 'failed', 'timeout'
                'video_url': str or None,
                'duration': int or None,
                'model': str,
                'dry_run': bool,
            }
        """
        # Validate inputs
        if duration < MIN_DURATION or duration > MAX_DURATION:
            raise ValueError(f"Duration must be between {MIN_DURATION} and {MAX_DURATION} seconds")
        
        if resolution not in VALID_RESOLUTIONS:
            raise ValueError(f"Resolution must be one of: {', '.join(VALID_RESOLUTIONS)}")
        
        if aspect_ratio and aspect_ratio not in VALID_ASPECT_RATIOS:
            raise ValueError(f"Aspect ratio must be one of: {', '.join(VALID_ASPECT_RATIOS)}")
        
        if image_path:
            # Validate image path/URL
            if not self.dry_run:
                # Live runs require HTTPS URLs (xAI API requirement)
                if not (image_path.startswith("https://") or image_path.startswith("http://")):
                    print("ERROR: --image must be an HTTPS URL for live API calls.", file=sys.stderr)
                    print("Local file paths are only supported with --dry-run.", file=sys.stderr)
                    print("", file=sys.stderr)
                    print("Options:", file=sys.stderr)
                    print("  1. Upload your image to a public/signed HTTPS URL", file=sys.stderr)
                    print("  2. Use --dry-run flag to test with local paths", file=sys.stderr)
                    print("  3. Wait for xAI Files API upload support (not yet implemented)", file=sys.stderr)
                    sys.exit(1)
            # In dry-run mode, accept any path format without validation
        
        # Build request payload
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
        }
        
        if aspect_ratio:
            payload["aspect_ratio"] = aspect_ratio
        
        if image_path:
            # xAI API requires HTTPS URL for image parameter
            payload["image"] = {
                "url": image_path
            }
        
        # Dry run mode
        if self.dry_run:
            print("DRY RUN: Would submit video generation request:")
            print(json.dumps(payload, indent=2))
            return {
                "request_id": "dry-run-request-id",
                "status": "dry_run",
                "video_url": None,
                "duration": None,
                "model": model,
                "dry_run": True,
                "payload": payload,
            }
        
        # Submit generation request
        print(f"Submitting video generation: {prompt[:60]}...")
        resp = self._request(VIDEO_ENDPOINT, data=payload, method="POST")
        request_id = resp["request_id"]
        
        # Track request
        self.session_videos += 1
        self._request_log.append({
            "request_id": request_id,
            "model": model,
            "prompt": prompt[:80],
            "duration": duration,
            "resolution": resolution,
            "has_image": bool(image_path),
        })
        
        print(f"  Queued: {request_id}")
        
        result = {
            "request_id": request_id,
            "status": "pending",
            "video_url": None,
            "duration": None,
            "model": model,
            "dry_run": False,
        }
        
        if wait:
            result = self._poll_video(request_id, result, poll_interval, max_wait)
        
        return result
    
    def _poll_video(
        self,
        request_id: str,
        result: dict,
        poll_interval: int,
        max_wait: int,
    ) -> dict:
        """Poll video generation status until complete."""
        elapsed = 0
        status_url = f"{XAI_BASE_URL}/videos/{request_id}"
        
        print(f"  Polling for completion (max {max_wait}s)...")
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            try:
                resp = self._request(status_url)
            except Exception as e:
                print(f"  Poll error: {e}", file=sys.stderr)
                continue
            
            status = resp.get("status", "unknown")
            result["status"] = status
            
            if status == "done":
                video_data = resp.get("video", {})
                result["video_url"] = video_data.get("url")
                result["duration"] = video_data.get("duration")
                print(f"  ✓ Complete: {result['video_url']}")
                return result
            
            if status == "failed":
                error = resp.get("error", {})
                print(f"  ✗ FAILED: {error.get('message', 'unknown error')}", file=sys.stderr)
                return result
            
            # Still processing
            print(f"  [{elapsed}s] Status: {status}")
        
        result["status"] = "timeout"
        print(f"  ⚠ Timeout after {max_wait}s - video may still be processing")
        return result
    
    def check_status(self, request_id: str) -> dict:
        """
        Check the status of a video generation request.
        
        Args:
            request_id: The request ID returned from generate_video()
        
        Returns:
            dict with status, video_url (if done), and duration
        """
        if self.dry_run:
            return {
                "request_id": request_id,
                "status": "dry_run",
                "video_url": None,
                "duration": None,
                "dry_run": True,
            }
        
        status_url = f"{XAI_BASE_URL}/videos/{request_id}"
        resp = self._request(status_url)
        
        status = resp.get("status", "unknown")
        result = {
            "request_id": request_id,
            "status": status,
            "video_url": None,
            "duration": None,
            "dry_run": False,
        }
        
        if status == "done":
            video_data = resp.get("video", {})
            result["video_url"] = video_data.get("url")
            result["duration"] = video_data.get("duration")
        
        return result
    
    def download_video(self, video_url: str, output_path: str) -> str:
        """
        Download a generated video to local file.
        
        Args:
            video_url: URL of the generated video
            output_path: Local path to save video
        
        Returns:
            Path to saved file
        """
        if self.dry_run:
            print(f"DRY RUN: Would download {video_url} to {output_path}")
            return output_path
        
        print(f"Downloading video to {output_path}...")
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Download with urllib
        urllib.request.urlretrieve(video_url, output_path)
        
        file_size = Path(output_path).stat().st_size
        print(f"  ✓ Saved: {output_path} ({file_size / 1024 / 1024:.1f} MB)")
        
        return output_path
    
    def session_report(self) -> str:
        """Return a summary of session activity."""
        lines = [
            "Aurora Session Report",
            f"  Videos: {self.session_videos}",
            f"  Requests:",
        ]
        for entry in self._request_log:
            has_img = "I2V" if entry["has_image"] else "T2V"
            lines.append(
                f"    {entry['request_id'][:12]}... "
                f"{has_img} {entry['duration']}s {entry['resolution']} "
                f"({entry['model']}) {entry['prompt']}"
            )
        return "\n".join(lines)
