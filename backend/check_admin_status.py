import asyncio
from app.database import async_session
from app.models.user import User
from sqlalchemy import select

async def check_admin():
    async with async_session() as db:
        email = "admin@ai-video.com"
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            print(f"User: {user.email}")
            print(f"Is Admin: {user.is_admin}")
            print(f"Credits: {user.credits}")
            # Force update just in case
            if not user.is_admin:
                print("Forcing is_admin=True")
                user.is_admin = True
                await db.commit()
        else:
            print(f"User {email} NOT FOUND!")

if __name__ == "__main__":
    asyncio.run(check_admin())
