"""Affiliate model for referral/commission tracking."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
)
from app.database import Base


class Affiliate(Base):
    """An affiliate who earns commissions by referring users."""
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Affiliate code (used by customers for discounts)
    code = Column(String(50), unique=True, nullable=False, index=True)

    # Commission rate (percentage of sale)
    commission_rate = Column(Float, default=15.0)  # 15% default

    # Discount the customer gets when using the code
    discount_pct = Column(Float, default=10.0)  # 10% discount for customer

    # Stats (denormalized for fast queries)
    total_referrals = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    total_paid_out = Column(Float, default=0.0)
    pending_payout = Column(Float, default=0.0)

    # Status
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)  # Admin notes

    # Payment info
    payment_method = Column(String(50), nullable=True)  # paypal, crypto, bank
    payment_details = Column(Text, nullable=True)  # email, wallet, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Referral(Base):
    """Tracks each time an affiliate code is used."""
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False, index=True)
    referred_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # The code used
    code_used = Column(String(50), nullable=False)

    # Revenue generated
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    sale_amount = Column(Float, default=0.0)  # Total sale before discount
    discount_amount = Column(Float, default=0.0)  # Discount given to customer
    commission_amount = Column(Float, default=0.0)  # Commission earned by affiliate
    commission_paid = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
