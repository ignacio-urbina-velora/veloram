"""Application configuration with pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class TierConfig:
    """Per-tier GPU and model configuration.

    vast.ai pricing reference (as of 2026):
    - RTX 5090: $0.23–$0.37/h (spot), ~$0.50/h on-demand
    - H100: $0.90–$1.53/h
    - A100 80GB: $0.70–$1.20/h

    API key: https://cloud.vast.ai/api-keys
    """

    TIERS = {
        1: {
            "name": "Quick",
            "model": "LTX-2 fp8/NVFP8 + Native Audio",
            "gpu_types": ["RTX_5090", "RTX_4090"],
            "min_vram_gb": 24,
            "prefer_comfyui_template": True,
            "gpu_cost_per_hour": (0.23, 0.42),
            "cost_range": (3, 6),
            "wait_minutes": (4, 8),
            "shots_range": (3, 8),
            "workflow": "ltx_video.json",
            "packages": {
                "basic": {"price": 50, "videos": 5, "credits": 22.5},
                "medium": {"price": 85, "videos": 10, "credits": 45.0},
                "full": {"price": 150, "videos": 20, "credits": 90.0},
            },
            "clip_duration_range": (10, 15),
            "resolution": "720p",
            "fps": 24,
            "features": [
                "Avatar del reactor (8 visualizaciones)",
                "ControlNet básico (OpenPose)",
                "Sincronización de audio nativa",
                "Costura de FFmpeg"
            ]
        },
        2: {
            "name": "Pro",
            "model": "Wan 2.2 14B FP8 + NSFW Remix",
            "gpu_types": ["RTX_5090", "A100_80GB"],
            "min_vram_gb": 32,
            "prefer_comfyui_template": True,
            "gpu_cost_per_hour": (0.30, 1.53),
            "cost_range": (8, 14),
            "wait_minutes": (8, 15),
            "shots_range": (5, 15),
            "workflow": "wan_22.json",
            "packages": {
                "basic": {"price": 90, "videos": 5, "credits": 55.0},
                "medium": {"price": 159, "videos": 10, "credits": 110.0},
                "full": {"price": 299, "videos": 20, "credits": 220.0},
            },
            "clip_duration_range": (8, 10),
            "resolution": "1080p",
            "fps": 60,
            "features": [
                "InstantID + FaceID-PlusV2 (12 visualizaciones)",
                "Multi-ControlNet (Profundidad/Pose abierta/Astuto)",
                "Remezcla NSFW LoRA (0.8)",
                "Interpolación 60 FPS",
                "1080p nativo"
            ]
        },
        3: {
            "name": "Cinematic Ultra",
            "model": "HunyuanVideo-I2V 1.5/2.0 bf16 + Post-Pro",
            "gpu_types": ["H100_80GB", "A100_80GB"],
            "min_vram_gb": 80,
            "prefer_comfyui_template": True,
            "gpu_cost_per_hour": (1.10, 3.95),
            "cost_range": (25, 55),
            "wait_minutes": (18, 40),
            "shots_range": (8, 40),
            "workflow": "hunyuan_video.json",
            "packages": {
                "basic": {"price": 350, "videos": 5, "credits": 182.5},
                "medium": {"price": 680, "videos": 10, "credits": 365.0},
                "full": {"price": 1350, "videos": 20, "credits": 730.0},
            },
            "clip_duration_range": (15, 25),
            "resolution": "4K",
            "fps": 60,
            "features": [
                "InstantID + CodeFormer (16 visualizaciones, 99%)",
                "ControlNet completo (5 tipos)",
                "Intensidad LoRA 0,9",
                "LUT de gradación de color 4K de alta calidad",
                "Sin censura absoluta"
            ]
        },
    }

    @classmethod
    def get(cls, tier: int) -> dict:
        return cls.TIERS.get(tier, cls.TIERS[1])


class Settings(BaseSettings):
    """App settings loaded from environment."""

    # App
    APP_NAME: str = "Velora Studio"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    BACKEND_URL: str = "http://localhost:8000"

    # Auth
    JWT_SECRET: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_video_v3.db"

    @property
    def async_database_url(self) -> str:
        """Ensure the URL uses the asyncpg driver if it is PostgreSQL."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # vast.ai
    VAST_API_KEY: str = ""
    VAST_API_BASE: str = "https://console.vast.ai/api/v0"

    # ComfyUI
    COMFYUI_DOCKER_IMAGE: str = "comfyui-platform:latest"
    COMFYUI_PORT: int = 8188

    # Storage (S3)
    S3_BUCKET: str = ""
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT: Optional[str] = None

    # Audio
    ELEVENLABS_API_KEY: str = ""
    XTTS_ENABLED: bool = False

    # FFmpeg
    FFMPEG_PATH: str = "ffmpeg"  # Default to system PATH

    # LoRA URLs
    LORA_WAN_REMIX_URL: str = "https://huggingface.co/FX-FeiHou/wan2.2-Remix"
    LORA_COLLECTION_URL: str = "https://huggingface.co/rahul7star/wan2.2Lora"

    # Pricing
    FREE_CREDITS: float = 50.00  # $ credits for new users

    # Langflow (Director Brain)
    LANGFLOW_BASE_URL: str = ""
    LANGFLOW_API_KEY: str = ""
    LANGFLOW_FLOW_ID: str = ""
    LANGFLOW_APPLICATION_ID: str = ""

    # Flowise (Alternative Director Brain)
    FLOWISE_BASE_URL: str = "http://localhost:3001"
    FLOWISE_API_KEY: str = ""
    FLOWISE_CHATFLOW_ID: str = ""

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Velora Studio <onboarding@velora-studio.site>"

    # Modal (image/avatar generation)
    MODAL_TOKEN_ID: str = ""
    MODAL_TOKEN_SECRET: str = ""
    MODAL_ENDPOINT_URL: str = ""  # Set after: modal deploy modal_app.py

    # AI Agents (Director Brain)
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    DIRECTOR_MODAL_URL: str = ""
    FAL_KEY: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}


settings = Settings()
