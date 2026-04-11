
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.generation_service import generation_service
from app.models.project import Project

DATABASE_URL = "sqlite+aiosqlite:///c:/Users/user/.gemini/antigravity/scratch/ai-video-platform/backend/ai_video_v3.db"

async def verify_gen():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Let's try project 1
        project_id = 1
        print(f"Triggering generation for project {project_id}...")
        try:
            # We use the internal method to bypass VAST/GPU costs and just test logic
            url = await generation_service._generate_mock_project(session, project_id)
            print(f"Generation successful! Mock video URL: {url}")
            await session.commit()
        except Exception as e:
            print(f"Generation failed: {e}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_gen())
