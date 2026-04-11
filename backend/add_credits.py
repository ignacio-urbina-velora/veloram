import sys
import os
import asyncio
sys.path.append(os.getcwd())

from app.database import async_session
from app.models.user import User
from sqlalchemy import select

async def main():
    email = "ignaciourbina.96@gmail.com"
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.credits += 10000.0  # Giving you 10,000 credits!
            await session.commit()
            print(f"✅ Se han agregado exitosamente 10,000 créditos a {email}. Saldo actual: {user.credits}")
        else:
            print(f"❌ No se encontró ningún usuario con el correo {email}")

if __name__ == "__main__":
    asyncio.run(main())
