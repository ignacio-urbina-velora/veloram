import asyncio
from app.database import async_session
from app.models.user import User
from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    async with async_session() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == "ignaciourbina.96@gmail.com"))
        if result.scalar_one_or_none():
            print("User already exists")
            return

        user = User(
            email="ignaciourbina.96@gmail.com",
            username="ignacio_dev",
            hashed_password=pwd_context.hash("password123"),
            credits=100.0,
            is_admin=True
        )
        session.add(user)
        await session.commit()
        print("User created: ignaciourbina.96@gmail.com / password123")

if __name__ == "__main__":
    asyncio.run(create_test_user())
