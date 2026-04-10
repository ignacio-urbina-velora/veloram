"""Job model for tracking GPU tasks."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.database import Base


class Job(Base):
    """Tracks individual GPU tasks (avatar gen, clip gen, post-processing)."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    shot_id = Column(Integer, ForeignKey("shots.id"), nullable=True)

    # Type: avatar_gen, clip_gen, postprocess
    job_type = Column(String(30), nullable=False)

    # vast.ai instance tracking
    vast_instance_id = Column(String(100), nullable=True)
    vast_instance_ip = Column(String(50), nullable=True)
    gpu_type = Column(String(50), nullable=True)

    # Status
    status = Column(String(20), default="pending")
    # pending → renting_gpu → deploying → running → downloading → done → failed

    progress_pct = Column(Float, default=0.0)  # 0-100
    error = Column(Text, nullable=True)

    # Cost
    cost_usd = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
