"""Modal service — calls the deployed FLUX web endpoint to generate avatar images."""

import httpx
import base64
from pathlib import Path
from typing import Any
from app.config import settings

MODAL_ENDPOINT_URL: str = settings.MODAL_ENDPOINT_URL
MODAL_TOKEN_ID: str = settings.MODAL_TOKEN_ID
MODAL_TOKEN_SECRET: str = settings.MODAL_TOKEN_SECRET



def build_avatar_prompt(
    gender: str,
    age: int,
    country: str,
    build: str,
    eyes: str,
    hair_color: str,
    hairstyle: str,
    clothing: str,
    breast_size: str | None = None,
    extra: str = "",
) -> str:
    """Convert avatar form parameters into a FLUX-optimized prompt."""

    ethnicity_map = {
        "Japón": "Japanese",
        "Estados Unidos": "American",
        "Brasil": "Brazilian",
        "Rusia": "Russian",
        "Corea": "Korean",
        "China": "Chinese",
        "México": "Mexican",
        "Colombia": "Colombian",
        "España": "Spanish",
        "Egipto": "Egyptian",
        "Francia": "French",
        "Ninguno específico": "",
    }

    build_map = {
        "Muscular": "muscular athletic",
        "Atlética": "athletic toned",
        "Delgada": "slim",
        "Curvy": "curvy",
        "Robusta": "full-figured",
    }

    clothing_map = {
        "Casual / Streetwear": "casual streetwear outfit",
        "Elegante / Vestido de noche": "elegant evening dress",
        "Ropa interior / Lingerie": "lingerie",
        "Traje de baño / Bikini": "swimsuit bikini",
        "Traje ejecutivo": "professional business suit",
        "Cyberpunk Scifi": "cyberpunk sci-fi outfit",
    }

    breast_map = {
        "Pequeño": "small chest",
        "Mediano": "medium chest",
        "Grande": "large chest",
        "Muy Grande": "very large chest",
    }

    ethnicity = ethnicity_map.get(country, "")
    body = build_map.get(build, build)
    outfit = clothing_map.get(clothing, clothing)

    # Anclajes de calidad y proporciones faciales correctas para FLUX
    QUALITY_PREFIX = (
        "RAW photo, sharp focus, photorealistic, 8k uhd, "
        "natural facial proportions, symmetrical face, correct face anatomy, "
        "realistic face structure, no distortion"
    )
    NEGATIVE_SUFFIX = (
        # Se agrega al final como contexto negativo explícito dentro del prompt positivo
        # FLUX no tiene negative prompt nativo, así que lo reforzamos con positivos
        "well-proportioned oval face, natural jawline, realistic nose width, "
        "balanced facial features"
    )

    parts = [
        QUALITY_PREFIX,
        f"portrait of a {age} year old",
        f"{ethnicity} {gender.lower()}" if ethnicity else gender.lower(),
        f"{body}" if body else "",
        f"with {eyes} eyes",
        f"and {hair_color} {hairstyle} hair",
        f"wearing {outfit}",
        NEGATIVE_SUFFIX,
    ]

    if gender == "Mujer" and breast_size:
        parts.append(breast_map.get(breast_size, ""))

    if extra.strip():
        parts.append(extra.strip())

    return ", ".join(p for p in parts if p)


async def generate_avatar_image(prompt: str, base_image_b64: str | None = None, strength: float = 0.85) -> str:
    """
    Call the Modal web endpoint and return a base64-encoded PNG string.
    Raises httpx.HTTPStatusError on failure.
    """
    if not MODAL_ENDPOINT_URL:
        raise ValueError(
            "MODAL_ENDPOINT_URL no configurado. Corre: modal deploy modal_app.py y copia la URL al .env"
        )

    payload: dict[str, Any] = {
        "prompt": prompt,
        "width": 896,    # Proporción 7:8 — evita caras alargadas vs el 768x1024 anterior
        "height": 1152,
        "steps": 28,     # Más pasos = mejor anatomía facial (era 4, muy bajo para FLUX dev)
    }
    
    if base_image_b64:
        payload["init_image_b64"] = base_image_b64
        payload["strength"] = strength

    # Modal web endpoints accept token auth via custom headers
    headers = {
        "Content-Type": "application/json",
        "x-modal-token-id": MODAL_TOKEN_ID,
        "x-modal-token-secret": MODAL_TOKEN_SECRET
    }

    async with httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client:
        try:
            response = await client.post(
                MODAL_ENDPOINT_URL,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            if "image_b64" not in data:
                raise ValueError("Modal response missing 'image_b64'")
                
            return data["image_b64"]
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            print(f"Modal HTTP Error {e.response.status_code}: {error_detail}")
            raise ValueError(f"Modal Service Error: {error_detail or str(e)}")
        except Exception as e:
            print(f"Error calling Modal FLUX: {e}")
            raise


async def save_avatar_image(b64_str: str, filename: str) -> str:
    """Save base64 image to local storage dir. Returns relative URL."""
    storage_dir = Path("storage/avatars")
    storage_dir.mkdir(parents=True, exist_ok=True)

    img_bytes = base64.b64decode(b64_str)
    filepath = storage_dir / filename
    filepath.write_bytes(img_bytes)
    return f"/storage/avatars/{filename}"
