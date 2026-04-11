import asyncio
import base64
import sys

from backend.app.services.modal_service import generate_avatar_image

async def run():
    prompt = "high quality portrait photo of a 22 year old beautiful blonde woman, cute, smiling warmly, waving her hand at the camera, highly detailed, realistic texture, cinematic lighting, 8k"
    print(f"Calling FLUX with prompt: {prompt}")
    
    try:
        b64 = await generate_avatar_image(prompt, None, None)
        with open("flux_test_result.png", "wb") as f:
            f.write(base64.b64decode(b64))
        print("Success! Saved as flux_test_result.png")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
