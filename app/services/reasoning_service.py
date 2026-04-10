import modal
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ReasoningService:
    """Service to interact with the Reasoning Agent on Modal."""

    def __init__(self):
        self.app_name = "reasoning-agent"
        self.method_name = "reason"

    async def get_reasoning(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the Modal reasoning agent."""
        try:
            # We use modal.Function.lookup to call the deployed function
            # Note: This requires the worker to be deployed first
            f = modal.Function.lookup(self.app_name, "ReasoningAgent.reason")
            
            # Using asyncio to run in thread for now as Modal call is blocking in some contexts
            # but modal python client has async support too
            # For simplicity in this demo, we'll assume the user has modal configured
            result = f.remote(prompt, system_prompt)
            return result
        except Exception as e:
            logger.error(f"Reasoning agent call failed: {e}")
            return f"Lo siento, el agente de razonamiento no está disponible en este momento. Error: {str(e)}"

reasoning_service = ReasoningService()
