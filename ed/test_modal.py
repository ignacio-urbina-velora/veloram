
import httpx
import asyncio

async def test_modal():
    url = "https://ignaciourbinakonecta--avatar-generate.modal.run"
    token_id = "wk-zgKLgaMEjSbsJJfCnoGZm4"
    token_secret = "ws-fKNahBbuJRC4OXpd8pnrkO"
    
    payload = {
        "prompt": "Portrait photo of a 25 year old woman, highly detailed",
        "width": 768,
        "height": 1024,
        "steps": 28,
    }
    
    auth = (token_id, token_secret)
    
    print(f"Testing Modal endpoint: {url}")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload, auth=auth)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if "image_b64" in data:
                    print("Success! Received image_b64")
                else:
                    print(f"Unexpected response format: {data}")
            else:
                print(f"Error response: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_modal())
