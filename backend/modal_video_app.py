"""
Modal deployment script for Image-to-Video using Stable Video Diffusion (SVD).
Deploy this using: `modal deploy modal_video_app.py`
"""

import modal
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import io
import base64
import os

# Define the Modal App and Image
app = modal.App("video-generate-svd")

image = (
    modal.Image.debian_slim()
    .pip_install(
        "torch",
        "diffusers",
        "transformers",
        "accelerate",
        "safetensors",
        "pillow",
        "fastapi[standard]"
    )
)

# Authentication setup
TOKEN_ID = os.environ.get("MODAL_TOKEN_ID", "wk-zgKLgaMEjSbsJJfCnoGZm4")
TOKEN_SECRET = os.environ.get("MODAL_TOKEN_SECRET", "ws-fKNahBbuJRC4OXpd8pnrkO")

def check_auth(request: Request):
    auth_id = request.headers.get("x-modal-token-id")
    auth_secret = request.headers.get("x-modal-token-secret")
    if auth_id != TOKEN_ID or auth_secret != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Inference Container
@app.cls(gpu="A10G", container_idle_timeout=300, image=image)
class VideoGenerator:
    @modal.enter()
    def setup(self):
        import torch
        from diffusers import StableVideoDiffusionPipeline
        
        print("Loading SVD model...")
        self.pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt", 
            torch_dtype=torch.float16, 
            variant="fp16"
        )
        self.pipe.enable_model_cpu_offload()
        print("Model loaded successfully.")

    @modal.method()
    def generate(self, init_image_b64: str, fps: int = 7, motion_bucket_id: int = 127):
        import torch
        from PIL import Image
        from diffusers.utils import export_to_video
        import tempfile
        
        # Load image
        img_bytes = base64.b64decode(init_image_b64)
        init_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        init_image = init_image.resize((1024, 576))  # SVD XT native resolution

        print(f"Generating video...")
        generator = torch.manual_seed(42)
        frames = self.pipe(
            init_image, 
            decode_chunk_size=8, 
            generator=generator,
            fps=fps,
            motion_bucket_id=motion_bucket_id
        ).frames[0]
        
        # Export video to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_file.close()
        export_to_video(frames, temp_file.name, fps=fps)
        
        # Read file and encode to base64
        with open(temp_file.name, "rb") as f:
            video_bytes = f.read()
            video_b64 = base64.b64encode(video_bytes).decode('utf-8')
            
        os.remove(temp_file.name)
        return video_b64


@app.function(image=image)
@modal.web_endpoint(method="POST")
async def generate_video_endpoint(request: Request):
    """
    Expects JSON:
    {
        "init_image_b64": "<base64_string>",
        "fps": 7,
        "motion_bucket_id": 127
    }
    """
    check_auth(request)
    body = await request.json()
    
    if "init_image_b64" not in body:
        raise HTTPException(status_code=400, detail="Missing init_image_b64")

    try:
        generator = VideoGenerator()
        video_b64 = generator.generate.remote(
            body["init_image_b64"],
            body.get("fps", 7),
            body.get("motion_bucket_id", 127)
        )
        return JSONResponse({"video_b64": video_b64})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
