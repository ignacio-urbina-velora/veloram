"""Avatar schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AvatarCreateFromSelfie(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    # Image will be sent as form-data file


class AvatarCreateFromPrompt(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=10, max_length=1000)
    tier: int = Field(ge=1, le=3, default=1)


class AvatarResponse(BaseModel):
    id: int
    name: str
    source_type: str
    views_count: int
    status: str
    reference_pack_url: Optional[str] = None
    tier_generated: int
    created_at: datetime

    class Config:
        from_attributes = True
