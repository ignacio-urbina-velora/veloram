import httpx
import asyncio
import os
from dotenv import load_dotenv

async def test_vast():
    load_dotenv()
    api_key = os.getenv("VAST_API_KEY")
    base_url = "https://console.vast.ai/api/v0"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"Testing Vast.ai with key: {api_key[:5]}...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{base_url}/instances/", headers=headers, timeout=10)
            if resp.status_code == 200:
                print("✅ Vast.ai connection OK")
                print(f"Instances: {len(resp.json().get('instances', []))}")
            else:
                print(f"❌ Vast.ai error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_vast())
