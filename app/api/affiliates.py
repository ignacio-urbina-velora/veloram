"""Affiliate public API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.affiliate import Affiliate, Referral
from app.schemas.affiliate import (
    AffiliateApply, AffiliateResponse, ApplyCodeRequest, ApplyCodeResponse, ReferralResponse
)

router = APIRouter(prefix="/affiliates", tags=["affiliates"])


@router.post("/apply", response_model=AffiliateResponse)
async def apply_to_be_affiliate(
    req: AffiliateApply,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If code is 'auto', use username
    code = req.code
    if code == "auto":
        code = user.username.lower().replace(" ", "_")

    # Check if already an affiliate
    existing = await db.execute(select(Affiliate).where(Affiliate.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already an affiliate")

    # Check if code is taken
    code_check = await db.execute(select(Affiliate).where(Affiliate.code == code))
    if code_check.scalar_one_or_none():
        # If auto-generated code is taken, append small random hash or id
        code = f"{code}_{user.id}"

    new_affiliate = Affiliate(
        user_id=user.id,
        code=code,
        payment_method=req.payment_method,
        payment_details=req.payment_details
    )
    db.add(new_affiliate)
    await db.commit()
    await db.refresh(new_affiliate)
    return new_affiliate


@router.get("/me", response_model=AffiliateResponse)
async def get_my_affiliate_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get stats for the current user's affiliate account."""
    result = await db.execute(select(Affiliate).where(Affiliate.user_id == user.id))
    affiliate = result.scalar_one_or_none()
    if not affiliate:
        raise HTTPException(status_code=404, detail="User is not an affiliate")
    
    # Include referrals for the dashboard
    ref_result = await db.execute(
        select(Referral).where(Referral.affiliate_id == affiliate.id).order_by(Referral.created_at.desc())
    )
    referrals = ref_result.scalars().all()
    
    # We dynamically add referrals to the response
    # (Note: In Pydantic v2/from_attributes, we can just attach it to the object)
    affiliate.referrals = referrals
    return affiliate


@router.post("/check-code", response_model=ApplyCodeResponse)
async def check_discount_code(
    req: ApplyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Check if a discount code is valid and get the discount percentage."""
    result = await db.execute(select(Affiliate).where(Affiliate.code == req.code, Affiliate.is_active == True))
    affiliate = result.scalar_one_or_none()
    
    if not affiliate:
        return ApplyCodeResponse(valid=False, message="Código inválido o expirado")
        
    return ApplyCodeResponse(
        valid=True,
        discount_pct=affiliate.discount_pct,
        message=f"¡Código aplicado! {affiliate.discount_pct}% de descuento"
    )


@router.get("/my-referrals", response_model=List[ReferralResponse])
async def get_my_referrals(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of referrals for the current affiliate."""
    aff_result = await db.execute(select(Affiliate).where(Affiliate.user_id == user.id))
    affiliate = aff_result.scalar_one_or_none()
    if not affiliate:
        raise HTTPException(status_code=404, detail="User is not an affiliate")

    ref_result = await db.execute(
        select(Referral).where(Referral.affiliate_id == affiliate.id).order_by(Referral.created_at.desc())
    )
    return ref_result.scalars().all()
