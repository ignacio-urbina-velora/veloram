import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token
from app.database import async_session
from app.models.user import User
from sqlalchemy import select

async def debug_queue_api():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.is_admin == True))
        admin = result.scalars().first()
        if not admin:
            print("No admin user found!")
            return
        token = create_access_token(admin.id)
        
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Testing /admin/queue...")
    response = client.get("/admin/queue", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")

if __name__ == "__main__":
    asyncio.run(debug_queue_api())
