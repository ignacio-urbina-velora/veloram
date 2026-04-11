import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())
load_dotenv()

from app.services.director_service import director_service
from app.database import async_session, engine, Base
from app.models.project import Project
from sqlalchemy import select

async def test_persistence():
    print("--- 🧪 Testing Director AI Persistence ---")
    
    # 1. Create a dummy project in DB
    async with async_session() as db:
        new_project = Project(
            user_id=1, # Assuming user 1 exists
            title="Test Persistence Project",
            tier=1
        )
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        project_id = str(new_project.id)
        print(f"Created project {project_id}")

        # 2. Run initial plan
        idea = "A futuristic city in the clouds with flying drones and neon lights"
        print(f"Running initial plan for: {idea}")
        result = await director_service.plan_video(idea, 15, "cyberpunk", project_id, db)
        
        # 3. Verify Bible was persisted
        await db.refresh(new_project)
        bible = new_project.director_bible
        if bible and bible.get("style_guide"):
            print("✅ Success: Director's Bible persisted in JSON field.")
            print(f"Style Guide Preview: {bible['style_guide'][:100]}...")
        else:
            print("❌ Failure: Bible not found in DB.")

        # 4. Test Refinement (State Recovery)
        print("\n--- Testing Refinement ---")
        feedback = "Make the scene more cinematic and add a close up of a drone."
        shots = result.get("shots", [])
        refine_result = await director_service.refine_sequence(shots, feedback, project_id, db)
        
        if refine_result.get("shots"):
            print(f"✅ Success: Refined sequence generated {len(refine_result['shots'])} shots.")
        else:
            print("❌ Failure: Refinement returned no shots.")

if __name__ == "__main__":
    asyncio.run(test_persistence())
