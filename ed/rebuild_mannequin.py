import httpx
import base64
import os
import json

MODAL_BLENDER_URL = "https://ignaciourbinakonecta--blender-avatar-service-api-generate.modal.run"
OUTPUT_PATH = "frontend/public/model/amala.glb"

async def rebuild():
    print("Requesting fresh mannequin from Blender service...")
    params = {
        "gender": "Mujer",
        "height": 170,
        "weight": 60,
        "build": "Atlética",
        "age": 26
    }
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        try:
            resp = await client.post(
                MODAL_BLENDER_URL,
                json={"params": params},
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            data = resp.json()
            glb_b64 = data.get("glb_base64")
            
            if glb_b64:
                glb_bytes = base64.b64decode(glb_b64)
                os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
                with open(OUTPUT_PATH, "wb") as f:
                    f.write(glb_bytes)
                print(f"Successfully saved new mannequin to {OUTPUT_PATH}")
                print(f"Size: {len(glb_bytes)} bytes")
                if "logs" in data:
                    print("--- SERVER LOGS ---")
                    print(data["logs"])
            else:
                print("Error: No glb_base64 in response")
                if "logs" in data:
                    print("Logs:", data["logs"])
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(rebuild())
