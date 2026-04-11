
import asyncio
import os
import sys

# Ensure backend root is in sys.path
sys.path.append(os.getcwd())

from app.database import async_session
from app.services.generation_service import generation_service

async def main():
    print("Testing keyframe generation for Project 6...")
    try:
        async with async_session() as session:
            await generation_service.generate_keyframes(session, 6)
            print("Successfully triggered keyframes for 6")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
