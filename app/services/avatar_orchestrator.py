import logging
import base64
import httpx
import uuid
import os
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.modal_service import generate_avatar_image, build_avatar_prompt
from app.services.skin_service import extract_skin_color_from_b64
from app.services.storage_service import storage_service
from app.models.avatar import Avatar
from app.config import settings

logger = logging.getLogger(__name__)

class AvatarOrchestrator:
    """
    Orchestrates the creation of a professional avatar:
    1. Generates a high-quality Flux face.
    2. Extracts the skin tone.
    3. Generates a matching 3D body in Blender.
    """

    MODAL_BLENDER_URL = "https://ignaciourbinakonecta--blender-avatar-service-api-generate.modal.run"

    async def create_professional_avatar(
        self,
        db: AsyncSession,
        user_id: int,
        params: Dict[str, Any]
    ) -> tuple[Avatar, str, Optional[str]]:
        # 1. Build Prompt and Generate Face with Flux
        hifi_prompt = build_avatar_prompt(**params)
        logger.info(f"Generating Flux face for user {user_id}...")
        face_b64 = await generate_avatar_image(hifi_prompt)
        
        # 2. Extract Skin Tone
        logger.info("Extracting skin tone...")
        skin_color_hex = extract_skin_color_from_b64(face_b64)
        logger.info(f"Extracted skin tone: {skin_color_hex}")

        # 3. Generate 3D Body with Blender
        logger.info("Generating 3D body with Blender...")
        blender_params = {
            "gender": params.get("gender", "Mujer"),
            "skin_color": skin_color_hex,
            "height": params.get("height", 170),
            "weight": params.get("weight", 60),
            "build": params.get("build", "Atlética"),
            "age": params.get("age", 25)
        }

        glb_b64 = None
        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                resp = await client.post(
                    self.MODAL_BLENDER_URL,
                    json={"params": blender_params},
                    headers={"Content-Type": "application/json"}
                )
                resp.raise_for_status()
                data = resp.json()
                glb_b64 = data.get("glb_base64")
        except Exception as e:
            logger.error(f"Blender generation failed: {e}")
            # We continue even if Blender fails, the face is the most important part

        # 4. Save files to storage
        uid = str(uuid.uuid4())[:8]
        
        # Save Face Image
        face_bytes = base64.b64decode(face_b64)
        face_key = f"avatars/face_{user_id}_{uid}.png"
        face_url = await storage_service.upload_image(face_bytes, face_key)
        
        # Save GLB if available
        glb_url = None
        if glb_b64:
            glb_bytes = base64.b64decode(glb_b64)
            glb_key = f"models/body_{user_id}_{uid}.glb"
            glb_url = await storage_service.upload_image(glb_bytes, glb_key)

        # 5. Create Database Record
        avatar = Avatar(
            user_id=user_id,
            name=params.get("name", "Nuevo Avatar Profesional"),
            status="ready",
            source_type="professional_pipeline",
            source_data=hifi_prompt,
            reference_pack_url=face_url,
            metadata_json={
                "skin_tone": skin_color_hex,
                "face_prompt": hifi_prompt,
                "params": params,
                "glb_url": glb_url,
                "has_3d_model": glb_url is not None
            }
        )
        
        db.add(avatar)
        await db.commit()
        await db.refresh(avatar)
        
        return avatar, str(face_b64), (str(glb_b64) if glb_b64 else None)

avatar_orchestrator = AvatarOrchestrator()

avatar_orchestrator = AvatarOrchestrator()
