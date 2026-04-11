"""Project and Shot models for multi-shot video planning."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
)
from app.database import Base


class Project(Base):
    """A video project containing multiple shots."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=True)

    title = Column(String(200), nullable=False)
    tier = Column(Integer, nullable=False, default=1)  # 1=Quick, 2=Pro, 3=Cinematic

    # Duration
    target_duration_sec = Column(Integer, default=900)  # 15 min = 900s

    # Status
    status = Column(String(30), default="draft")
    # draft → generating → postprocessing → completed → failed

    # Global Context (Coherence)
    global_prompt = Column(Text, nullable=True) # Subject & Atmosphere
    negative_prompt_global = Column(Text, nullable=True)
    style_preset = Column(String(100), nullable=True) # cinematic, cyberpunk, etc.
    is_mock = Column(Integer, default=0) # Using Integer (0/1) for SQLite compatibility as boolean toggle
    video_engine = Column(String(50), default="mock") # mock, wan_v2.1, wan_v2.2, ltx_video, hunyuan


    # Output
    final_video_url = Column(String(500), nullable=True)
    total_cost_usd = Column(Float, default=0.0)

    # --- LANGGRAPH PERSISTENCE (Hybrid) ---
    director_bible = Column(JSON, nullable=True) # The source of truth for style/characters
    bible_version = Column(Integer, default=1)
    thread_id = Column(String(100), nullable=True, index=True) # LangGraph checkpointer link
    # --------------------------------------

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class Shot(Base):
    """An individual shot/sequence within a project."""
    __tablename__ = "shots"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)

    # Order in sequence
    order = Column(Integer, nullable=False, default=0)

    # Director controls
    prompt = Column(Text, nullable=False)
    camera_movement = Column(String(50), default="static")
    # static, pan_left, pan_right, dolly_in, dolly_out, orbit, tilt_up, tilt_down, crane

    lighting = Column(String(100), default="natural")
    # natural, warm_golden, cold_blue, dramatic_shadows, neon, candlelight, sunset, studio

    mood = Column(String(100), default="neutral")
    # neutral, intense, romantic, dramatic, mysterious, playful, seductive, melancholic

    dialogue = Column(Text, nullable=True)  # Spoken text / sounds

    # Negative prompt for refinement
    negative_prompt = Column(Text, nullable=True)

    # Duration
    duration_target_sec = Column(Float, default=10.0)

    # Output
    status = Column(String(20), default="pending")
    # pending → queued → generating → interpolating → done → failed

    clip_url = Column(String(500), nullable=True)
    preview_url = Column(String(500), nullable=True)  # Low-res preview thumbnail

    # Generation metadata
    generation_metadata = Column(JSON, nullable=True)
    # {seed, actual_duration, model_used, lora_strength, controlnet_type, etc.}

    created_at = Column(DateTime, default=datetime.utcnow)
