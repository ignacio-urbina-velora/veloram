"""Project and Shot schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Shot schemas ---

class ShotCreate(BaseModel):
    prompt: str = Field(min_length=2, max_length=2000)
    camera_movement: str = Field(
        default="static",
        pattern="^(static|pan_left|pan_right|dolly_in|dolly_out|orbit|tilt_up|tilt_down|crane)$",
    )
    lighting: str = Field(default="natural", max_length=100)
    mood: str = Field(default="neutral", max_length=100)
    dialogue: Optional[str] = Field(default=None, max_length=500)
    negative_prompt: Optional[str] = Field(default=None, max_length=1000)
    duration_target_sec: float = Field(ge=1, le=120, default=10.0)


class ShotUpdate(BaseModel):
    prompt: Optional[str] = Field(default=None, min_length=10, max_length=2000)
    camera_movement: Optional[str] = None
    lighting: Optional[str] = None
    mood: Optional[str] = None
    dialogue: Optional[str] = None
    negative_prompt: Optional[str] = None
    duration_target_sec: Optional[float] = Field(default=None, ge=5, le=120)
    order: Optional[int] = None

class PromptRefineRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

class PromptRefineResponse(BaseModel):
    refined_prompt: str


class ShotResponse(BaseModel):
    id: int
    order: int
    prompt: str
    camera_movement: str
    lighting: str
    mood: str
    dialogue: Optional[str]
    negative_prompt: Optional[str]
    duration_target_sec: float
    status: str
    clip_url: Optional[str]
    preview_url: Optional[str]

    class Config:
        from_attributes = True


# --- Project schemas ---

class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    tier: int = Field(ge=1, le=3, default=1)
    avatar_id: Optional[int] = None
    target_duration_sec: int = Field(ge=1, le=900, default=900)
    global_prompt: Optional[str] = None
    negative_prompt_global: Optional[str] = None
    style_preset: Optional[str] = "cinematic"
    is_mock: bool = False
    video_engine: str = "mock"
    shots: List[ShotCreate] = Field(min_length=1, max_length=20)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    tier: Optional[int] = Field(default=None, ge=1, le=3)
    avatar_id: Optional[int] = None
    global_prompt: Optional[str] = None
    negative_prompt_global: Optional[str] = None
    style_preset: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    tier: int
    avatar_id: Optional[int]
    target_duration_sec: int
    status: str
    final_video_url: Optional[str]
    total_cost_usd: float
    global_prompt: Optional[str]
    negative_prompt_global: Optional[str]
    style_preset: Optional[str]
    is_mock: bool
    video_engine: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    shots: List[ShotResponse] = []


class CostEstimate(BaseModel):
    tier: int
    tier_name: str
    estimated_cost_min: float
    estimated_cost_max: float
    estimated_time_min: int  # minutes
    estimated_time_max: int
    shots_count: int
    clips_per_shot: int
    total_clips: int
    resolution: str
    fps: int
