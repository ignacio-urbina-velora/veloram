import asyncio
from app.database import async_session
from app.models.user import User
from app.models.affiliate import Affiliate
import bcrypt
from sqlalchemy import select

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

async def seed_user(session, email, username, password, is_admin=True):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        print(f"User {email} already exists. Updating password and admin status.")
        user.hashed_password = hash_password(password)
        user.is_admin = is_admin
        await session.commit()
    else:
        print(f"Creating user {email}...")
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            credits=2500.0,
            is_admin=is_admin,
            is_active=True
        )
        session.add(user)
        await session.flush()
        
        # Create affiliate
        affiliate = Affiliate(
            user_id=user.id,
            code=username.replace(".", "_"),
            is_active=True
        )
        session.add(affiliate)
        await session.commit()
    return user

async def seed_admin():
    try:
        async with async_session() as session:
            # User 1: General admin
            await seed_user(session, "admin@ai-video.com", "admin", "ErosFrame2026!", is_admin=True)
            
            # User 2: User's specific account
            await seed_user(session, "ignaciourbina.96@gmail.com", "ignacio_urbina_admin", "campeon18", is_admin=True)
            
            print("Seeding completed successfully.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        # Don't re-raise, we want the server to try and start anyway

if __name__ == "__main__":
    asyncio.run(seed_admin())
