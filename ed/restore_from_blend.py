import httpx
import base64
import os
import json

# The URL for the new Modal endpoint we just added
MODAL_EXPORT_URL = "https://ignaciourbinakonecta--blender-avatar-service-api-export-blend.modal.run"
BLEND_FILE_PATH = "frontend/public/model/amala.blend"
OUTPUT_GLB_PATH = "frontend/public/model/amala.glb"

async def restore():
    if not os.path.exists(BLEND_FILE_PATH):
        print(f"Error: {BLEND_FILE_PATH} not found.")
        return

    print(f"Reading {BLEND_FILE_PATH}...")
    with open(BLEND_FILE_PATH, "rb") as f:
        blend_b64 = base64.b64encode(f.read()).decode("utf-8")

    print("Sending .blend to Modal for GLB export (this may take a minute)...")
    
    payload = {
        "blend_file_b64": blend_b64
    }
    
    async with httpx.AsyncClient(timeout=900.0) as client:
        try:
            resp = await client.post(
                MODAL_EXPORT_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if resp.status_code != 200:
                print(f"Server Error ({resp.status_code}): {resp.text}")
                return
                
            data = resp.json()
            glb_b64 = data.get("glb_base64")
            
            if glb_b64:
                print(f"Received GLB from Modal. Saving to {OUTPUT_GLB_PATH}...")
                glb_bytes = base64.b64decode(glb_b64)
                with open(OUTPUT_GLB_PATH, "wb") as f:
                    f.write(glb_bytes)
                print(f"Success! New file size: {len(glb_bytes)} bytes")
            else:
                print("Error: No glb_base64 in response.")
                if "logs" in data:
                    print("--- SERVER LOGS ---")
                    print(data["logs"])
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(restore())
