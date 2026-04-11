"""Job tracking & SSE progress endpoints."""

import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.project import Project, Shot
from app.schemas.job import JobResponse, ProjectProgress

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/project/{project_id}", response_model=list[JobResponse])
async def list_project_jobs(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all jobs for a project."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Job).where(Job.project_id == project_id).order_by(Job.created_at)
    )
    return result.scalars().all()


@router.get("/project/{project_id}/progress")
async def project_progress_sse(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SSE endpoint for real-time project progress."""
    project = await db.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    async def event_stream():
        while True:
            # Re-query progress
            async with db.begin():
                proj = await db.get(Project, project_id)

                # Count shots
                total_shots = await db.scalar(
                    select(func.count()).where(Shot.project_id == project_id)
                )
                done_shots = await db.scalar(
                    select(func.count()).where(
                        Shot.project_id == project_id,
                        Shot.status == "done",
                    )
                )

                # Aggregate job progress
                avg_progress = await db.scalar(
                    select(func.avg(Job.progress_pct)).where(
                        Job.project_id == project_id
                    )
                ) or 0

                total_cost = await db.scalar(
                    select(func.sum(Job.cost_usd)).where(
                        Job.project_id == project_id
                    )
                ) or 0

                progress = ProjectProgress(
                    project_id=project_id,
                    status=proj.status,
                    overall_progress=round(avg_progress, 1),
                    shots_completed=done_shots or 0,
                    shots_total=total_shots or 0,
                    current_step=_status_to_step(proj.status),
                    total_cost_so_far=round(total_cost, 2),
                )

                data = json.dumps(progress.model_dump())
                yield f"data: {data}\n\n"

                # Stop if completed or failed
                if proj.status in ("completed", "failed"):
                    break

            await asyncio.sleep(3)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


def _status_to_step(status: str) -> str:
    steps = {
        "draft": "Waiting to start",
        "queued": "Queued for generation",
        "generating": "Generating video clips on GPU",
        "postprocessing": "Stitching clips & applying effects",
        "completed": "Video ready!",
        "failed": "Generation failed",
    }
    return steps.get(status, status)
