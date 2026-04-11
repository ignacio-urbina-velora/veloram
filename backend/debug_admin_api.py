import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token
from app.database import async_session
from app.models.user import User
from sqlalchemy import select

async def debug_admin_apis():
    async with async_session() as db:
        # Get an admin user
        result = await db.execute(select(User).where(User.is_admin == True))
        admin = result.scalars().first()
        if not admin:
            print("No admin user found in DB!")
            return

        token = create_access_token(admin.id)
        
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = ["/admin/stats", "/admin/users", "/admin/queue", "/admin/referrals", "/admin/affiliates"]
    
    for ep in endpoints:
        print(f"\nTesting {ep}...")
        try:
            response = client.get(ep, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error Body: {response.text}")
            else:
                print("Success!")
        except Exception as e:
            print(f"Exception during {ep}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_admin_apis())
