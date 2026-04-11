import httpx
import asyncio
import base64
import os
from dotenv import load_dotenv

load_dotenv()

async def test_reproduction():
    url = os.getenv("MODAL_ENDPOINT_URL")
    token_id = os.getenv("MODAL_TOKEN_ID")
    token_secret = os.getenv("MODAL_TOKEN_SECRET")
    
    # Prompt estético final    # USAMOS LA TÉCNICA DE PROMPT FUSIONADO (Safe Mode)
    prompt = "Professional masterpiece portrait, head and shoulders shot, eye-level camera, natural head position, slight head tilt, natural shoulder-to-neck ratio, proportionate anatomy, octabox lighting. Person characteristics: género mujer, 25 años de edad, mide 175 cm y pesa 55 kg, etnia latino. Photorealistic, 8k, RAW photo, sharp focus on eyes, detailed iris, voluminous hair, smooth flawless skin, elegant posture, no elongated features, no artifacts, professional quality. Negative prompt: elongated face, long face, stretched face, distorted proportions, deformed head, big chin, small forehead, bad anatomy, low angle distortion, fisheye effect, upshot perspective, exaggerated face length, asymmetrical face, mutant, ugly, deformed, blurry, low quality. Avoid any distorted proportions, elongated neck, or facial landmarks."
    
    payload = {
        "prompt": prompt,
        "width": 768,
        "height": 1024,
        "steps": 4
    }
    
    headers = {
        "x-modal-token-id": token_id,
        "x-modal-token-secret": token_secret,
        "Content-Type": "application/json"
    }
    
    print(f"Calling Modal with reproduction prompt...")
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                img_data = base64.b64decode(data["image_b64"])
                with open("reproduction_output.png", "wb") as f:
                    f.write(img_data)
                print("Image saved to reproduction_output.png")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_reproduction())
