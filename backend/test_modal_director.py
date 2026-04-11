import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())
load_dotenv()

from app.agents.director.nodes import bible_creator_node
from app.agents.director.state import DirectorState

async def test_modal_director():
    print("--- 🧪 Testing Director AI on Modal (NSFW) ---")
    
    # Check if configured
    url = os.getenv("DIRECTOR_MODAL_URL")
    if not url or "tu-url" in url:
        print("❌ ERROR: Debes desplegar el worker primero y poner la URL en el .env")
        return

    # Simulation of a +18 request that usually fails in OpenAI
    state: DirectorState = {
        "project_id": "test_modal",
        "idea": "Una escena de romance apasionado en una terraza nocturna neón, estilo visual seductor y cinematográfico.",
        "duration_target_sec": 15,
        "style": "cinematic",
        "style_guide": "",
        "characters": {},
        "rules": [],
        "bible_version": 1,
        "bible_summary": None,
        "shots": [],
        "user_feedback": None,
        "validation_issues": [],
        "current_step": "start"
    }
    
    try:
        print(f"Enviando idea a Modal: {state['idea']}")
        result = bible_creator_node(state)
        
        print("\n✅ RESULTADO RECIBIDO:")
        print(f"Style Guide: {result.get('style_guide')}")
        print(f"Characters: {result.get('characters')}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_modal_director())
