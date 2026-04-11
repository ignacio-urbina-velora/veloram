import asyncio
from app.database import init_db
from app.models.user import User
from app.models.avatar import Avatar
from app.models.project import Project, Shot
from app.models.job import Job
from app.models.affiliate import Affiliate

async def main():
    print("Initializing Database...")
    await init_db()
    print("Database Initialized successfully.")

if __name__ == "__main__":
    asyncio.run(main())
