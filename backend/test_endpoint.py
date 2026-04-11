import asyncio
from app.api.avatars import generate_portrait, PortraitGenerateRequest
from app.database import async_session_maker
from app.models.user import User
from sqlalchemy import select

class MockUser:
    id = "1"  # Not needed if we pass a real user

async def run():
    async with async_session_maker() as db:
        res = await db.execute(select(User).limit(1))
        real_user = res.scalar_one_or_none()
        
        if not real_user:
            print("No user found in DB to test with")
            return
            
        print(f"Testing with user {real_user.email} (credits: {real_user.credits})")
        req = PortraitGenerateRequest(prompt="Test portrait")
        
        try:
            result = await generate_portrait(req, current_user=real_user, db=db)
            print("Success!")
            print(result.keys())
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
