"""ComfyUI headless client – connects to ComfyUI running on vast.ai."""

import json
import logging
import asyncio
import uuid
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

WORKFLOWS_DIR = Path(__file__).parent.parent / "comfyui_workflows"


class ComfyUIClient:
    """Communicates with a remote ComfyUI instance via REST API."""

    def __init__(self, host: str):
        """host = ip:port of the ComfyUI instance."""
        self.base_url = f"http://{host}"
        self.client_id = str(uuid.uuid4())

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/system_stats")
                return resp.status_code == 200
        except Exception:
            return False

    def load_workflow(self, workflow_name: str) -> dict:
        """Load a workflow JSON template from disk."""
        path = WORKFLOWS_DIR / workflow_name
        if not path.exists():
            raise FileNotFoundError(f"Workflow not found: {path}")
        with open(path, "r") as f:
            return json.load(f)

    def inject_params(
        self,
        workflow: dict,
        params: dict,
    ) -> dict:
        """Inject parameters into a workflow template.

        Supported params:
        - prompt: text prompt for generation
        - negative_prompt: negative prompt
        - seed: random seed
        - lora_name: LoRA model filename
        - lora_strength: LoRA strength (0-1)
        - avatar_embedding: path to face embedding
        - controlnet_type: type of ControlNet
        - width, height: output dimensions
        - frames: number of frames
        - fps: frames per second
        """
        workflow_str = json.dumps(workflow)

        # Simple template variable replacement
        replacements = {
            "{{PROMPT}}": params.get("prompt", ""),
            "{{NEGATIVE_PROMPT}}": params.get("negative_prompt", ""),
            "{{SEED}}": str(params.get("seed", 42)),
            "{{LORA_NAME}}": params.get("lora_name", ""),
            "{{LORA_STRENGTH}}": str(params.get("lora_strength", 0.8)),
            "{{AVATAR_EMBEDDING}}": params.get("avatar_embedding", ""),
            "{{CONTROLNET_TYPE}}": params.get("controlnet_type", "openpose"),
            "{{WIDTH}}": str(params.get("width", 1280)),
            "{{HEIGHT}}": str(params.get("height", 720)),
            "{{FRAMES}}": str(params.get("frames", 120)),
            "{{FPS}}": str(params.get("fps", 24)),
        }

        for key, value in replacements.items():
            workflow_str = workflow_str.replace(key, value)

        return json.loads(workflow_str)

    async def queue_prompt(self, workflow: dict) -> str:
        """Submit a workflow to ComfyUI queue. Returns prompt_id."""
        payload = {
            "prompt": workflow,
            "client_id": self.client_id,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{self.base_url}/prompt", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["prompt_id"]

    async def get_progress(self, prompt_id: str) -> dict:
        """Get execution progress for a prompt."""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}/history/{prompt_id}")
            resp.raise_for_status()
            history = resp.json()
            if prompt_id in history:
                return history[prompt_id]
            return {"status": "pending"}

    async def wait_for_completion(
        self,
        prompt_id: str,
        timeout_sec: int = 600,
        poll_interval: int = 5,
        progress_callback=None,
    ) -> dict:
        """Poll until prompt execution completes."""
        elapsed = 0
        while elapsed < timeout_sec:
            progress = await self.get_progress(prompt_id)
            status = progress.get("status", {})

            if isinstance(status, dict) and status.get("completed", False):
                return progress

            if isinstance(status, dict) and status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI execution error: {progress}")

            # Calc rough progress
            if progress_callback and isinstance(status, dict):
                msgs = status.get("messages", [])
                if msgs:
                    await progress_callback(len(msgs), elapsed)

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"ComfyUI prompt {prompt_id} timed out after {timeout_sec}s")

    async def download_output(
        self,
        prompt_id: str,
        output_node: str = "SaveVideo",
    ) -> Optional[bytes]:
        """Download the output file from ComfyUI."""
        progress = await self.get_progress(prompt_id)
        outputs = progress.get("outputs", {})

        for node_id, node_output in outputs.items():
            if "videos" in node_output:
                video = node_output["videos"][0]
                filename = video["filename"]
                subfolder = video.get("subfolder", "")

                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.get(
                        f"{self.base_url}/view",
                        params={
                            "filename": filename,
                            "subfolder": subfolder,
                            "type": "output",
                        },
                    )
                    resp.raise_for_status()
                    return resp.content

            elif "images" in node_output:
                image = node_output["images"][0]
                filename = image["filename"]
                subfolder = image.get("subfolder", "")

                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.get(
                        f"{self.base_url}/view",
                        params={
                            "filename": filename,
                            "subfolder": subfolder,
                            "type": "output",
                        },
                    )
                    resp.raise_for_status()
                    return resp.content

        return None

    async def upload_image(self, image_data: bytes, filename: str) -> str:
        """Upload an image to ComfyUI input folder."""
        async with httpx.AsyncClient(timeout=30) as client:
            files = {"image": (filename, image_data, "image/png")}
            resp = await client.post(f"{self.base_url}/upload/image", files=files)
            resp.raise_for_status()
            data = resp.json()
            return data.get("name", filename)
