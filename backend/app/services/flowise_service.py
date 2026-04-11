"""Flowise API Service — communicates with the Flowise Agentflow to act as the 'Director Brain'.

The Flowise agent:
1. Takes a user's video idea
2. Divides it into 6-12 coherent shots
3. Generates detailed prompts per shot (camera, lighting, mood, dialogue)
4. Verifies narrative coherence between shots
5. Exports structured JSON for ComfyUI generation
"""

import httpx
import logging
import json
from typing import Optional, List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class FlowiseService:
    """Client for the Flowise Agentflow API."""

    def __init__(self, base_url: str = settings.FLOWISE_BASE_URL):
        self.base_url = base_url
        self.api_key = settings.FLOWISE_API_KEY
        self.chatflow_id: Optional[str] = settings.FLOWISE_CHATFLOW_ID

    def set_chatflow(self, chatflow_id: str):
        """Set the active chatflow/agentflow ID."""
        self.chatflow_id = chatflow_id

    async def send_message(
        self,
        message: str,
        chatflow_id: Optional[str] = None,
        session_id: Optional[str] = None,
        override_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a message to the Flowise Agentflow and return the response."""
        flow_id = chatflow_id or self.chatflow_id
        if not flow_id:
            logger.warning("No chatflow_id configured. Calls will fail.")
            # We don't raise error here to allow initialization without ID
            return {"text": "No chatflow ID configured."}

        url = f"{self.base_url}/api/v1/prediction/{flow_id}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {"question": message}
        if session_id:
            payload["overrideConfig"] = {"sessionId": session_id}
        if override_config:
            payload.setdefault("overrideConfig", {}).update(override_config)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Flowise API error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Flowise API error: {e.response.status_code}")
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Flowise at {self.base_url}")
            raise RuntimeError(f"Flowise service unavailable at {self.base_url}")

    async def plan_video(
        self,
        idea: str,
        duration_minutes: int = 15,
        style: str = "cinematic",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Use the Director Agentflow to plan a full video from an idea.
        
        Returns structured shot plan with prompts, camera, lighting, mood.
        """
        planning_prompt = f"""Planifica un video de {duration_minutes} minutos con esta idea:

"{idea}"

Estilo visual: {style}

Divide en 6-12 shots coherentes. Para cada shot genera:
1. Prompt visual detallado (sujeto, entorno, iluminación, atmósfera)
2. Movimiento de cámara (dolly-in, pan left, orbit, tilt up, crane, etc.)
3. Iluminación (natural, neon, volumetric, cinematic, golden hour)
4. Mood (dramatic, mysterious, energetic, romantic, melancholic)
5. Duración en segundos
6. Notas de continuidad con el shot anterior

Responde en formato JSON con esta estructura:
{{
  "title": "título del proyecto",
  "total_shots": N,
  "shots": [
    {{
      "order": 1,
      "prompt": "...",
      "camera_movement": "...",
      "lighting": "...",
      "mood": "...",
      "duration_sec": N,
      "continuity_note": "..."
    }}
  ],
  "coherence_score": 0-100,
  "global_style_notes": "..."
}}"""

        result = await self.send_message(planning_prompt, session_id=session_id)
        
        # Try to extract JSON from the response
        response_text = result.get("text", result.get("response", ""))
        try:
            # Look for JSON block in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                plan = json.loads(response_text[json_start:json_end])
                return {"plan": plan, "raw_response": response_text}
        except json.JSONDecodeError:
            pass

        return {"plan": None, "raw_response": response_text}

    async def refine_shot(
        self,
        shot_prompt: str,
        context: str = "",
        session_id: Optional[str] = None,
    ) -> str:
        """Refine a single shot's prompt for maximum visual quality."""
        refine_prompt = f"""Mejora este prompt de shot para generación de video con IA.
Hazlo más detallado y cinematográfico, manteniendo coherencia.

Prompt actual: {shot_prompt}
Contexto del proyecto: {context}

Responde SOLO con el prompt mejorado, sin explicaciones."""

        result = await self.send_message(refine_prompt, session_id=session_id)
        return result.get("text", result.get("response", shot_prompt))

    async def check_coherence(
        self,
        shots: List[Dict[str, str]],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Verify narrative coherence between shots."""
        shots_text = "\n".join([
            f"Shot {s.get('order', i+1)}: {s.get('prompt', '')}"
            for i, s in enumerate(shots)
        ])

        coherence_prompt = f"""Analiza la coherencia narrativa de estos shots:

{shots_text}

Evalúa:
1. ¿Los shots conectan de forma fluida?
2. ¿Hay saltos lógicos?
3. ¿El estilo visual es consistente?
4. Sugerencias de mejora

Responde en JSON:
{{
  "coherence_score": 0-100,
  "issues": ["lista de problemas"],
  "suggestions": ["lista de mejoras"],
  "overall": "resumen"
}}"""

        result = await self.send_message(coherence_prompt, session_id=session_id)
        response_text = result.get("text", result.get("response", ""))
        
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except json.JSONDecodeError:
            pass

        return {"coherence_score": -1, "issues": [], "suggestions": [], "overall": response_text}

    async def health_check(self) -> bool:
        """Check if Flowise is running and accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/ping")
                return response.status_code == 200
        except Exception:
            return False


flowise_service = FlowiseService()
