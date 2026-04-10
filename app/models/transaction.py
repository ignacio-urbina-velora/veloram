"""Transaction model for the billing and credits system."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    amount = Column(Float, nullable=False) # Positive for recharges, Negative for usage
    description = Column(String(255), nullable=False)
    
    related_entity_type = Column(String(50), nullable=True) # e.g. "project", "shot", "plan_purchase"
    related_entity_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
