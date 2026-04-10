import fal_client
import os
from typing import Optional, Dict, Any
from app.config import settings

class PortraitService:
    def __init__(self):
        self.api_key = settings.FAL_KEY
        if not self.api_key:
            print("⚠️ Warning: FAL_KEY not found in settings.")

    async def animate_face(self, image_url: str, video_url: str) -> Dict[str, Any]:
        """
        Uses LivePortrait via fal.ai to animate a face.
        """
        if not self.api_key:
            raise ValueError("FAL_KEY is required for animation service.")

        print(f"[PortraitService] Animating face with LivePortrait...")
        
        # Call LivePortrait
        # See: https://fal.ai/models/fal-ai/live-portrait
        handler = await fal_client.submit_async(
            "fal-ai/live-portrait",
            arguments={
                "image_url": image_url,
                "video_url": video_url
            }
        )
        
        result = await handler.get()
        return result

    async def generate_wan_video(self, prompt: str, aspect_ratio: str = "16:9") -> Dict[str, Any]:
        """
        Generates a high-quality video clip using Wan 2.1 via fal.ai.
        """
        if not self.api_key:
            raise ValueError("FAL_KEY is required for Wan video generation.")

        print(f"[PortraitService] Generating Wan video with prompt: {prompt[:50]}...")
        
        handler = await fal_client.submit_async(
            "fal-ai/wan/v2.1/t2v-480p", # Fixed identifier
            arguments={
                "prompt": prompt,
                "aspect_ratio": aspect_ratio
            }
        )
        
        result = await handler.get()
        return result

portrait_service = PortraitService()
