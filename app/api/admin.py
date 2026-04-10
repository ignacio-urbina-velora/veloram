"""Admin API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.affiliate import Affiliate, Referral
from app.models.project import Project, Shot
from app.models.job import Job
from app.schemas.admin import UserAdminResponse, ProjectQueueResponse, AdminReferralResponse
from app.schemas.affiliate import (
    AdminDashboardStats, AffiliateDetailAdmin, AffiliateAdminUpdate, PayoutRequest
)

router = APIRouter(prefix="/admin", tags=["admin"])


async def check_admin(user: User = Depends(get_current_user)):
    """Dependency to check if user is the master admin."""
    if not user.is_admin or user.email != "admin@ai-video.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required (Master Credentials Only)"
        )
    return user


@router.get("/stats", response_model=AdminDashboardStats)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """Get high-level statistics for the admin dashboard."""
    # User counts
    total_users = await db.scalar(select(func.count(User.id)))
    total_affiliates = await db.scalar(select(func.count(Affiliate.id)))
    active_affiliates = await db.scalar(select(func.count(Affiliate.id)).where(Affiliate.is_active == True))
    
    # Revenue & Commissions
    total_revenue = await db.scalar(select(func.sum(Referral.sale_amount))) or 0.0
    total_commissions = await db.scalar(select(func.sum(Referral.commission_amount))) or 0.0
    total_paid_out = await db.scalar(select(func.sum(Affiliate.total_paid_out))) or 0.0
    pending_payouts = await db.scalar(select(func.sum(Affiliate.pending_payout))) or 0.0
    
    # Project stats
    total_projects = await db.scalar(select(func.count(Project.id)))
    projects_completed = await db.scalar(select(func.count(Project.id)).where(Project.status == "completed"))
    projects_queued = await db.scalar(select(func.count(Project.id)).where(Project.status.in_(["queued", "generating", "postprocessing"])))

    return AdminDashboardStats(
        total_users=total_users,
        total_affiliates=total_affiliates,
        active_affiliates=active_affiliates,
        total_revenue=total_revenue,
        total_commissions=total_commissions,
        total_paid_out=total_paid_out,
        pending_payouts=pending_payouts,
        total_projects=total_projects,
        projects_completed=projects_completed,
        projects_queued=projects_queued
    )


@router.get("/users", response_model=List[UserAdminResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """List all users with their details."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get("/queue", response_model=List[ProjectQueueResponse])
async def get_video_queue(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """Get current active video generation queue."""
    result = await db.execute(
        select(Project, User.email)
        .join(User, Project.user_id == User.id)
        .where(Project.status.in_(["queued", "generating", "postprocessing"]))
        .order_by(Project.created_at.asc())
    )
    
    queue = []
    for project, email in result:
        queue.append({
            "id": project.id,
            "user_id": project.user_id,
            "user_email": email,
            "title": project.title,
            "tier": project.tier,
            "status": project.status,
            "created_at": project.created_at
        })
    return queue


@router.get("/referrals", response_model=List[AdminReferralResponse])
async def get_referral_log(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """List all recent referrals across all affiliates."""
    result = await db.execute(
        select(Referral, User.email, Affiliate.code)
        .join(User, Referral.referred_user_id == User.id)
        .join(Affiliate, Referral.affiliate_id == Affiliate.id)
        .order_by(Referral.created_at.desc())
        .limit(50)
    )
    
    referrals = []
    for referral, email, code in result:
        referrals.append({
            "id": referral.id,
            "affiliate_code": code,
            "referred_email": email,
            "sale_amount": referral.sale_amount,
            "commission_amount": referral.commission_amount,
            "created_at": referral.created_at
        })
    return referrals


@router.get("/affiliates", response_model=List[AffiliateDetailAdmin])
async def list_affiliates(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """List all affiliates with their details and performance."""
    result = await db.execute(
        select(Affiliate, User.username, User.email)
        .join(User, Affiliate.user_id == User.id)
    )
    affiliates_data = []
    for affiliate, username, email in result:
        # Get recent referrals for each
        ref_result = await db.execute(
            select(Referral).where(Referral.affiliate_id == affiliate.id).limit(10)
        )
        referrals = ref_result.scalars().all()
        
        aff_dict = {c.name: getattr(affiliate, c.name) for c in Affiliate.__table__.columns}
        aff_dict["username"] = username
        aff_dict["email"] = email
        aff_dict["referrals"] = referrals
        affiliates_data.append(aff_dict)
        
    return affiliates_data


@router.patch("/affiliates/{affiliate_id}", response_model=AffiliateDetailAdmin)
async def update_affiliate(
    affiliate_id: int,
    req: AffiliateAdminUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """Update affiliate settings (rates, status, notes)."""
    affiliate = await db.get(Affiliate, affiliate_id)
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")

    if req.commission_rate is not None:
        affiliate.commission_rate = req.commission_rate
    if req.discount_pct is not None:
        affiliate.discount_pct = req.discount_pct
    if req.is_active is not None:
        affiliate.is_active = req.is_active
    if req.notes is not None:
        affiliate.notes = req.notes

    await db.commit()
    await db.refresh(affiliate)
    
    # Return updated with user info
    user = await db.get(User, affiliate.user_id)
    aff_dict = {c.name: getattr(affiliate, c.name) for c in Affiliate.__table__.columns}
    aff_dict["username"] = user.username
    aff_dict["email"] = user.email
    return aff_dict


@router.post("/affiliates/{affiliate_id}/payout")
async def process_payout(
    affiliate_id: int,
    req: PayoutRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
):
    """Mark commissions as paid and update totals."""
    affiliate = await db.get(Affiliate, affiliate_id)
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")

    if req.amount > affiliate.pending_payout:
        raise HTTPException(status_code=400, detail="Payout amount exceeds pending balance")

    affiliate.pending_payout -= req.amount
    affiliate.total_paid_out += req.amount
    
    # Update referrals status
    # (Simplified: just update totals. In production, we'd mark specific commissions)
    
    await db.commit()
    return {"message": "Payout processed successfully", "new_balance": affiliate.pending_payout}


@router.post("/fix-user")
async def fix_user_credentials(db: AsyncSession = Depends(get_db)):
    """Temporary endpoint to seed/fix credentials for main user accounts.
    This replaces `railway run` seeding which operates on a different ephemeral disk."""
    from app.models.affiliate import Affiliate
    import bcrypt
    
    def hash_pw(pw: str) -> str:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    
    users_to_fix = [
        {"email": "admin@ai-video.com", "username": "admin", "password": "ErosFrame2026!", "credits": 2500.0},
        {"email": "ignaciourbina.96@gmail.com", "username": "ignacio_urbina_admin", "password": "campeon18", "credits": 2500.0},
    ]
    
    results = []
    for u in users_to_fix:
        result = await db.execute(select(User).where(User.email == u["email"]))
        user = result.scalar_one_or_none()
        if user:
            user.hashed_password = hash_pw(u["password"])
            user.is_admin = True
            user.is_active = True
            results.append({"email": u["email"], "action": "updated"})
        else:
            user = User(
                email=u["email"],
                username=u["username"],
                hashed_password=hash_pw(u["password"]),
                credits=u["credits"],
                is_admin=True,
                is_active=True
            )
            db.add(user)
            await db.flush()
            # Create affiliate record
            existing_aff = await db.execute(select(Affiliate).where(Affiliate.user_id == user.id))
            if not existing_aff.scalar_one_or_none():
                aff = Affiliate(user_id=user.id, code=u["username"], is_active=True)
                db.add(aff)
            results.append({"email": u["email"], "action": "created"})
    
    await db.commit()
    return {"status": "ok", "results": results}
