import httpx
import base64
import json
import asyncio

async def test_projection():
    print("Testing /project-face endpoint...")
    
    # create a dummy 1x1 png image
    img_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
    
    url = "https://ignaciourbinakonecta--blender-avatar-service-api-project-face.modal.run"
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                url,
                json={"face_image_b64": img_b64},
                timeout=600.0
            )
            print(f"Status Code: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error Response: {resp.text}")
            else:
                print("Success!")
        except Exception as e:
            print(f"Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_projection())
