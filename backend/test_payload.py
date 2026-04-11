import asyncio
import httpx
import os

async def fetch_payload():
    url = "https://ignaciourbinakonecta--blender-avatar-service-api-generate.modal.run"
    headers = {"Authorization": f"Bearer {os.getenv('MODAL_API_KEY', 'default_secret_key')}"}
    payload = {"prompt": "test", "api_key": os.getenv('MODAL_API_KEY', 'default_secret_key')}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        data = resp.json()
        print("Keys returned:", data.keys())
        # Print a snippet of each key
        for k, v in data.items():
            if isinstance(v, str):
                print(f"{k}: {v[:50]}...")
            else:
                print(f"{k}: {v}")

asyncio.run(fetch_payload())
