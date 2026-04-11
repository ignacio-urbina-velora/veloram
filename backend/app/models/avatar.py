"""Avatar model for face reference packs."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from app.database import Base


class Avatar(Base):
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)

    # Source: "selfie" or "prompt"
    source_type = Column(String(20), nullable=False, default="selfie")
    source_data = Column(Text, nullable=True)  # prompt text or original image URL

    # Reference pack (generated views)
    reference_pack_url = Column(String(500), nullable=True)  # S3 URL to zip
    views_count = Column(Integer, default=8)  # 8-16 depending on tier
    embedding_path = Column(String(500), nullable=True)  # Path to face embedding

    # Metadata
    tier_generated = Column(Integer, default=1)  # Tier used for generation
    metadata_json = Column(JSON, nullable=True)  # Extra info (angles, expressions, etc.)

    status = Column(String(20), default="pending")  # pending, processing, ready, failed
    created_at = Column(DateTime, default=datetime.utcnow)
