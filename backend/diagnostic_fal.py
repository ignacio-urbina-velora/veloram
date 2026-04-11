
import httpx
import asyncio
import os

FAL_KEY = "007994d3-8bf4-4968-871d-3f4c1cc81e4a:3e85731d856b698eb004da49d22e0e7d"

async def test_fal():
    print(f"Testing Fal.ai with key: {FAL_KEY[:10]}...")
    url = "https://fal.run/fal-ai/flux/schnell"
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": "a cinematic shot of an airplane flying above the clouds, ultra realistic, 8k",
        "image_size": {"width": 1024, "height": 576}
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS: Fal.ai is working.")
                print(f"Result: {response.json().get('images', [{}])[0].get('url')}")
            else:
                print(f"FAILED: {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_fal())
