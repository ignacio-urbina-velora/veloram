import sys
import os
import asyncio
sys.path.append(os.getcwd())

from app.database import async_session
from app.models.user import User
from app.api.avatars import generate_avatar, AvatarGenerateRequest
from app.services.modal_service import build_avatar_prompt, generate_avatar_image
from sqlalchemy import select
from fastapi import HTTPException
import base64
from io import BytesIO
from PIL import Image

def create_dummy():
    img = Image.new('RGB', (10, 10), color=(150, 150, 150))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

async def run_internal_test():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "ignaciourbina.96@gmail.com"))
        user = result.scalar_one_or_none()
        if not user:
            print("User not found.")
            return

        print(f"User found, credits: {user.credits}")
        
        req = AvatarGenerateRequest(
            base_image_b64=create_dummy(),
            gender="Hombre",
            age=30,
            hair_color="castaño",
            hairstyle="corto",
            clothing="casual",
            country="Chile",
            eyes="oscuros",
            extra_prompt="prueba interna"
        )
        
        try:
            print("Starting avatar generation internally...")
            res = await generate_avatar(req, current_user=user, db=db)
            print("SUCCESS! Generated image of length:", len(res.image_b64))
        except HTTPException as e:
            print(f"HTTPException: {e.status_code} - {e.detail}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(run_internal_test())
