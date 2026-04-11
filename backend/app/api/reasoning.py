"""Reasoning API — connects to Flowise Agentflow (Director Brain) and fallback to Modal Llama 3."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.api.deps import get_current_user
from app.models.user import User
from app.services.flowise_service import flowise_service
from app.services.reasoning_service import reasoning_service

router = APIRouter(prefix="/reasoning", tags=["reasoning"])


class ReasoningRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    project_id: Optional[int] = None


class PlanVideoRequest(BaseModel):
    idea: str
    duration_minutes: int = 15
    style: str = "cinematic"


class RefineRequest(BaseModel):
    shot_prompt: str
    context: str = ""


class CoherenceRequest(BaseModel):
    shots: List[Dict[str, Any]]


class ReasoningResponse(BaseModel):
    response: str


class PlanResponse(BaseModel):
    plan: Optional[Dict[str, Any]] = None
    raw_response: str


class CoherenceResponse(BaseModel):
    coherence_score: int
    issues: List[str] = []
    suggestions: List[str] = []
    overall: str = ""


# --- Simple Chat ---

@router.post("", response_model=ReasoningResponse)
async def get_ai_reasoning(
    req: ReasoningRequest,
    user: User = Depends(get_current_user),
):
    """Chat with the AI reasoning agent (Flowise or fallback to Modal)."""
    # Try Flowise first
    flowise_ok = await flowise_service.health_check()
    if flowise_ok and flowise_service.chatflow_id:
        try:
            result = await flowise_service.send_message(req.prompt)
            return ReasoningResponse(response=result.get("text", result.get("response", "")))
        except Exception:
            pass

    # Fallback to Modal Llama 3
    result = await reasoning_service.get_reasoning(req.prompt, req.system_prompt)
    return ReasoningResponse(response=result)


# --- Director Brain: Video Planning ---

@router.post("/plan", response_model=PlanResponse)
async def plan_video(
    req: PlanVideoRequest,
    user: User = Depends(get_current_user),
):
    """Use the Director Agentflow to plan a full video."""
    flowise_ok = await flowise_service.health_check()
    if flowise_ok and flowise_service.chatflow_id:
        try:
            result = await flowise_service.plan_video(
                idea=req.idea,
                duration_minutes=req.duration_minutes,
                style=req.style,
            )
            return PlanResponse(**result)
        except Exception as e:
            # Fall through to fallback
            pass

    # Fallback: use Modal Llama 3 directly
    planning_prompt = f"""Planifica un video de {req.duration_minutes} minutos con esta idea: "{req.idea}"
Estilo: {req.style}. Divide en 6-12 shots. Para cada shot: prompt visual, cámara, iluminación, mood, duración. Responde en JSON."""

    result = await reasoning_service.get_reasoning(planning_prompt)
    return PlanResponse(plan=None, raw_response=result)


# --- Refine Shot ---

@router.post("/refine", response_model=ReasoningResponse)
async def refine_shot(
    req: RefineRequest,
    user: User = Depends(get_current_user),
):
    """Refine a shot prompt for better visual quality."""
    flowise_ok = await flowise_service.health_check()
    if flowise_ok and flowise_service.chatflow_id:
        try:
            result = await flowise_service.refine_shot(req.shot_prompt, req.context)
            return ReasoningResponse(response=result)
        except Exception:
            pass

    result = await reasoning_service.get_reasoning(
        f"Mejora este prompt de shot: {req.shot_prompt}. Contexto: {req.context}",
        "Eres un experto en prompts para generación de video IA. Responde solo con el prompt mejorado."
    )
    return ReasoningResponse(response=result)


# --- Coherence Check ---

@router.post("/coherence", response_model=CoherenceResponse)
async def check_coherence(
    req: CoherenceRequest,
    user: User = Depends(get_current_user),
):
    """Verify coherence between shots."""
    flowise_ok = await flowise_service.health_check()
    if flowise_ok and flowise_service.chatflow_id:
        try:
            result = await flowise_service.check_coherence(req.shots)
            return CoherenceResponse(**result)
        except Exception:
            pass

    shots_text = "\n".join([f"Shot {s.get('order', i+1)}: {s.get('prompt', '')}" for i, s in enumerate(req.shots)])
    result = await reasoning_service.get_reasoning(
        f"Analiza coherencia: {shots_text}",
        "Evalúa coherencia narrativa. Responde con score 0-100 y sugerencias."
    )
    return CoherenceResponse(coherence_score=-1, overall=result)


# --- Flowise Configuration ---

@router.post("/configure")
async def configure_flowise(
    chatflow_id: str,
    user: User = Depends(get_current_user),
):
    """Set the Flowise chatflow ID for the Director Brain."""
    if not user.is_admin or user.email != "admin@ai-video.com":
        raise HTTPException(status_code=403, detail="Solo el administrador puede configurar Flowise")
    
    flowise_service.set_chatflow(chatflow_id)
    return {"status": "ok", "chatflow_id": chatflow_id}


@router.get("/status")
async def reasoning_status(user: User = Depends(get_current_user)):
    """Check the status of the reasoning services."""
    flowise_ok = await flowise_service.health_check()
    return {
        "flowise": {
            "available": flowise_ok,
            "chatflow_configured": bool(flowise_service.chatflow_id),
            "url": flowise_service.base_url,
        },
        "modal_llama3": {
            "available": True,  # Always available as fallback
        },
    }
