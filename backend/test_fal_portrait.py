import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())
load_dotenv()

from app.services.portrait_service import portrait_service

async def test_fal_features():
    print("--- 🧪 Testing Fal.ai Features (Pro) ---")
    
    if not os.getenv("FAL_KEY"):
        print("❌ ERROR: Debes configurar FAL_KEY en tu .env")
        return

    # 1. Test LivePortrait (Sample URLS)
    print("\n--- Testing LivePortrait ---")
    source_image = "https://raw.githubusercontent.com/KwaiVGI/LivePortrait/main/assets/examples/source/s9.jpg"
    driving_video = "https://raw.githubusercontent.com/KwaiVGI/LivePortrait/main/assets/examples/driving/d0.mp4"
    
    try:
        result = await portrait_service.animate_face(source_image, driving_video)
        print(f"✅ LivePortrait Success! Result URL: {result.get('video', {}).get('url')}")
    except Exception as e:
        print(f"❌ LivePortrait Error: {e}")

    # 2. Test Wan Video (Low Res for speed)
    print("\n--- Testing Wan Video (T2V) ---")
    prompt = "A high-tech cinematic studio with glowing neon lights and high-end video cameras."
    try:
        result = await portrait_service.generate_wan_video(prompt)
        print(f"✅ Wan Video Success! Result URL: {result.get('video', {}).get('url')}")
    except Exception as e:
        print(f"❌ Wan Video Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fal_features())
