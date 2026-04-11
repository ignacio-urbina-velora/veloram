import asyncio
import httpx
import os
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FAL_KEY = os.getenv("FAL_KEY")

async def test_fal():
    print(f"Testing Fal.ai with key: {FAL_KEY[:10]}...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        fal_url = "https://fal.run/fal-ai/flux/schnell"
        payload = {
            "prompt": "A professional high-fidelity 8k portrait of a woman, cinematic lighting.",
            "image_size": {"width": 1024, "height": 1024},
            "num_inference_steps": 4,
            "enable_safety_checker": False
        }
        
        response = await client.post(
            fal_url,
            json=payload,
            headers={"Authorization": f"Key {FAL_KEY}"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            image_url = data.get("images", [{}])[0].get("url")
            print(f"Success! Image URL: {image_url}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_fal())
