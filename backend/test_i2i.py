import httpx
import asyncio
import json
import base64
import io
from PIL import Image

async def test_modal():
    url = "https://ignaciourbinakonecta--avatar-generate.modal.run"
    headers = {
        "Content-Type": "application/json",
        "x-modal-token-id": "wk-zgKLgaMEjSbsJJfCnoGZm4",
        "x-modal-token-secret": "ws-fKNahBbuJRC4OXpd8pnrkO"
    }

    # Generate a solid color image to test img2img
    img = Image.new("RGB", (512, 512), "red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64_img = base64.b64encode(buf.read()).decode('utf-8')
    
    payload = {
        "prompt": "a beautiful landscape, digital art, high quality",
        "width": 512,
        "height": 512,
        "steps": 4,
        "init_image_b64": b64_img,
        "strength": 0.8
    }
    
    print(f"Calling Modal endpoint with img2img: {url}...")
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("Success!")
            else:
                print(f"Error Response: {response.text}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_modal())
