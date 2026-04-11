
import asyncio
import base64
import os
import sys
from pathlib import Path

# Add backend to path to import services
sys.path.append(os.getcwd())

from app.services.modal_service import generate_avatar_image, save_avatar_image, build_avatar_prompt

async def generate_test_avatar():
    # Simulate a user request through the prompt builder
    prompt = build_avatar_prompt(
        gender="Mujer",
        age=25,
        country="Egipto",
        build="Delgada",
        eyes="Ambar",
        hair_color="Oscuro",
        hairstyle="Wavy",
        clothing="Casual / Streetwear",
        breast_size="Mediano",
        extra="urban background blurred"
    )
    
    print(f"Generating professional test avatar with prompt: {prompt[:100]}...")
    try:
        # 1. Generate via Modal
        b64_image = await generate_avatar_image(prompt)
        print(f"Generation successful! Image size: {len(b64_image)} chars")
        
        # 2. Save to storage
        filename = "test_avatar_professional.png"
        url = await save_avatar_image(b64_image, filename)
        
        print(f"Image saved successfully to: {url}")
        print(f"Full path: {os.path.abspath(f'storage/avatars/{filename}')}")
        
    except Exception as e:
        print(f"Error during test generation: {str(e)}")

if __name__ == "__main__":
    # Ensure we are in the backend directory
    if not os.path.exists("app"):
        print("Error: Must run from the 'backend' directory.")
        sys.exit(1)
    
    asyncio.run(generate_test_avatar())
