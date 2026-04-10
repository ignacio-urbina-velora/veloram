"""Avatar generation API router."""

import uuid
import os
import base64
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

import logging
from app.api.deps import get_current_user
from app.database import get_db
from app.services.modal_service import (
    build_avatar_prompt, 
    generate_avatar_image, 
    save_avatar_image, 
    generate_consistent_avatar,
    generate_hyperreal_texture
)
from app.services.wan_service import (
    build_wan22_prompt,
    generate_wan22_image,
    generate_avatar_wan22,
    NEGATIVE_PROMPT as WAN_NEGATIVE_PROMPT,
)
from app.models.avatar import Avatar

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avatars", tags=["Avatars"])

GENERATION_COST = 10  # créditos por generación


class AvatarListItem(BaseModel):
    id: int
    name: str
    texture_url: str
    status: str
    created_at: str
    morphs: Optional[Dict[str, Any]] = None
    styles: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[AvatarListItem])
async def list_avatars(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all saved avatars for the current user."""
    from sqlalchemy import select
    result = await db.execute(
        select(Avatar)
        .where(Avatar.user_id == current_user.id)
        .order_by(Avatar.created_at.desc())
    )
    avatars = result.scalars().all()
    return [
        AvatarListItem(
            id=a.id,
            name=a.name,
            texture_url=a.reference_pack_url or "",
            status=a.status,
            created_at=str(a.created_at),
            morphs=(a.metadata_json or {}).get("morphs"),
            styles=(a.metadata_json or {}).get("styles"),
        )
        for a in avatars
    ]


@router.delete("/{avatar_id}", status_code=204)
async def delete_avatar(
    avatar_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved avatar from DB and disk."""
    from sqlalchemy import select
    result = await db.execute(
        select(Avatar).where(Avatar.id == avatar_id, Avatar.user_id == current_user.id)
    )
    avatar = result.scalar_one_or_none()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar no encontrado")

    # Remove file from disk
    if avatar.reference_pack_url:
        file_path = avatar.reference_pack_url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)

    await db.delete(avatar)
    await db.commit()


class PortraitGenerateRequest(BaseModel):
    gender: str = "Mujer"
    age: int = 25
    eyes: str = "Café"
    hair_color: str = "Castaño medio"
    hairstyle: str = "Mediano"
    country: str = "Chilena"
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = ""
    
    # New detailed morphs
    face_shape: Optional[str] = "Ovalada"
    skin_tone: Optional[str] = "Medio"
    eye_shape: Optional[str] = "Almendrados"
    eyebrow_style: Optional[str] = "Naturales"
    hair_length: Optional[str] = "Mediano"
    bangs: Optional[str] = "Sin flequillo"
    lip_volume: Optional[str] = "Medio"
    lip_color: Optional[str] = "Natural"
    makeup: Optional[str] = "Natural"
    expression: Optional[str] = "Neutra"
    lighting: Optional[str] = "De estudio"
    tier: str = "professional"

class MultiViewReference(BaseModel):
    view: str
    base64: str

class TextureRequest(BaseModel):
    references: list[MultiViewReference]
    prompt_enhancement: Optional[str] = ""
    tier: str = "professional"

class ExtractSkinToneRequest(BaseModel):
    image_b64: str

@router.post("/extract-skin-tone")
async def extract_skin_tone(req: ExtractSkinToneRequest):
    """Extract dominant skin color from a base64 image."""
    from app.services.skin_service import extract_skin_color_from_b64
    color_hex = extract_skin_color_from_b64(req.image_b64)
    return {"color": color_hex}


@router.post("/generate-portrait")
async def generate_portrait(
    req: PortraitGenerateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a 2D portrait using Wan 2.2 (primary) or Modal FLUX (fallback)."""
    from app.models.user import User
    from sqlalchemy import select

    # Check credits
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    current_credits = float(user.credits or 0)
    cost = 10.0
    if current_credits < cost:
        raise HTTPException(
            status_code=402,
            detail=f"Créditos insuficientes. Necesitas {cost}, tienes {int(current_credits)}.",
        )

    # ── Motor v3.0: Wan 2.2 (Primary) ──────────────────────────────
    # Build prompt optimized for Wan 2.2 hyperrealism
    if req.prompt and len(req.prompt) > 20:
        # User-provided full prompt
        wan_prompt = req.prompt
    else:
        # Build from parameters using Wan 2.2 prompt builder
        wan_prompt = build_wan22_prompt(
            gender=req.gender,
            age=req.age,
            ethnicity=req.country,
            hair_color=req.hair_color,
            hairstyle=req.hairstyle,
            expression=req.expression,
            skin_tone=req.skin_tone,
            eye_color=req.eyes,
            eye_shape=req.eye_shape,
            face_shape=req.face_shape,
            makeup=req.makeup,
            lighting=req.lighting,
            extra=req.prompt or "",
        )

    try:
        # Try Wan 2.2 first (fast, cheap, hyperrealistic)
        logger.info(f"[Portrait] Trying Wan 2.2 engine...")
        image_b64 = await generate_wan22_image(wan_prompt, tier=req.tier)

        # Fallback to Modal FLUX if Wan 2.2 fails
        if not image_b64:
            logger.warning("[Portrait] Wan 2.2 failed, falling back to Modal FLUX...")
            hifi_prompt = build_avatar_prompt(
                gender=req.gender, age=req.age, country=req.country,
                eyes=req.eyes, hair_color=req.hair_color, hairstyle=req.hairstyle,
                extra=req.prompt or "", face_shape=req.face_shape,
                skin_tone=req.skin_tone, eye_shape=req.eye_shape,
                eyebrow_style=req.eyebrow_style, hair_length=req.hair_length,
                bangs=req.bangs, lip_volume=req.lip_volume,
                lip_color=req.lip_color, makeup=req.makeup,
                expression=req.expression, lighting=req.lighting,
            )
            image_b64 = await generate_avatar_image(hifi_prompt, tier=req.tier)

        if not image_b64:
            raise HTTPException(status_code=500, detail="All generation engines failed")

        # Deduct credits
        user.credits = current_credits - cost
        await db.commit()

        return {"image_b64": image_b64, "prompt_used": wan_prompt, "credits_deducted": cost}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        logger.error(f"[Portrait] Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AvatarGenerateRequest(BaseModel):
    gender: str = "Mujer"
    age: int = 26
    height: int = 170
    weight: int = 60
    build: str = "Atlética"
    country: str = "Ninguno específico"
    eyes: str = "Ambar"
    hairstyle: str = "Blunt bob"
    hair_color: str = "Negro"
    breast_size: Optional[str] = None
    clothing: str = "Casual / Streetwear"
    extra_prompt: str = ""
    base_image_b64: Optional[str] = None
    strength: Optional[float] = 0.85
    
    # New facial parameters
    face_shape: str = "oval"
    skin_tone: str = "natural"
    eye_shape: str = "almond"
    eyebrow_style: str = "natural"
    hair_length: str = "medium"
    bangs: str = "no"
    lip_volume: str = "full"
    lip_color: str = "natural"
    makeup: str = "minimal"
    expression: str = "neutral"
    lighting: str = "soft studio"


class AvatarGenerateResponse(BaseModel):
    image_b64: str
    prompt_used: str
    credits_deducted: int


@router.post("/generate", response_model=AvatarGenerateResponse)
async def generate_avatar(
    req: AvatarGenerateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an avatar image using Modal FLUX and deduct credits."""

    # Check credits (users have credits stored as float)
    from app.models.user import User
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    current_credits = float(user.credits or 0)
    if current_credits < GENERATION_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Créditos insuficientes. Necesitas {GENERATION_COST}, tienes {int(current_credits)}.",
        )

    prompt = build_avatar_prompt(
        gender=req.gender,
        age=req.age,
        country=req.country,
        eyes=req.eyes,
        hair_color=req.hair_color,
        hairstyle=req.hairstyle,
        extra=req.extra_prompt,
        face_shape=req.face_shape,
        skin_tone=req.skin_tone,
        eye_shape=req.eye_shape,
        eyebrow_style=req.eyebrow_style,
        hair_length=req.hair_length,
        bangs=req.bangs,
        lip_volume=req.lip_volume,
        lip_color=req.lip_color,
        makeup=req.makeup,
        expression=req.expression,
        lighting=req.lighting,
    )

    # Call Modal
    try:
        image_b64 = await generate_avatar_image(prompt, req.base_image_b64, req.strength)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error en generación: {str(e)}")

    # Deduct credits
    user.credits = current_credits - GENERATION_COST
    await db.commit()

    return AvatarGenerateResponse(
        image_b64=image_b64,
        prompt_used=prompt,
        credits_deducted=GENERATION_COST,
    )

@router.post("/professional/generate")
async def generate_professional_avatar(
    req: Dict[str, Any],
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a professional avatar:
    1. Flux Face
    2. Skin Tone Extraction
    3. Blender Body Sync
    """
    from app.services.avatar_orchestrator import avatar_orchestrator
    from app.models.user import User
    from sqlalchemy import select

    # Check credits (Professional generation might cost more, e.g., 20)
    PROFESSIONAL_COST = 20.0
    
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    current_credits = float(user.credits or 0)
    if current_credits < PROFESSIONAL_COST:
        raise HTTPException(
            status_code=402,
            detail=f"Créditos insuficientes. Necesitas {PROFESSIONAL_COST}, tienes {int(current_credits)}.",
        )

    try:
        avatar, face_b64, glb_b64 = await avatar_orchestrator.create_professional_avatar(
            db=db,
            user_id=current_user.id,
            params=req
        )

        # Deduct credits
        user.credits = current_credits - PROFESSIONAL_COST
        await db.commit()

        return {
            "avatar_id": avatar.id,
            "face_image_b64": face_b64,
            "glb_model_b64": glb_b64,
            "credits_deducted": PROFESSIONAL_COST,
            "status": "ready"
        }
    except Exception as e:
        import traceback
        logger.error(f"Error in professional avatar pipeline: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en el pipeline profesional: {str(e)}")

@router.post("/generate-texture-8k")
async def generate_texture_8k(
    req: TextureRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint de alta fidelidad basado en 'mejora 2d'.
    Procesa múltiples vistas para generar una imagen hiperrealista editorial.
    """
    COST = 25.0
    from app.models.user import User
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user or user.credits < COST:
        raise HTTPException(status_code=402, detail="Créditos insuficientes para generación hiperrealista")

    # Construir prompt macro avanzado
    hifi_prompt = build_avatar_prompt(
        gender="Mujer", # Por defecto o extraer de morphs
        age=28,
        extra=req.prompt_enhancement or "professional editorial photography, hyper-detailed skin"
    )

    try:
        # Convertir referencias a formato lista dict para el servicio
        refs = [{"view": r.view, "base64": r.base64} for r in req.references]
        
        image_b64 = await generate_hyperreal_texture(
            references=refs,
            prompt=hifi_prompt,
            tier=req.tier
        )

        user.credits -= COST
        await db.commit()

        return {
            "success": True,
            "image_b64": image_b64,
            "message": "Textura hiperrealista generada correctamente",
            "credits_remaining": user.credits
        }
    except Exception as e:
        logger.error(f"Error en generate_texture_8k: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ConsistentVariationRequest(BaseModel):
    avatar_id: int
    prompt: str
    face_weight: float = 0.75
    seed: Optional[int] = None

@router.post("/generate-consistent", response_model=Dict[str, Any])
async def generate_consistent_variation(
    req: ConsistentVariationRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new image of an existing avatar in a new context (prompt) 
    maintaining identity via IP-Adapter-FaceID.
    """
    from app.models.avatar import Avatar
    from app.models.user import User
    from sqlalchemy import select
    from pathlib import Path

    # 1. Verify Avatar ownership
    result = await db.execute(
        select(Avatar).where(Avatar.id == req.avatar_id, Avatar.user_id == current_user.id)
    )
    avatar = result.scalar_one_or_none()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar no encontrado o no pertenece al usuario")

    # 2. Check Credits
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    COST = 15.0 # High-fidelity costs slightly more
    if not user or user.credits < COST:
         raise HTTPException(status_code=402, detail="Créditos insuficientes")

    # 3. Load Anchor Image
    anchor_b64 = None
    if avatar.reference_pack_url:
        local_path = Path(avatar.reference_pack_url.lstrip("/"))
        if local_path.exists():
            anchor_b64 = base64.b64encode(local_path.read_bytes()).decode('utf-8')
    
    if not anchor_b64:
        raise HTTPException(status_code=400, detail="El avatar no tiene una imagen de referencia válida")

    # 4. Generate
    try:
        image_b64 = await generate_consistent_avatar(
            prompt=req.prompt,
            anchor_image_b64=anchor_b64,
            face_weight=req.face_weight,
            seed=req.seed
        )
        
        # Deduct credits
        user.credits -= COST
        await db.commit()

        return {
            "image_b64": image_b64,
            "credits_remaining": user.credits,
            "avatar_id": avatar.id
        }
    except Exception as e:
        logger.error(f"Consistency generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


SAVE_COST = 0  # Saving is free
AVATAR_STORAGE_DIR = "storage/avatars"


class AvatarSaveRequest(BaseModel):
    name: str = "Mi Avatar"
    image_b64: str              # Snapshot base64 del canvas 3D (maniquí)
    refined_image_b64: Optional[str] = None  # Imagen HD generada por IA (Flux + ControlNet)
    morphs: Optional[Dict[str, Any]] = None
    styles: Optional[Dict[str, Any]] = None


class AvatarSaveResponse(BaseModel):
    id: int
    name: str
    texture_url: str
    message: str


@router.post("/save", response_model=AvatarSaveResponse)
async def save_avatar(
    req: AvatarSaveRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Guarda el avatar HD en disco y persiste los metadatos en BD.
    
    Si se proporciona refined_image_b64 (imagen IA), esta se convierte en la imagen
    principal del avatar. La captura del maniquí 3D se archiva en los metadatos.
    """
    os.makedirs(AVATAR_STORAGE_DIR, exist_ok=True)
    uid_suffix = uuid.uuid4().hex[:8]
    source_type = "mannequin_3d"
    base_snapshot_url: Optional[str] = None

    # --- 1. Guardar siempre la captura base del maniquí 3D ---
    raw_snapshot = req.image_b64
    if raw_snapshot.startswith("data:"):
        raw_snapshot = raw_snapshot.split(",", 1)[1]
    try:
        snapshot_bytes = base64.b64decode(raw_snapshot)
    except Exception:
        raise HTTPException(status_code=400, detail="Imagen base64 del maniquí inválida")

    snapshot_filename = f"avatar_snap_{current_user.id}_{uid_suffix}.png"
    snapshot_path = os.path.join(AVATAR_STORAGE_DIR, snapshot_filename)
    with open(snapshot_path, "wb") as f:
        f.write(snapshot_bytes)
    base_snapshot_url = f"/storage/avatars/{snapshot_filename}"

    # --- 2. Si hay imagen HD refinada por IA, usarla como imagen principal ---
    if req.refined_image_b64:
        raw_hd = req.refined_image_b64
        if raw_hd.startswith("data:"):
            raw_hd = raw_hd.split(",", 1)[1]
        try:
            hd_bytes = base64.b64decode(raw_hd)
        except Exception:
            raise HTTPException(status_code=400, detail="Imagen base64 HD inválida")

        hd_filename = f"avatar_hd_{current_user.id}_{uid_suffix}.png"
        hd_path = os.path.join(AVATAR_STORAGE_DIR, hd_filename)
        with open(hd_path, "wb") as f:
            f.write(hd_bytes)
        texture_url = f"/storage/avatars/{hd_filename}"
        source_type = "professional_hd"  # Marcamos como avatar de alta definición
    else:
        # Sin refinado: usar la captura del maniquí como imagen principal
        texture_url = base_snapshot_url

    # --- 3. Persistir en base de datos ---
    avatar = Avatar(
        user_id=current_user.id,
        name=req.name,
        source_type=source_type,
        source_data=str(req.morphs or {}),
        reference_pack_url=texture_url,
        metadata_json={
            "styles": req.styles or {},
            "morphs": req.morphs or {},
            "base_snapshot_url": base_snapshot_url,  # Siempre guardamos el 3D base
            "is_hd": bool(req.refined_image_b64),
        },
        status="ready",
    )
    db.add(avatar)
    await db.commit()
    await db.refresh(avatar)

    logger.info(f"Avatar guardado: id={avatar.id}, tipo={source_type}, user={current_user.id}")

    return AvatarSaveResponse(
        id=avatar.id,
        name=avatar.name,
        texture_url=texture_url,
        message="✨ Avatar HD guardado correctamente en tu colección." if req.refined_image_b64 else "Avatar guardado correctamente en tu colección.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# FACE PROJECTION: Blender-based face → mannequin UV projection
# ─────────────────────────────────────────────────────────────────────────────

class FaceProjectRequest(BaseModel):
    face_image_b64: str        # Base64 of the Flux-generated face PNG
    mannequin_glb_b64: Optional[str] = None  # Optional GLB of the current mannequin

class FaceProjectResponse(BaseModel):
    glb_base64: str            # Base64 of the projected GLB with shape keys
    logs: Optional[str] = None


BLENDER_FACE_PROJECT_URL = "https://ignaciourbinakonecta--blender-avatar-service-api-project-face.modal.run"


@router.post("/project-face", response_model=FaceProjectResponse)
async def project_face(
    req: FaceProjectRequest,
    current_user=Depends(get_current_user),
):
    """
    Projects a Flux-generated face onto the mannequin using Blender's UV Project modifier.
    Returns a GLB with proper head-only UV mapping and shape keys for manual correction.
    """
    import httpx

    logger.info(f"Face projection requested by user {current_user.id}")

    face_b64 = req.face_image_b64
    if "," in face_b64:
        face_b64 = face_b64.split(",", 1)[1]

    payload = {"face_image_b64": face_b64}
    if req.mannequin_glb_b64:
        mannequin_b64 = req.mannequin_glb_b64
        if "," in mannequin_b64:
            mannequin_b64 = mannequin_b64.split(",", 1)[1]
        payload["mannequin_glb_b64"] = mannequin_b64

    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            resp = await client.post(
                BLENDER_FACE_PROJECT_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error(f"Blender face projection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Blender projection failed: {str(e)}")

    return FaceProjectResponse(
        glb_base64=data.get("glb_base64", ""),
        logs=data.get("logs"),
    )
