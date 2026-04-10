from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserAdminResponse(BaseModel):
    id: int
    email: str
    username: str
    credits: float
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectQueueResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    title: str
    tier: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AdminReferralResponse(BaseModel):
    id: int
    affiliate_code: str
    referred_email: str
    sale_amount: float
    commission_amount: float
    created_at: datetime

    class Config:
        from_attributes = True
