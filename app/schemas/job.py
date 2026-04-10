"""Job schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobResponse(BaseModel):
    id: int
    project_id: int
    shot_id: Optional[int]
    job_type: str
    status: str
    progress_pct: float
    gpu_type: Optional[str]
    cost_usd: float
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectProgress(BaseModel):
    """Aggregated progress for SSE streaming."""
    project_id: int
    status: str
    overall_progress: float  # 0-100
    shots_completed: int
    shots_total: int
    current_step: str  # Description of what's happening
    estimated_remaining_sec: Optional[int] = None
    total_cost_so_far: float = 0.0
