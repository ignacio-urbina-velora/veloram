"""Wan 2.2 Image Generation Service via fal.ai API.

Motor Hiperrealista v3.0 — Generación directa sin dependencia de maniquí 3D.
Optimizado para retratos UGC hiperrealistas estilo contenido natural.
"""

import os
import base64
import logging
import httpx
from typing import Optional, Any

from app.config import settings

logger = logging.getLogger(__name__)

# ─── Tier Configuration ──────────────────────────────────────────────
TIER_CONFIG = {
    "quick":        {"steps": 20, "guidance": 4.0, "width": 576,  "height": 1024, "cost": 0.015},
    "professional": {"steps": 30, "guidance": 4.5, "width": 768,  "height": 1344, "cost": 0.025},
    "cinematic":    {"steps": 40, "guidance": 5.0, "width": 1024, "height": 1792, "cost": 0.040},
}

# ─── Negative Prompt (Universal) ─────────────────────────────────────
NEGATIVE_PROMPT = (
    "CGI, 3D render, cartoon, illustration, painting, airbrushed skin, "
    "plastic skin, doll-like, overprocessed, HDR effect, oversaturated, "
    "studio backdrop, posed look, stock photo feel, watermark, text, "
    "anime, manga, digital art, oversmoothed skin, waxy, blurry, low quality, "
    "deformed, bad anatomy, extra limbs, bad hands, mutated, cross-eyed, "
    "ugly, distorted face, asymmetric eyes, unnatural pose, stiff expression, "
    "flat lighting, artificial bokeh, instagram filter, beauty filter, "
    "oversharpened, noise, grain artifacts, jpeg artifacts"
)


def build_wan22_prompt(
    gender: str = "woman",
    age: int = 25,
    ethnicity: str = "diverse",
    hair_color: str = "brown",
    hairstyle: str = "medium length",
    expression: str = "neutral",
    skin_tone: str = "natural",
    eye_color: str = "brown",
    eye_shape: str = "almond",
    face_shape: str = "oval",
    makeup: str = "minimal",
    lighting: str = "natural ambient",
    extra: str = "",
    **kwargs: Any,
) -> str:
    """
    Build a hyperrealistic UGC-style prompt optimized for Wan 2.2 14B.
    
    Research-backed structure for Wan 2.2:
    - Subject details FIRST (model prioritizes early tokens)
    - CFG 3.5-5.0 range (lower = more natural, less "AI look")
    - Natural imperfections for breaking the uncanny valley
    - Camera/lens specs at the end for subtle influence
    """
    # Clean up "none" values
    ethnicity = ethnicity if ethnicity and ethnicity.lower() not in ("ninguno específico", "none", "") else "diverse"
    
    prompt = (
        # === SUBJECT (most important — Wan 2.2 prioritizes early tokens) ===
        f"Intimate candid portrait of a real {age} year old {ethnicity} {gender.lower()}, "
        f"{face_shape} face, {skin_tone} complexion, "
        f"{eye_color} {eye_shape} eyes with wet reflective cornea and visible iris striations, "
        f"natural {hair_color} {hairstyle} hair with individual flyaway strands catching the light, "
        f"{expression} expression with subtle asymmetry, "
        
        # === SKIN REALISM (critical for hyperrealism) ===
        f"extremely detailed skin texture with visible pores and fine lines, "
        f"natural skin variation and micro-blemishes, subtle vellus hair on jawline, "
        f"realistic subsurface scattering on ears and nose, natural skin oils, "
        f"{makeup} makeup, "
        
        # === ENVIRONMENT & LIGHTING ===
        f"{lighting} lighting with natural light falloff, "
        f"soft volumetric atmosphere, real environment background slightly out of focus, "
        
        # === CAMERA & TECHNICAL (end of prompt for subtle influence) ===
        f"shot on 85mm f/1.8 lens, shallow depth of field, "
        f"film-like color rendering, natural color grading, "
        f"RAW unprocessed photo, authentic candid moment"
    )

    if extra:
        prompt += f", {extra}"

    return prompt


async def generate_wan22_image(
    prompt: str,
    negative_prompt: str = NEGATIVE_PROMPT,
    tier: str = "professional",
    seed: int = -1,
) -> Optional[str]:
    """
    Generate a hyperrealistic portrait using Wan 2.2 14B via fal.ai.
    
    Returns base64-encoded image string or None on failure.
    Cost: ~$0.025 per image (professional tier).
    """
    fal_key = settings.FAL_KEY
    if not fal_key:
        logger.error("[Wan22] FAL_KEY not configured")
        return None

    cfg = TIER_CONFIG.get(tier, TIER_CONFIG["professional"])

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "image_size": {"width": cfg["width"], "height": cfg["height"]},
        "num_inference_steps": cfg["steps"],
        "guidance_scale": cfg["guidance"],
        "enable_safety_checker": False,
    }
    if seed > 0:
        payload["seed"] = seed

    fal_url = "https://fal.run/fal-ai/wan/v2.2-a14b/text-to-image"
    headers = {
        "Authorization": f"Key {fal_key}",
        "Content-Type": "application/json",
    }

    try:
        logger.info(f"[Wan22] Generating image (tier={tier}, steps={cfg['steps']})...")
        logger.info(f"[Wan22] Prompt: {prompt[:100]}...")

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(fal_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # fal.ai Wan 2.2 returns {"image": {"url": "..."}}
                image_url = None
                if "image" in data:
                    image_url = data["image"].get("url")
                elif "images" in data:
                    image_url = data["images"][0].get("url") if data["images"] else None

                if image_url:
                    # Download the image and convert to base64
                    img_response = await client.get(image_url)
                    if img_response.status_code == 200:
                        b64 = base64.b64encode(img_response.content).decode("utf-8")
                        logger.info(f"[Wan22] Success! Image size: {len(img_response.content)} bytes")
                        return b64
                    else:
                        logger.error(f"[Wan22] Failed to download image: HTTP {img_response.status_code}")
                else:
                    logger.error(f"[Wan22] No image URL in response: {data}")
            else:
                logger.error(f"[Wan22] fal.ai returned HTTP {response.status_code}: {response.text}")

    except httpx.TimeoutException:
        logger.error("[Wan22] Request timed out (120s)")
    except Exception as e:
        logger.error(f"[Wan22] Exception: {e}")

    return None


async def generate_avatar_wan22(
    gender: str = "woman",
    age: int = 25,
    ethnicity: str = "diverse",
    hair_color: str = "brown",
    hairstyle: str = "medium length",
    expression: str = "neutral",
    skin_tone: str = "natural",
    eye_color: str = "brown",
    eye_shape: str = "almond",
    face_shape: str = "oval",
    makeup: str = "minimal",
    lighting: str = "natural ambient",
    extra: str = "",
    tier: str = "professional",
    **kwargs: Any,
) -> Optional[str]:
    """
    High-level API: Build prompt + generate image in one call.
    Returns base64 string or None.
    """
    prompt = build_wan22_prompt(
        gender=gender,
        age=age,
        ethnicity=ethnicity,
        hair_color=hair_color,
        hairstyle=hairstyle,
        expression=expression,
        skin_tone=skin_tone,
        eye_color=eye_color,
        eye_shape=eye_shape,
        face_shape=face_shape,
        makeup=makeup,
        lighting=lighting,
        extra=extra,
    )

    return await generate_wan22_image(prompt=prompt, tier=tier)


def build_shot_prompt_wan22(
    shot_prompt: str,
    avatar_metadata: Optional[dict] = None,
    lighting: str = "natural",
    camera_movement: str = "static",
    mood: str = "neutral",
) -> str:
    """
    Build a prompt for a video shot that maintains character consistency.
    Combines the shot's unique action with the avatar's visual DNA.
    """
    # 1. Base identification (Natural Hiperrealismo v3.0)
    subject_desc = "A real person"
    if avatar_metadata:
        age = avatar_metadata.get("age", 25)
        ethnicity = avatar_metadata.get("ethnicity", "diverse")
        gender = avatar_metadata.get("gender", "woman").lower()
        hair = f"{avatar_metadata.get('hair_color', 'brown')} {avatar_metadata.get('hairstyle', 'medium length')}"
        subject_desc = f"A real {age} year old {ethnicity} {gender} with {hair} hair"

    # 2. Action / Context
    # We put the action early for Wan 2.2 to prioritize it
    prompt = (
        f"Cinematic shot of {subject_desc}, {shot_prompt}. "
        f"Subtle {mood} mood, {lighting} lighting. "
        
        # 3. Quality & Realism (Natural Hiperrealismo Reinforcement)
        f"Extreme skin detail, visible pores, natural skin texture, "
        f"highly detailed facial features matching the character, "
        f"natural lighting falloff, sharp focus, 8k resolution, "
        
        # 4. Camera movement influence
        f"authentic {camera_movement} camera feel, shot on high-end cinema camera, "
        f"professional color grading, hyper-realistic candid style"
    )

    return prompt


async def generate_shot_wan22(
    shot_prompt: str,
    avatar_id: Optional[int] = None,
    avatar_metadata: Optional[dict] = None,
    lighting: str = "natural",
    camera_movement: str = "static",
    mood: str = "neutral",
    tier: str = "professional",
) -> Optional[str]:
    """
    Generate a high-quality keyframe for a workflow shot using Wan 2.2.
    """
    prompt = build_shot_prompt_wan22(
        shot_prompt=shot_prompt,
        avatar_metadata=avatar_metadata,
        lighting=lighting,
        camera_movement=camera_movement,
        mood=mood
    )
    
    # We use the standard image generation but with the refined shot prompt
    return await generate_wan22_image(prompt=prompt, tier=tier)


# ─── Video Generation (I2V) ──────────────────────────────────────────

async def generate_video(
    engine: str,
    prompt: Optional[str] = None,
    image_url: Optional[str] = None,
    image_b64: Optional[str] = None,
    **kwargs: Any
) -> Optional[str]:
    """
    Generic video generation entry point.
    Returns URL of the generated video or None.
    """
    if engine == "wan_v2.1" or engine == "wan_v2.2":
        return await generate_video_wan(prompt=prompt, image_url=image_url, image_b64=image_b64, **kwargs)
    elif engine == "ltx_video":
        return await generate_video_ltx(prompt=prompt, image_url=image_url, image_b64=image_b64, **kwargs)
    elif engine == "hunyuan":
        return await generate_video_hunyuan(prompt=prompt, image_url=image_url, image_b64=image_b64, **kwargs)
    
    logger.error(f"[VideoService] Unsupported engine: {engine}")
    return None


async def generate_video_wan(
    prompt: str,
    image_url: Optional[str] = None,
    image_b64: Optional[str] = None,
    tier: str = "professional",
    **kwargs: Any
) -> Optional[str]:
    """Wan v2.1/2.2 Image-to-Video generation."""
    fal_key = settings.FAL_KEY
    if not fal_key: return None

    # Resolve image input
    source_image = image_url
    if image_b64 and not source_image:
        source_image = f"data:image/png;base64,{image_b64}"

    payload = {
        "prompt": prompt,
        "image_url": source_image,
        "num_frames": 81, # 5s at 16fps approx
        "enable_safety_checker": False,
    }
    
    fal_url = "https://fal.run/fal-ai/wan/v2.1-1.3b/image-to-video"
    return await _call_fal_video(fal_url, payload, fal_key)


async def generate_video_ltx(
    prompt: str,
    image_url: Optional[str] = None,
    image_b64: Optional[str] = None,
    **kwargs: Any
) -> Optional[str]:
    """LTX-Video Image-to-Video generation."""
    fal_key = settings.FAL_KEY
    if not fal_key: return None

    source_image = image_url
    if image_b64 and not source_image:
        source_image = f"data:image/png;base64,{image_b64}"

    payload = {
        "prompt": prompt,
        "image_url": source_image,
        "enable_safety_checker": False,
    }
    
    fal_url = "https://fal.run/fal-ai/ltx-video"
    return await _call_fal_video(fal_url, payload, fal_key)


async def generate_video_hunyuan(
    prompt: str,
    image_url: Optional[str] = None,
    image_b64: Optional[str] = None,
    **kwargs: Any
) -> Optional[str]:
    """HunyuanVideo Image-to-Video generation."""
    fal_key = settings.FAL_KEY
    if not fal_key: return None

    source_image = image_url
    if image_b64 and not source_image:
        source_image = f"data:image/png;base64,{image_b64}"

    payload = {
        "prompt": prompt,
        "image_url": source_image,
        "enable_safety_checker": False,
    }
    
    fal_url = "https://fal.run/fal-ai/hunyuan-video"
    return await _call_fal_video(fal_url, payload, fal_key)


async def _call_fal_video(url: str, payload: dict, api_key: str) -> Optional[str]:
    """Utility to call fal.ai video endpoints."""
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                video_url = data.get("video", {}).get("url")
                if not video_url:
                    video_url = data.get("url") # Fallback for some endpoints
                return video_url
            else:
                logger.error(f"[FalVideo] Error {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"[FalVideo] Exception: {e}")
    return None
