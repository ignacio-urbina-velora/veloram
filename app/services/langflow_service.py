"""Langflow API Service — communicates with Langflow to act as the 'Director Brain'."""

import httpx
import logging
import json
from typing import Optional, List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class LangflowService:
    """Client for the Langflow API."""

    def __init__(self, base_url: str = settings.LANGFLOW_BASE_URL):
        self.base_url = base_url
        self.api_key = settings.LANGFLOW_API_KEY
        self.flow_id: Optional[str] = settings.LANGFLOW_FLOW_ID
        self.application_id: Optional[str] = settings.LANGFLOW_APPLICATION_ID

    async def run_flow(
        self,
        message: str,
        flow_id: Optional[str] = None,
        tweaks: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a Langflow flow and return the response."""
        fid = flow_id or self.flow_id
        if not fid:
            logger.warning("No flow_id configured.")
            return {"result": "No flow ID configured."}

        # Langflow API (Process)
        url = f"{self.base_url}/api/v1/process/{fid}"
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        payload = {
            "input_value": message,
            "output_type": "chat",
            "input_type": "chat",
        }
        
        if tweaks:
            payload["tweaks"] = tweaks

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Langflow API error: {e}")
            raise RuntimeError(f"Langflow API error: {e}")

    async def plan_video(
        self,
        idea: str,
        duration_minutes: int = 1,
        style: str = "cinematic",
    ) -> Dict[str, Any]:
        """Use the Langflow Director to plan a full video from an idea."""
        planning_prompt = f"""Planifica un video de {duration_minutes} minutos con esta idea:
"{idea}"
Estilo visual: {style}

Divide en 6-12 shots coherentes. Responde en este JSON:
{{
  "title": "...",
  "shots": [
    {{
      "order": 1,
      "image_prompt": "...",
      "motion_prompt": "...",
      "camera_movement": "...",
      "duration_sec": 5
    }}
  ]
}}"""

        result = await self.run_flow(planning_prompt)
        
        # Extract text from Langflow response
        # Langflow response structure typically: {"result": "...", "outputs": [...]}
        response_text = result.get("result", "")
        if not response_text and "outputs" in result:
            # Fallback for structured Langflow outputs
            try:
                response_text = result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            except (KeyError, IndexError):
                pass

        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                plan = json.loads(response_text[json_start:json_end])
                return {"plan": plan, "raw_response": response_text}
        except json.JSONDecodeError:
            pass

        return {"plan": None, "raw_response": response_text}

langflow_service = LangflowService()
