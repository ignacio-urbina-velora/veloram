
import asyncio
import base64
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import engine, Base
from app.models.project import Project, Shot
from app.models.user import User
from app.services.generation_service import generation_service
from app.services.director_service import director_service

async def test_flow():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # 1. Ensure a test user exists
        result = await db.execute(select(User).where(User.email == "admin@ai-video.com"))
        user = result.scalar_one_or_none()
        if not user:
            print("Admin user not found. Run seed first.")
            return

        # 2. Create a test project
        project = Project(
            user_id=user.id,
            title="Test Image-First Flow",
            tier=2
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        print(f"Project created: {project.id}")

        # 3. Plan with Director
        print("Planning with Director...")
        plan = await director_service.plan_video(
            idea="A detective walking in the rain, noir style", 
            target_duration_sec=10, 
            style="cinematic", 
            project_id=str(project.id),
            db=db
        )
        print(f"Generated {len(plan['shots'])} shots.")

        # 4. Create shots in DB (Simulating projects.py logic)
        shots = []
        for i, s_data in enumerate(plan['shots']):
            shot = Shot(
                project_id=project.id,
                order=i,
                prompt=s_data['prompt'],
                camera_movement=s_data.get('camera_movement', 'static'),
                duration_target_sec=s_data.get('duration_target_sec', 5.0)
            )
            db.add(shot)
            shots.append(shot)
        await db.commit()

        # 5. Generate Keyframes
        print("Generating Keyframes (Stage 1)...")
        await generation_service.generate_keyframes(db, project.id)
        
        await db.refresh(project)
        result = await db.execute(select(Shot).where(Shot.project_id == project.id))
        all_shots = result.scalars().all()
        
        for s in all_shots:
            print(f"Shot {s.order} preview_url: {s.preview_url}")
            if not s.preview_url:
                print(f"FAILED: Shot {s.order} has no preview_url")

        # 6. Generate Video (Stage 2)
        # Note: We use the mock/modal toggle based on settings. 
        # For this test, we just verify it calls the right logic.
        print("Starting Video Generation (Stage 2)...")
        # We simulate the start_generation background call
        # project.is_mock = 1 # Set to 1 if you want to test the mock flow instead
        await generation_service._generate_modal_project(db, project.id)
        
        await db.refresh(project)
        print(f"Final Status: {project.status}")
        print(f"Final Video: {project.final_video_url}")

if __name__ == "__main__":
    asyncio.run(test_flow())
