import httpx
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.director_service import director_service
from app.services.billing_service import billing_service
from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User

router = APIRouter()

class PlanRequest(BaseModel):
    idea: str
    target_duration_sec: int = 15
    style: str = "cinematic"
    project_id: Optional[str] = None # Optional for draft mode

class ShotModel(BaseModel):
    order: int
    prompt: str
    camera_movement: str
    lighting: str
    mood: str
    dialogue: Optional[str] = None
    negative_prompt: Optional[str] = None
    duration_target_sec: float

class RefineRequest(BaseModel):
    shot: ShotModel
    feedback: str

class RefineSequenceRequest(BaseModel):
    shots: List[ShotModel]
    feedback: str
    project_id: Optional[str] = None

# Cost per LLM usage (Director Brain)
DIRECTOR_COST_CREDITS = 0.05

@router.post("/plan")
async def plan_video(
    request: PlanRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await billing_service.deduct_credits(db, user.id, DIRECTOR_COST_CREDITS, "Director AI: Generar Plan")
        result = await director_service.plan_video(
            request.idea, 
            request.target_duration_sec, 
            request.style,
            project_id=request.project_id or f"temp_{user.id}",
            db=db
        )
        
        # Trigger keyframe generation in background with the ACTUAL ID (if it's successfully a number)
        actual_project_id = result.get("project_id")
        print(f"[DirectorAPI] Plan finished. Found project_id in result: {actual_project_id}")
        
        if actual_project_id and str(actual_project_id).isdigit():
            try:
                pid = int(actual_project_id)
                async def run_keyframes():
                    from app.database import async_session
                    from app.services.generation_service import generation_service
                    async with async_session() as session:
                        print(f"[DEBUG-WORKFLOW] >>> EXECUTING keyframe generation for project {pid}")
                        await generation_service.generate_keyframes(session, pid)
                        print(f"[DEBUG-WORKFLOW] <<< FINISHED execution for project {pid}")
                
                print(f"[DirectorAPI] Registering BACKGROUND TASK for project {pid}")
                background_tasks.add_task(run_keyframes)
            except (ValueError, TypeError) as e:
                print(f"[DirectorAPI] ERROR parsing project_id for background task: {e}")
        else:
            print(f"[DirectorAPI] WARNING: Skipping keyframes generation trigger. project_id {actual_project_id} is invalid.")

        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refine-sequence")
async def refine_sequence(
    request: RefineSequenceRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Business logic: refine the sequence using LangGraph
        result = await director_service.refine_sequence(
            request.shots,
            request.feedback,
            project_id=request.project_id,
            db=db
        )
        
        project_id_str = result.get("project_id")
        if project_id_str:
            try:
                pid = int(project_id_str)
                async def run_keyframes():
                    from app.database import async_session
                    from app.services.generation_service import generation_service
                    async with async_session() as session:
                        await generation_service.generate_keyframes(session, pid)
                background_tasks.add_task(run_keyframes)
            except (ValueError, TypeError):
                pass

        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    try:
        # We assume True if the service instance is initialized
        # In a real scenario we'd ping the Modal endpoint
        return {"status": "online", "model": director_service.model}
    except Exception:
        pass
    return {"status": "offline"}
