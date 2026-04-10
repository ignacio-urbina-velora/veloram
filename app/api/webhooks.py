from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models.affiliate import Affiliate, Referral
from app.models.user import User
from app.models.infrastructure import InfrastructureFund, InfrastructureLog

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Fixed commission table based on CCBill pricing requirements
COMMISSION_TABLE = {
    # Tier 1 - Quick (LTX-2 fp8)
    "tier1_basic": {"price": 50, "commission": 4},
    "tier1_medium": {"price": 85, "commission": 8},
    "tier1_full": {"price": 150, "commission": 15},
    
    # Tier 2 - Pro (Wan 2.2 FP8)
    "tier2_basic": {"price": 90, "commission": 8},
    "tier2_medium": {"price": 159, "commission": 13},
    "tier2_full": {"price": 299, "commission": 30},
    
    # Tier 3 - Cinematic Ultra (HunyuanVideo bf16)
    "tier3_basic": {"price": 350, "commission": 35},
    "tier3_medium": {"price": 680, "commission": 68},
    "tier3_full": {"price": 1350, "commission": 135},
}

@router.post("/ccbill")
async def ccbill_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    CCBill payment webhook handler.
    Expects form data or JSON containing:
    - clientAccnum, clientSubacc
    - eventType (e.g. NewSaleSuccess)
    - custom_plan_id (e.g. 'tier1_basic')
    - custom_user_id
    - custom_ref_code (optional)
    """
    payload = await request.form()
    # In a real scenario, you verify the CCBill signature hash here to prevent spoofing.
    
    # Check if this is an approved sale
    event_type = payload.get("eventType")
    if event_type != "NewSaleSuccess":
        return {"status": "ignored", "reason": "Not a new sale"}
        
    plan_id = payload.get("custom_plan_id")
    user_id = payload.get("custom_user_id")
    ref_code = payload.get("custom_ref_code")
    
    if not plan_id or plan_id not in COMMISSION_TABLE:
        return {"status": "error", "message": "Invalid or missing plan ID"}
        
    if ref_code:
        # Check if affiliate code exists
        result = await db.execute(select(Affiliate).where(Affiliate.code == ref_code, Affiliate.is_active == True))
        affiliate = result.scalar_one_or_none()
        
        if affiliate:
            # Calculate fixed commission from the table
            plan_details = COMMISSION_TABLE[plan_id]
            sale_amount = plan_details["price"]
            commission_amount = plan_details["commission"]
            
            # Record the referral
            new_referral = Referral(
                affiliate_id=affiliate.id,
                referred_user_id=int(user_id) if user_id else None,
                code_used=ref_code,
                sale_amount=sale_amount,
                commission_amount=commission_amount,
                commission_paid=False,
            )
            db.add(new_referral)
            
            # Update affiliate totals
            affiliate.total_referrals += 1
            affiliate.total_earnings += commission_amount
            affiliate.pending_payout += commission_amount
            
            await db.commit()
            
    # --- INFRASTRUCTURE COST ALLOCATION ---
    # Take 20% of the sale to cover GPU (Vast.ai) and Voice (ElevenLabs) costs.
    plan_details = COMMISSION_TABLE[plan_id]
    sale_amount = plan_details["price"]
    infra_allocation = sale_amount * 0.20  # 20% allocation
    
    # Get or create the global fund record
    res = await db.execute(select(InfrastructureFund))
    fund = res.scalar_one_or_none()
    
    if not fund:
        fund = InfrastructureFund(total_accrued=0, total_spent=0, current_balance=0)
        db.add(fund)
        await db.flush()
    
    # Update fund
    fund.total_accrued += infra_allocation
    fund.current_balance += infra_allocation
    
    # Log the accrual
    log = InfrastructureLog(
        type="accrual",
        amount=infra_allocation,
        description=f"Fund allocation (20%) from {plan_id} sale by user {user_id}"
    )
    db.add(log)
    
    await db.commit()
    # ---------------------------------------
            
    # Add credits/specs to user account here (omitted for brevity)
    
    return {"status": "success"}
