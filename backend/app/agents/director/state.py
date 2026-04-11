from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Shot(TypedDict):
    order: int
    image_prompt: str
    motion_prompt: str
    camera_movement: str
    lighting: str
    mood: str
    dialogue: Optional[str]
    duration_target_sec: float
    negative_prompt: Optional[str]
    status: str  # e.g., "draft", "approved", "rejected"

class DirectorState(TypedDict):
    project_id: str
    idea: str
    duration_target_sec: int
    style: str
    
    # --- DIRECTOR'S BIBLE ---
    style_guide: str      # Visual style guidelines inferred from the idea
    characters: List[Dict[str, str]] # Character profiles
    rules: List[str]      # Cinematic rules to obey
    bible_summary: Optional[str] # Compact summary to avoid token explosion
    bible_version: int    # Versioning for schema migrations
    # ------------------------
    
    shots: List[Shot]
    user_feedback: Optional[str]
    director_critique: Optional[str] # Collaborative feedback or suggestions
    interaction_mode: str            # "chat", "critique", or "planning"
    explanation: Optional[str]       # The current conversational response
    validation_issues: List[str]  # Notes from the technical validator if a shot is impossible
    current_step: str     # Track which node we are in
    
class Character(BaseModel):
    name: str = Field(description="Character's name")
    description: str = Field(description="Physical description and attire")

class DirectorBible(BaseModel):
    """Pydantic model representing the extracted Director's Bible."""
    style_guide: str = Field(description="A highly visual description of the cinematography, lighting, and color grading style.")
    characters: List[Character] = Field(description="List of characters with their physical description and attire.")
    rules: List[str] = Field(description="List of strict cinematic rules or constraints for this specific video based on the idea.")

class ShotModelSchema(BaseModel):
    """Schema for individual shot generation."""
    order: int
    image_prompt: str = Field(description="Highly detailed english prompt for generating the static keyframe image.", default="Cinematic scene, high detail.")
    motion_prompt: str = Field(description="English prompt for the image-to-video model.", default="Slow cinematic movement.")
    camera_movement: str = Field(description="STRICTLY one of: static, pan_left, pan_right, dolly_in, dolly_out, orbit, tilt_up, tilt_down, crane", default="static")
    lighting: str = Field(description="STRICTLY one of: natural, warm_golden, cold_blue, dramatic_shadows, neon, candlelight, sunset, studio", default="natural")
    mood: str = Field(description="STRICTLY one of: neutral, intense, romantic, dramatic, mysterious, playful, seductive, melancholic", default="neutral")
    dialogue: Optional[str] = Field(description="Optional character dialogue in Spanish", default=None)
    negative_prompt: Optional[str] = Field(description="Optional negative prompt", default=None)
    duration_target_sec: Optional[float] = Field(description="Target duration in seconds", default=10.0)
    prompt: Optional[str] = Field(description="Fallback field for image_prompt", default=None)

class ShotSequence(BaseModel):
    explanation: str = Field(description="Brief conversational response or explanation of the planned shots in Spanish.")
    shots: List[ShotModelSchema]
