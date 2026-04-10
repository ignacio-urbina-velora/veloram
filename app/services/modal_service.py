"""Modal service — calls the deployed FLUX web endpoint to generate avatar images."""

import os
import base64
import logging
import httpx
from pathlib import Path
from typing import Any, Optional, List, Dict, Union
from app.config import settings

# Absolute path for storage to avoid path resolution issues
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_ABS_PATH = BASE_DIR / "storage"
os.makedirs(STORAGE_ABS_PATH, exist_ok=True)

logger = logging.getLogger(__name__)

# Minimal 1x1 grey JPEG as fallback placeholder
_PLACEHOLDER_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U"
    "HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA"
    "Ah8AAgABAAMRAf/EABQAAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA"
    "/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAT8A"
    "Kg//2Q=="
)

def _make_placeholder_b64(width: int = 1024, height: int = 576) -> str:
    """Return a minimal valid JPEG as b64 placeholder (grey 1x1, tiny)."""
    return _PLACEHOLDER_JPEG_B64

MODAL_ENDPOINT_URL: str = settings.MODAL_ENDPOINT_URL or "https://ignaciourbinakonecta--avatar-generate.modal.run"
MODAL_TOKEN_ID: str = settings.MODAL_TOKEN_ID or "wk-zgKLgaMEjSbsJJfCnoGZm4"
MODAL_TOKEN_SECRET: str = settings.MODAL_TOKEN_SECRET or "ws-fKNahBbuJRC4OXpd8pnrkO"

def build_avatar_prompt(
    gender: str,
    age: int,
    country: str = "",
    eyes: str = "",
    hair_color: str = "",
    hairstyle: str = "",
    extra: str = "",
    face_shape: str = "oval",
    skin_tone: str = "natural",
    eye_shape: str = "almond",
    eyebrow_style: str = "natural",
    hair_length: str = "medium",
    bangs: str = "no",
    lip_volume: str = "full",
    lip_color: str = "natural",
    makeup: str = "minimal",
    expression: str = "neutral",
    lighting: str = "soft studio",
    **kwargs: Any
) -> str:
    """
    Builds a strict, hyper-realistic candid portrait ignoring any CGI parameters.
    """
    etnia = country if country and country != "Ninguno específico" else "diverse"
    
    prompt = f"""
    ultra photorealistic close-up portrait of a {age} year old {etnia} {gender.lower()}, {face_shape} face shape,
    8k raw photo, shot on Canon EOS R5 with 85mm f/1.4 lens,
    natural soft window light mixed with golden hour cinematic lighting,
    extremely detailed skin texture with visible pores and subtle freckles,
    natural skin imperfections and micro texture, realistic subsurface scattering,
    natural skin oils and peach fuzz, {skin_tone} skin tone,
    {eyes} {eye_shape} eyes with realistic iris depth and natural catchlight,
    realistic eyelashes, {eyebrow_style} eyebrows, {hair_color} {hair_length} {hairstyle} hair with {bangs} bangs,
    {lip_volume} lips with {lip_color} color, {makeup} makeup, {expression} expression,
    cinematic color grading, film grain, masterpiece, best quality,
    highly detailed, photorealistic, sharp focus
    """.strip()

    if extra:
        prompt += f", {extra}"
        
    return prompt

async def generate_image(
    prompt: str,
    base_image_b64: str | None = None,
    strength: float = 0.85,
    width: int = 1024,
    height: int = 1024,
    steps: int = 28,
    tier: str = "professional"
) -> str | None:
    """Generate image via Modal endpoint. Returns base64 string or None."""
    
    # Inyección de prompt avanzado (ya viene listo del builder, pero por si acaso viene de texto libre)
    if "Canon EOS" not in prompt:
        advanced_prompt = f"{prompt}, ultra photorealistic close-up portrait, 8k raw photo, Canon EOS R5, 85mm f/1.4, extreme skin detail, visible pores"
    else:
        advanced_prompt = prompt
        
    negative_prompt = "cartoon, illustration, painting, drawing, 3d render, cgi, plastic skin, barbie, doll, smooth skin, airbrushed, waxy skin, blurry, low detail, deformed, bad anatomy, extra limbs, bad hands, text, watermark, overexposed, underexposed, low quality, stylized, anime, digital art, flat lighting, artificial"

    modal_url = MODAL_ENDPOINT_URL
    modal_id = MODAL_TOKEN_ID
    modal_secret = MODAL_TOKEN_SECRET

    # TIERS dict for steps
    t_steps = {"cinematic": 40, "professional": 32, "quick": 25}
    actual_steps = t_steps.get(tier, steps)

    # 1. Use Fal.ai for pure text-to-image (Much faster, avoids Modal 10-minute queues)
    if not base_image_b64 and settings.FAL_KEY:
        try:
            print(f"[ModalService] Attempting Fal.ai generation: {prompt[:50]}...")
            async with httpx.AsyncClient(timeout=120.0) as client:
                fal_url = "https://fal.run/fal-ai/flux/dev"
                payload_fal = {
                    "prompt": advanced_prompt,
                    "image_size": {"width": width, "height": height},
                    "num_inference_steps": actual_steps,
                    "enable_safety_checker": False
                }

                response = await client.post(
                    fal_url,
                    json=payload_fal,
                    headers={"Authorization": f"Key {settings.FAL_KEY}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("images", [{}])[0].get("url")
                    if image_url:
                        img_res = await client.get(image_url)
                        if img_res.status_code == 200:
                            print(f"[ModalService] Fal.ai generation successful. Size: {len(img_res.content)} bytes")
                            return base64.b64encode(img_res.content).decode("utf-8")
                        else:
                            print(f"[ModalService] Failed to download image from Fal.ai: {img_res.status_code}")
                
                print(f"[ModalService] Fal.ai failed (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"[ModalService] Fal.ai exception: {str(e)}")

    # 2. Use Modal (Motor 2.0 with ControlNets & Upscale) if Fal failed or for 3D-to-2D
    if True: # We enforce Modal
        if not modal_url or not modal_id:
            logger.warning("[ModalService] Missing Modal credentials. Skipping call.")
            return _make_placeholder_b64(width, height)

        payload: dict[str, Any] = {
            "prompt": advanced_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "tier": tier
        }
        if base_image_b64:
            payload["init_image_b64"] = base_image_b64
            payload["strength"] = strength

        headers = {
            "Content-Type": "application/json",
            "x-modal-token-id": modal_id,
            "x-modal-token-secret": modal_secret
        }

        async with httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client:
            try:
                response = await client.post(modal_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                if "image_b64" in data:
                    print("[ModalService] Modal generation successful.")
                    return data["image_b64"]
                print(f"[ModalService] Modal response missing 'image_b64': {data}")
            except httpx.HTTPStatusError as e:
                print(f"[ModalService] Modal HTTP Error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                print(f"[ModalService] Modal error: {e}")
    else:
        print("[ModalService] Modal not configured, skipping.")

    # 3. Last resort: return a placeholder image so the pipeline doesn't crash
    print("[ModalService] WARNING: All generation backends failed. Returning placeholder image.")
    return _make_placeholder_b64(width, height)

async def generate_flux_general(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 28,
    seed: Optional[int] = None,
    ip_adapters: Optional[List[Dict[str, Any]]] = None,
    controlnets: Optional[List[Dict[str, Any]]] = None,
    guidance_scale: float = 3.5,
    enable_safety_checker: bool = False
) -> str:
    """
    Advanced generation using fal-ai/flux-general.
    Supports IP-Adapter (Identity) and ControlNet (Structure).
    """
    if not settings.FAL_KEY:
        raise ValueError("FAL_KEY is required for Flux-General features")

    payload = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "enable_safety_checker": enable_safety_checker,
    }

    if seed is not None:
        payload["seed"] = seed
    if ip_adapters:
        payload["ip_adapters"] = ip_adapters
    if controlnets:
        payload["controlnets"] = controlnets

    try:
        print(f"[ModalService] flux-general generation: {prompt[:50]}...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://fal.run/fal-ai/flux-general",
                json=payload,
                headers={"Authorization": f"Key {settings.FAL_KEY}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("images", [{}])[0].get("url")
                if image_url:
                    img_res = await client.get(image_url)
                    if img_res.status_code == 200:
                        return base64.b64encode(img_res.content).decode("utf-8")
            
            error_msg = f"Fal-ai flux-general failed ({response.status_code}): {response.text}"
            print(f"[ModalService] ERROR: {error_msg}")
            raise ValueError(error_msg)
    except Exception as e:
        print(f"[ModalService] Exception in flux-general: {e}")
        raise

async def generate_consistent_avatar(
    prompt: str,
    anchor_image_b64: Optional[str] = None,
    depth_image_b64: Optional[str] = None,
    face_weight: float = 0.7,
    depth_weight: float = 0.5,
    seed: Optional[int] = None,
    width: int = 896,
    height: int = 1152
) -> str:
    """
    High-level API for character consistency.
    Uses anchor_image as IP-Adapter reference.
    """
    ip_adapters = []
    if anchor_image_b64:
        ip_adapters.append({
            "image_url": f"data:image/png;base64,{anchor_image_b64}",
            "scale": face_weight
        })

    controlnets = []
    if depth_image_b64:
        # Note: In fal-ai/flux-general, we need the specific model path for depth
        controlnets.append({
            "path": "https://huggingface.co/x-labs/flux-controlnet-depth/blob/main/diffusion_pytorch_model.safetensors",
            "image_url": f"data:image/png;base64,{depth_image_b64}",
            "conditioning_scale": depth_weight
        })

    return await generate_flux_general(
        prompt=prompt,
        width=width,
        height=height,
        seed=seed,
        ip_adapters=ip_adapters,
        controlnets=controlnets
    )

async def generate_hyperreal_texture(
    references: List[Dict[str, str]], 
    prompt: str,
    width: int = 896,
    height: int = 1152,
    tier: str = "professional"
) -> str:
    """
    Motor de Hiperrealismo 2.0: Soporta tiers (cinematic, professional, quick)
    e inyecta prompts avanzados de textura editorial.
    """
    modal_url = MODAL_ENDPOINT_URL
    modal_id = MODAL_TOKEN_ID
    modal_secret = MODAL_TOKEN_SECRET

    # Inyección de prompt avanzado v2.0
    if "Canon EOS" not in prompt:
        advanced_prompt = f"{prompt}, ultra photorealistic close-up portrait, 8k raw photo, Canon EOS R5, 85mm f/1.4, extreme skin detail, visible pores"
    else:
        advanced_prompt = prompt
    
    negative_prompt = "cartoon, illustration, painting, drawing, 3d render, cgi, plastic skin, barbie, doll, smooth skin, airbrushed, waxy skin, blurry, low detail, deformed, bad anatomy, extra limbs, bad hands, text, watermark, overexposed, underexposed, low quality, stylized, anime, digital art, flat lighting, artificial"

    front_view = next((r["base64"] for r in references if r["view"] == "front"), references[0]["base64"])

    payload: dict[str, Any] = {
        "prompt": advanced_prompt,
        "negative_prompt": negative_prompt, # El worker debe soportar esto o lo ignorará
        "init_image_b64": front_view,
        "width": width,
        "height": height,
        "tier": tier
    }

    headers = {
        "Content-Type": "application/json",
        "x-modal-token-id": modal_id,
        "x-modal-token-secret": modal_secret
    }

    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(modal_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["image_b64"]

async def generate_avatar_image(prompt: str, base_image_b64: str | None = None, strength: float = 0.85, tier: str = "professional") -> str:
    """
    Specific wrapper for avatars (portrait aspect ratio).
    """
    return await generate_image(
        prompt=prompt,
        base_image_b64=base_image_b64,
        strength=strength,
        width=896,
        height=1152, # Portrait
        steps=28, # overridden by tier on server side
        tier=tier
    )

async def save_image(b64_str: str, folder: str, filename: str) -> str:
    """Save base64 image to local storage. Returns relative URL."""
    storage_dir = STORAGE_ABS_PATH / folder
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Strip prefix if present
    if "," in b64_str:
        b64_str = b64_str.split(",", 1)[1]

    try:
        img_bytes = base64.b64decode(b64_str)
        if len(img_bytes) < 1000:
            logger.warning(f"[ModalService] Saving very small image ({len(img_bytes)} bytes) to {filename}")
        
        filepath = storage_dir / filename
        filepath.write_bytes(img_bytes)
        return f"/storage/{folder}/{filename}"
    except Exception as e:
        logger.error(f"[ModalService] Failed to save image {filename}: {str(e)}")
        return ""

async def save_avatar_image(b64_str: str, filename: str) -> str:
    return await save_image(b64_str, "avatars", filename)

async def generate_video_clip(init_image_b64: str, fps: int = 7, motion_bucket_id: int = 127) -> str:
    """
    Call the Modal web endpoint for Stable Video Diffusion and return a base64-encoded MP4 string.
    """
    # NOTE: The user needs to deploy modal_video_app.py and set MODAL_VIDEO_ENDPOINT_URL in .env
    MODAL_VIDEO_ENDPOINT_URL = settings.MODAL_VIDEO_ENDPOINT_URL or "https://ignaciourbinakonecta--video-generate-svd-generate-video-endpoint.modal.run"
    
    payload = {
        "init_image_b64": init_image_b64,
        "fps": fps,
        "motion_bucket_id": motion_bucket_id
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-modal-token-id": MODAL_TOKEN_ID,
        "x-modal-token-secret": MODAL_TOKEN_SECRET
    }

    async with httpx.AsyncClient(timeout=1800.0, follow_redirects=True) as client:
        try:
            response = await client.post(
                MODAL_VIDEO_ENDPOINT_URL,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            if "video_b64" not in data:
                raise ValueError("Modal response missing 'video_b64'")
                
            return data["video_b64"]
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            print(f"Modal HTTP Error {e.response.status_code}: {error_detail}")
            raise ValueError(f"Modal Video Service Error: {error_detail or str(e)}")
        except Exception as e:
            print(f"Error calling Modal SVD: {e}")
            raise
