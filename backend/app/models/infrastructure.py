"""Infrastructure fund model to track platform costs."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base


class InfrastructureFund(Base):
    """Tracks the total pool of money gathered from sales to cover GPU/Voice costs."""
    __tablename__ = "infrastructure_funds"

    id = Column(Integer, primary_key=True, index=True)
    
    # Total accumulated from sales (e.g., 20% of every sale)
    total_accrued = Column(Float, default=0.0)
    
    # Total spent manually/automatically on Vast.ai / ElevenLabs
    total_spent = Column(Float, default=0.0)
    
    # Current theoretical balance (accrued - spent)
    current_balance = Column(Float, default=0.0)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)


class InfrastructureLog(Base):
    """Logs every transaction (accrual or expense)."""
    __tablename__ = "infrastructure_logs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20))  # 'accrual' (from sale) or 'expense' (manual top-up)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
