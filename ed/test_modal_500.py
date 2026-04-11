
import httpx
import asyncio
import os

async def test_modal():
    url = "https://ignaciourbinakonecta--avatar-generate.modal.run"
    headers = {
        "Content-Type": "application/json",
        "x-modal-token-id": "wk-zgKLgaMEjSbsJJfCnoGZm4",
        "x-modal-token-secret": "ws-fKNahBbuJRC4OXpd8pnrkO"
    }
    payload = {
        "prompt": "a professional portrait of a man, high quality",
        "width": 512, # smaller for test
        "height": 512,
        "steps": 4 # standard for schnell
    }
    
    print(f"Calling Modal endpoint: {url}...")
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_modal())
