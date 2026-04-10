from typing import Any, Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
from pydantic import BaseModel, Field

from app.agents.director.state import DirectorState, DirectorBible, ShotSequence
from app.config import settings
import os

import httpx
import os
import json
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

class ModalLLM(BaseChatModel):
    """Custom wrapper for the Modal-hosted Llama-3-8B Director."""
    endpoint_url: str
    token_id: str
    token_secret: str
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> ChatResult:
        # Extract system and user messages
        system_msg = next((m.content for m in messages if isinstance(m, SystemMessage)), "Eres un director experto.")
        user_msg = next((m.content for m in messages if isinstance(m, HumanMessage or BaseMessage)), "")

        with httpx.Client(timeout=120.0) as client:
            resp = client.post(
                self.endpoint_url,
                headers={
                    "x-modal-token-id": self.token_id,
                    "x-modal-token-secret": self.token_secret
                },
                json={"prompt": user_msg, "system_prompt": system_msg}
            )
            resp.raise_for_status()
            text = resp.json().get("response", "")
            
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    @property
    def _llm_type(self) -> str:
        return "modal-llama3"

    def with_structured_output(self, schema: Any, **kwargs: Any):
        """Wraps the result in a parser for the given Pydantic schema."""
        return StructuredModalLLM(llm=self, schema=schema)

class CategorizationSchema(BaseModel):
    intent: str = Field(description="STRICTLY one of: 'new_idea', 'feedback', 'chat', 'confirmation'")
    explanation: str = Field(description="Brief reasoning in Spanish for this categorization.")

class CritiqueSchema(BaseModel):
    opinion: str = Field(description="Collaborative and artistic opinion about the user's idea in Spanish.")
    suggestions: List[str] = Field(description="List of 2-3 specific artistic improvements.")
    next_step_prompt: str = Field(description="A question to the user to keep the conversation going.")

class StructuredModalLLM:
    """Wrapper to parse JSON output from ModalLLM into a Pydantic model."""
    def __init__(self, llm: ModalLLM, schema: Any):
        self.llm = llm
        self.schema = schema

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        msg = self.llm.invoke(input, **kwargs)
        content = msg.content
        # Remove any markdown code blocks
        content = content.replace("```json", "").replace("```", "").strip()
        try:
            if not content:
                # Fallback structure
                return self.schema(explanation="Entiendo. ¿Qué más te gustaría añadir a tu video?", shots=[])
            
            data = json.loads(content)
            return self.schema(**data)
        except Exception as e:
            print(f"Error parsing JSON from LLM: {e}\nContent: {content}")
            # Ensure it doesn't crash the whole pipeline, return empty sequence
            return self.schema(explanation="Error al procesar la respuesta técnica. ¿Podrías intentar de nuevo?", shots=[])

# Helper to get the LLM
def get_llm(model_name: str, temperature: float = 0.7):
    provider = settings.LLM_PROVIDER.lower()

    if provider == "modal":
        return ModalLLM(
            endpoint_url=settings.DIRECTOR_MODAL_URL,
            token_id=settings.MODAL_TOKEN_ID,
            token_secret=settings.MODAL_TOKEN_SECRET
        )

    # Fallback to OpenRouter/OpenAI
    api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
    base_url = "https://openrouter.ai/api/v1" if settings.OPENROUTER_API_KEY else None
    
    # Only add 'openai/' prefix if model name has no provider namespace already (no slash)
    # e.g. 'gpt-4o' → 'openai/gpt-4o', but 'meta-llama/llama-3.3-70b:free' stays as-is
    if base_url and "/" not in model_name:
        model_name = f"openai/{model_name}"
        
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=api_key,
        base_url=base_url
    )

def bible_creator_node(state: DirectorState) -> Dict[str, Any]:
    """Infers the Director's Bible from the initial idea."""
    llm = get_llm(model_name="gpt-4o-mini", temperature=0.7)
    structured_llm = llm.with_structured_output(DirectorBible, method="function_calling")
    
    prompt = f"""

    You are an expert Hollywood Director of Photography and Creative Director.
    Create a detailed 'Director's Bible' for a cinematic short video.
    
    Initial Idea: {state['idea']}
    Target Duration: {state['duration_target_sec']} seconds
    Desired Style: {state.get('style', 'cinematic')}
    
    Define the overall visual style guide, list the key characters with their physical descriptions, 
    and establish 3 to 5 strict cinematic rules that the AI generation should obey.
    """
    
    bible = structured_llm.invoke(prompt)
    
    return {
        "style_guide": bible.style_guide,
        "characters": [c.model_dump() for c in bible.characters],
        "rules": bible.rules,
        "bible_version": 1,
        "bible_summary": None,
        "current_step": "bible_creator"
    }

def router_node(state: DirectorState) -> Dict[str, Any]:
    """Determines the user's intent to route the graph correctly."""
    llm = get_llm(model_name="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(CategorizationSchema, method="function_calling")
    
    last_input = state.get("user_feedback") or state.get("idea", "")
    
    system_prompt = """
    Eres el Coordinador del Velora Director. Tu trabajo es categorizar la entrada del usuario.
    
    CATEGORÍAS:
    - 'new_idea': El usuario propone una idea nueva para un video.
    - 'feedback': El usuario pide cambios específicos sobre un plan existente.
    - 'chat': Saludos, preguntas generales o charla no relacionada con la creación técnica.
    - 'confirmation': El usuario acepta una sugerencia, dice "adelante", "está bien", "hazlo", etc.
    """
    
    cat = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Entrada del usuario: {last_input}")
    ])
    
    return {
        "interaction_mode": cat.intent,
        "explanation": cat.explanation,
        "current_step": "router"
    }

def chat_node(state: DirectorState) -> Dict[str, Any]:
    """Handles general conversation/chat."""
    llm = get_llm(model_name="gpt-4o-mini", temperature=0.7)
    
    last_input = state.get("user_feedback") or state.get("idea", "")
    
    system_prompt = """
    ERES EL VELORA DIRECTOR, UN ASISTENTE DE IA AMABLE Y PROFESIONAL.
    
    Tu objetivo es charlar con el usuario, responder sus dudas sobre cine, saludarlo o simplemente conversar.
    No generas shots técnicos aquí, solo mantienes la conversación fluida y profesional en ESPAÑOL.
    """
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_input)
    ]).content
    
    return {
        "explanation": response,
        "current_step": "chat"
    }

def critic_node(state: DirectorState) -> Dict[str, Any]:
    """Provides a collaborative artistic opinion before planning."""
    llm = get_llm(model_name="gpt-4o-mini", temperature=0.7)
    structured_llm = llm.with_structured_output(CritiqueSchema, method="function_calling")
    
    style_context = state.get("bible_summary") or state.get("style_guide", "")
    idea = state.get("idea", "")
    
    system_prompt = """
    ERES EL VELORA DIRECTOR, UN DIRECTOR DE CINE COLABORATIVO Y TALENTOSO.
    
    TU MISIÓN:
    Analiza la idea del usuario y la 'Biblia' del proyecto. Da tu opinión artística honesta pero amable.
    Propón mejoras que eleven la calidad cinematográfica (luces, encuadres, ritmo).
    
    ESTILO:
    - Colaborativo: Usa frases como "¿Qué te parece si...?", "Podríamos intentar...", "Desde mi punto de vista...".
    - Profesional: Habla con términos de cine pero de forma accesible.
    - Idioma: ESPAÑOL.
    """
    
    critique = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Idea: {idea}\nContexto Visual: {style_context}")
    ])
    
    full_response = f"{critique.opinion}\n\nSugerencias:\n- " + "\n- ".join(critique.suggestions) + f"\n\n{critique.next_step_prompt}"
    
    return {
        "director_critique": full_response,
        "explanation": full_response,
        "current_step": "critic"
    }

def summarizer_node(state: DirectorState) -> Dict[str, Any]:
    """Compresses the Bible into a compact summary to save tokens and maintain focus."""
    # Only summarize if it's long or if specifically triggered
    if state.get("bible_summary") and len(state.get("style_guide", "")) < 500:
        return {"current_step": "summarizer_skipped"}

    llm = get_llm(model_name="gpt-4o-mini", temperature=0.3)
    
    prompt = f"""
    Summarize the following Director's Bible into a very compact but highly descriptive 'Visual DNA' paragraph (max 100 words).
    Keep the core lighting, mood, and character essence.
    
    Style Guide: {state.get('style_guide')}
    Characters: {json.dumps(state.get('characters', {}))}
    Rules: {state.get('rules')}
    """
    
    summary = llm.invoke(prompt).content
    
    return {
        "bible_summary": summary,
        "current_step": "summarizer"
    }

def planner_node(state: DirectorState) -> Dict[str, Any]:
    """Generates or updates the shot sequence based on the bible and idea."""
    llm = get_llm(model_name="gpt-4o-mini", temperature=0.4)
    structured_llm = llm.with_structured_output(ShotSequence, method="function_calling")

    existing_shots = state.get("shots", [])
    user_feedback = state.get("user_feedback")
    validation_issues = state.get("validation_issues", [])
    
    # Use summary if available to keep prompt clean
    style_context = state.get("bible_summary") or state.get("style_guide", "")

    system_prompt = f"""
    ERES EL VELORA DIRECTOR, UN ASISTENTE DE IA AVANZADO Y EXPERTO EN NARRATIVA VISUAL.
    
    TU PERSONALIDAD:
    Eres colaborador, creativo y profesional. Respondes como un director de cine real en un set.
    
    TU MISIÓN:
    1. DIÁLOGO (Campo 'explanation'): Confirma que vas a preparar el plan técnico basado en vuestra charla.
    2. PLANIFICACIÓN (Campo 'shots'): Genera la secuencia de escenas técnica.

    BIBLIA DEL PROYECTO (Contexto Visual):
    {style_context}

    CRÍTICA/ACUERDOS PREVIOS:
    {state.get('director_critique', 'Ninguno')}
    """
    
    user_msg_content = f"Idea del usuario: {state['idea']}\nFeedback actual: {user_feedback}"
    if validation_issues:
        user_msg_content += f"\nCorregir estos problemas: {validation_issues}"
        
    sequence = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg_content)
    ])
    
    # Map image_prompt to prompt if needed for compatibility
    shots_data = []
    for i, shot in enumerate(sequence.shots):
        s_dict = shot.model_dump()
        if s_dict.get("prompt") is None and s_dict.get("image_prompt"):
            s_dict["prompt"] = s_dict["image_prompt"]
        if "order" not in s_dict or s_dict["order"] is None:
            s_dict["order"] = i
        shots_data.append(s_dict)
    
    return {
        "shots": shots_data,
        "explanation": sequence.explanation,
        "current_step": "planner",
        "user_feedback": None,
        "validation_issues": []
    }

def validator_node(state: DirectorState) -> Dict[str, Any]:
    """Reviews the generated sequence for mechanical and physical constraints."""
    shots = state.get("shots", [])
    validation_issues = []
    
    allowed_motions = ["static", "pan_left", "pan_right", "dolly_in", "dolly_out", "orbit", "tilt_up", "tilt_down", "crane"]
    
    for shot in shots:
        motion = shot.get("camera_movement", "").lower()
        if motion not in allowed_motions:
            validation_issues.append(f"Shot {shot['order']}: '{motion}' invalid motion.")
            
    return {
        "validation_issues": validation_issues,
        "current_step": "validator"
    }

