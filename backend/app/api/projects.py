"""Project & Shot endpoints – the multi-shot director API."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import Project, Shot
from app.models.affiliate import Affiliate, Referral
from app.services.generation_service import generation_service
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    ShotCreate, ShotUpdate, ShotResponse, CostEstimate,
    PromptRefineRequest, PromptRefineResponse
)
from app.config import TierConfig

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectDetailResponse, status_code=201)
async def create_project(
    req: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project with shots."""
    tier_cfg = TierConfig.get(req.tier)
    shots_min, shots_max = tier_cfg["shots_range"]

    if len(req.shots) < shots_min or len(req.shots) > shots_max:
        raise HTTPException(
            status_code=400,
            detail=f"Tier {req.tier} requires {shots_min}-{shots_max} shots"
        )

    project = Project(
        user_id=user.id,
        title=req.title,
        tier=req.tier,
        avatar_id=req.avatar_id,
        target_duration_sec=req.target_duration_sec,
        is_mock=1 if req.is_mock else 0,
    )
    db.add(project)
    await db.flush()

    # Create shots
    shots = []
    for i, shot_data in enumerate(req.shots):
        shot = Shot(
            project_id=project.id,
            order=i,
            prompt=shot_data.prompt,
            camera_movement=shot_data.camera_movement,
            lighting=shot_data.lighting,
            mood=shot_data.mood,
            dialogue=shot_data.dialogue,
            negative_prompt=shot_data.negative_prompt,
            duration_target_sec=shot_data.duration_target_sec,
        )
        db.add(shot)
        shots.append(shot)

    await db.flush()
    for shot in shots:
        await db.refresh(shot)
    await db.refresh(project)

    return ProjectDetailResponse(
        **{c.name: getattr(project, c.name) for c in Project.__table__.columns},
        shots=[ShotResponse.model_validate(s) for s in shots],
    )


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user.id)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Shot).where(Shot.project_id == project_id).order_by(Shot.order)
    )
    shots = result.scalars().all()

    return ProjectDetailResponse(
        **{c.name: getattr(project, c.name) for c in Project.__table__.columns},
        shots=[ShotResponse.model_validate(s) for s in shots],
    )


@router.put("/{project_id}/shots/{shot_id}", response_model=ShotResponse)
async def update_shot(
    project_id: int,
    shot_id: int,
    req: ShotUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a shot's director controls (prompt, camera, lighting, etc.)."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    shot = await db.get(Shot, shot_id)
    if not shot or shot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Shot not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(shot, field, value)

    await db.flush()
    await db.refresh(shot)
    return shot


@router.post("/{project_id}/shots", response_model=ShotResponse, status_code=201)
async def add_shot(
    project_id: int,
    req: ShotCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new shot to a project."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get current max order
    result = await db.execute(
        select(Shot.order).where(Shot.project_id == project_id).order_by(Shot.order.desc())
    )
    max_order = result.scalar() or -1

    shot = Shot(
        project_id=project_id,
        order=max_order + 1,
        prompt=req.prompt,
        camera_movement=req.camera_movement,
        lighting=req.lighting,
        mood=req.mood,
        dialogue=req.dialogue,
        negative_prompt=req.negative_prompt,
        duration_target_sec=req.duration_target_sec,
    )
    db.add(shot)
    await db.flush()
    await db.refresh(shot)
    return shot


@router.delete("/{project_id}/shots/{shot_id}", status_code=204)
async def delete_shot(
    project_id: int,
    shot_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    shot = await db.get(Shot, shot_id)
    if not shot or shot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Shot not found")

    await db.delete(shot)
    await db.commit()

@router.post("/refine-prompt", response_model=PromptRefineResponse)
async def refine_prompt(req: PromptRefineRequest):
    """Refine a prompt using AI (placeholder)."""
    # In a real app, this would call GPT-4o or a specialized video-prompt LLM
    refined = f"{req.prompt}, ultra-realistic, cinematic lighting, highly detailed, 8k, masterpiece"
    if req.context:
        refined = f"{req.context}. {refined}"
    return {"refined_prompt": refined}

@router.post("/{project_id}/shots/{shot_id}/generate", status_code=202)
async def generate_single_shot(
    project_id: int,
    shot_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a single shot for preview/refinement."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    shot = await db.get(Shot, shot_id)
    if not shot or shot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Shot not found")

    shot.status = "queued"
    await db.flush()
    await db.commit()

    # Dispatch to generation service (Background)
    # Background task wrapper to handle session
    background_tasks.add_task(generation_service.generate_shot, db, project_id, shot_id)
    
    return {"message": "Shot generation started", "shot_id": shot_id}


@router.post("/{project_id}/generate", status_code=202)
async def start_generation(
    project_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start video generation for a project. Returns immediately."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status not in ("draft", "failed"):
        raise HTTPException(status_code=400, detail=f"Cannot generate, status={project.status}")

    # Calculate estimated cost per video
    tier_cfg = TierConfig.get(project.tier)
    # Average cost per video = basic package credits / number of videos
    basic_pkg = tier_cfg["packages"]["basic"]
    estimated_cost = basic_pkg["credits"] / basic_pkg["videos"]
    
    is_master_admin = user.is_admin and user.email == "admin@ai-video.com"
    if not is_master_admin:
        try:
            from app.services.billing_service import billing_service
            await billing_service.deduct_credits(
                db, 
                user.id, 
                estimated_cost, 
                f"Generación de Video (Tier {project.tier})", 
                "project", 
                project.id
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=402, detail=str(e))

    # Start async generation
    project.status = "queued"
    await db.flush()
    await db.commit()

    # Background task wrapper to handle session
    async def run_gen():
        async with async_session() as session:
            try:
                if project.is_mock:
                    await generation_service._generate_mock_project(session, project_id)
                else:
                    await generation_service.generate_project(session, project_id)
                await session.commit()
            except Exception:
                await session.rollback()

    background_tasks.add_task(run_gen)

    return {"message": "Generation started", "project_id": project_id}


@router.post("/{project_id}/reset", status_code=200)
async def reset_project_status(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset a stuck project back to draft status."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status not in ("queued", "generating", "postprocessing", "failed"):
        raise HTTPException(status_code=400, detail=f"Project is not in a stuck state (current: {project.status})")

    project.status = "draft"
    await db.flush()
    await db.commit()
    
    return {"message": "Project reset to draft", "project_id": project_id}

@router.post("/{project_id}/generate-keyframes", status_code=202)
async def generate_keyframes(
    project_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate high-quality keyframes for all pending shots."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    from app.services.generation_service import generation_service
    from app.database import async_session
    
    async def run_keyframes():
        async with async_session() as session:
            await generation_service.generate_keyframes(session, project_id)
    
    background_tasks.add_task(run_keyframes)
    return {"message": "Keyframe generation started", "project_id": project_id}

@router.get("/estimate/{tier}", response_model=CostEstimate)
async def estimate_cost(tier: int, shots_count: int = 5):
    """Get cost/time estimate for a tier."""
    if tier not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Tier must be 1, 2, or 3")

    cfg = TierConfig.get(tier)
    clip_min, clip_max = cfg["clip_duration_range"]
    clips_per_shot = 15  # Average clips per shot to fill 15 min

    return CostEstimate(
        tier=tier,
        tier_name=cfg["name"],
        estimated_cost_min=cfg["cost_range"][0],
        estimated_cost_max=cfg["cost_range"][1],
        estimated_time_min=cfg["wait_minutes"][0],
        estimated_time_max=cfg["wait_minutes"][1],
        shots_count=shots_count,
        clips_per_shot=clips_per_shot,
        total_clips=shots_count * clips_per_shot,
        resolution=cfg["resolution"],
        fps=cfg["fps"],
    )
@router.post("/buy-package")
async def buy_package(
    tier: int,
    package_id: str,
    discount_code: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Simulate buying a video package and updating credits."""
    tier_cfg = TierConfig.TIERS.get(tier)
    if not tier_cfg:
        raise HTTPException(status_code=400, detail="Tier inválido")
    
    package = tier_cfg["packages"].get(package_id)
    if not package:
        raise HTTPException(status_code=400, detail="Paquete inválido")

    price = float(package["price"])
    discount_amount = 0.0
    affiliate_id = None
    commission_amount = 0.0

    # Handle Discount Code
    if discount_code:
        aff_result = await db.execute(
            select(Affiliate).where(Affiliate.code == discount_code, Affiliate.is_active == True)
        )
        affiliate = aff_result.scalar_one_or_none()
        
        if affiliate:
            affiliate_id = affiliate.id
            discount_amount = price * (affiliate.discount_pct / 100)
            price -= discount_amount
            commission_amount = price * (affiliate.commission_rate / 100)
            
            # Record Referral
            referral = Referral(
                affiliate_id=affiliate_id,
                referred_user_id=user.id,
                code_used=discount_code,
                sale_amount=float(package["price"]),
                discount_amount=discount_amount,
                commission_amount=commission_amount
            )
            db.add(referral)
            
            # Update Affiliate Totals
            affiliate.total_referrals += 1
            affiliate.total_earnings += commission_amount
            affiliate.pending_payout += commission_amount

    # Update User Credits (1 credit = 1 video)
    user.credits += package["videos"]
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": f"¡Compra exitosa! Has recibido {package['videos']} créditos.",
        "new_credits": user.credits,
        "discount_applied": discount_amount,
        "final_price": price
    }
