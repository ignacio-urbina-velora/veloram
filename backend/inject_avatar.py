import sys
import os
import asyncio
sys.path.append(os.getcwd())

from app.database import async_session
from app.models.user import User
from app.models.avatar import Avatar
from app.services.modal_service import build_avatar_prompt, generate_avatar_image
from sqlalchemy import select
import base64
from io import BytesIO
import uuid

async def create_and_save_avatar():
    try:
        async with async_session() as db:
            result = await db.execute(select(User).where(User.email == "ignaciourbina.96@gmail.com"))
            user = result.scalar_one_or_none()
            if not user:
                print("User not found.")
                return

            print("1. Generating Avatar via Modal...")
            prompt = build_avatar_prompt(
                gender="Mujer",
                age=25,
                country="Italia",
                eyes="Verdes",
                hair_color="Castaño oscuro",
                hairstyle="Pelo suelto",
                extra="hyperrealism, highly detailed",
                face_shape="oval",
                skin_tone="claro",
                eye_shape="almendrados",
                eyebrow_style="naturales",
                hair_length="largo",
                bangs="no",
                lip_volume="llenos",
                lip_color="natural",
                makeup="suave",
                expression="relajada",
                lighting="luz natural de ventana"
            )
            
            # Use strength 1.0 without base image to get a full fresh generation
            image_b64 = await generate_avatar_image(prompt)
            print("Avatar image generated successfully!")

            print("2. Saving Avatar to Storage and DB...")
            # Save bytes to storage
            raw_b64 = image_b64
            if raw_b64.startswith("data:"):
                raw_b64 = raw_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(raw_b64)

            os.makedirs("storage/avatars", exist_ok=True)
            filename = f"avatar_{user.id}_{uuid.uuid4().hex[:8]}.png"
            file_path = os.path.join("storage/avatars", filename)

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            texture_url = f"/storage/avatars/{filename}"

            avatar = Avatar(
                user_id=user.id,
                name="Avatar Creado Automáticamente",
                source_type="flux_projection",
                source_data="{}",
                reference_pack_url=texture_url,
                metadata_json={"styles": {}, "morphs": {}},
                status="ready",
            )
            db.add(avatar)
            await db.commit()
            print(f"Avatar saved to DB successfully! ID: {avatar.id}")
            
    except Exception as e:
        print(f"Error during creation: {e}")

if __name__ == "__main__":
    asyncio.run(create_and_save_avatar())
