import asyncio
from app.database import async_session
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    async with async_session() as session:
        # Check if user already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "ignacio@test.com"))
        if result.scalar_one_or_none():
            print("User already exists")
            return

        user = User(
            email="ignacio@test.com",
            username="ignacio",
            hashed_password=pwd_context.hash("password123"),
            credits=10.0,
            is_admin=True
        )
        session.add(user)
        await session.commit()
        print("User created: ignacio@test.com / password123")

if __name__ == "__main__":
    asyncio.run(create_test_user())
