import asyncio
import httpx
import os

async def run():    
    MODAL_URL = "https://ignaciourbinakonecta--blender-avatar-service-api-generate.modal.run"
    headers = {"Authorization": f"Bearer {os.getenv('MODAL_API_KEY', 'default_secret_key')}"}
    payload = {"prompt": "Test face", "api_key": os.getenv('MODAL_API_KEY', 'default_secret_key')}
    
    print("Testing Modal API connectivity...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print(f"Calling Modal URL: {MODAL_URL}")
            resp = await client.post(MODAL_URL, json=payload, headers=headers)
            print(f"Status Code: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error: {resp.text}")
            else:
                data = resp.json()
                print("Success! Got image data.")
    except Exception as e:
        print(f"Exception caught: {e}")

asyncio.run(run())
