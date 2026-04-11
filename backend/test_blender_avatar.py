
import httpx
import asyncio
import base64
import json

async def test_blender_avatar():
    url = "https://ignaciourbinakonecta--blender-avatar-service-api-generate.modal.run"
    payload = {
        "gender": "Mujer",
        "age": 26,
        "height": 170,
        "weight": 60,
        "build": "Atlética",
        "country": "España"
    }
    
    print(f"Calling Blender Avatar Service: {url}...")
    async with httpx.AsyncClient(timeout=600.0) as client:
        try:
            response = await client.post(url, json={"params": payload}, headers={"Content-Type": "application/json"})
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                glb_b64 = data.get("glb_base64", "")
                if glb_b64:
                    print(f"Success! Received GLB (base64 length: {len(glb_b64)})")
                    # Save a few bytes for verification
                    with open("test_output.glb", "wb") as f:
                        f.write(base64.b64decode(glb_b64))
                    print("Model saved to test_output.glb")
                    print("\n--- RECEIVED LOGS ---")
                    print(data.get("logs", "No logs found"))
                else:
                    print("Error: No glb_base64 in response")
                    print(f"Response data: {data}")
            else:
                print(f"Error Response: {response.text}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_blender_avatar())
