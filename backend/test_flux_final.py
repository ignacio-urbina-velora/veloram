import sys
import os
import asyncio
sys.path.append(os.getcwd())

from app.services.modal_service import build_avatar_prompt, generate_avatar_image

async def test_flux_final():
    params = {
        "gender": "Mujer",
        "age": 24,
        "country": "España",
        "eyes": "verdes",
        "hair_color": "rubio",
        "hairstyle": "pelo rizado natural",
        "face_shape": "oval",
        "skin_tone": "claro",
        "makeup": "muy poco",
        "expression": "relajada",
        "lighting": "luz natural de interior",
        "extra": "textura de cámara de teléfono, pecas tenues"
    }
    
    prompt = build_avatar_prompt(**params)
    print("--- GENERATED PROMPT ---")
    print(prompt)
    print("------------------------")
    
    print("\nCalling Modal FLUX service directly...")
    try:
        b64 = await generate_avatar_image(prompt)
        print(f"Success! Received base64 image (length: {len(b64)})")
        
        import base64
        with open("flux_test_final.png", "wb") as f:
            f.write(base64.b64decode(b64))
        print("Image saved to flux_test_final.png")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_flux_final())
