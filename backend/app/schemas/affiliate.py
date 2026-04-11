"""Affiliate schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Affiliate Registration ---

# --- Referral ---

class ApplyCodeRequest(BaseModel):
    """Customer applies a discount code."""
    code: str = Field(min_length=3, max_length=50)


class ApplyCodeResponse(BaseModel):
    valid: bool
    discount_pct: float = 0.0
    message: str = ""


class ReferralResponse(BaseModel):
    id: int
    referred_user_id: int
    code_used: str
    sale_amount: float
    discount_amount: float
    commission_amount: float
    commission_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Affiliate ---

class AffiliateApply(BaseModel):
    """User applies to become an affiliate."""
    code: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    payment_method: Optional[str] = None
    payment_details: Optional[str] = None


class AffiliateResponse(BaseModel):
    id: int
    user_id: int
    code: str
    commission_rate: float
    discount_pct: float
    total_referrals: int
    total_earnings: float
    total_paid_out: float
    pending_payout: float
    is_active: bool
    created_at: datetime
    referrals: Optional[List[ReferralResponse]] = []

    class Config:
        from_attributes = True


class AffiliateDetailAdmin(AffiliateResponse):
    """Extended response for admin view."""
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    payment_details: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    referrals: List[ReferralResponse] = []


# --- Admin Stats ---

class AdminDashboardStats(BaseModel):
    total_users: int
    total_affiliates: int
    active_affiliates: int
    total_revenue: float
    total_commissions: float
    total_paid_out: float
    pending_payouts: float
    total_projects: int
    projects_completed: int
    projects_queued: int


class AffiliateAdminUpdate(BaseModel):
    """Admin updates to an affiliate."""
    commission_rate: Optional[float] = Field(default=None, ge=0, le=100)
    discount_pct: Optional[float] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class PayoutRequest(BaseModel):
    """Mark commission as paid."""
    amount: float = Field(gt=0)
    notes: Optional[str] = None
