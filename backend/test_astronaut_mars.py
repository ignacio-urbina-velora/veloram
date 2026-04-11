
import asyncio
import os
import sys
from sqlalchemy import select

# Add parent dir to path for imports
sys.path.append(os.getcwd())

from app.database import async_session
from app.services.director_service import director_service
from app.services.generation_service import generation_service
from app.models.project import Project, Shot

async def run_full_test_cycle():
    print("--- INICIANDO CICLO COMPLETO DE PRUEBA: Astronauta en Marte ---")
    
    # 1. Definir la idea
    user_id = 6 # Usaremos el ID del usuario del reporte
    idea = "Un astronauta caminando sobre el suelo rojo de Marte, cinematico, 8k, ultra realista"
    duration = 10
    
    async with async_session() as db:
        # PASO 1: Planificar con el Director
        print("[1/4] El Director está planificando las escenas...")
        # Note: We pass temp_{user_id} to trigger the creation of a new real project
        result = await director_service.plan_video(
            idea=idea,
            target_duration_sec=duration,
            style="cinematic",
            project_id=f"temp_{user_id}",
            db=db
        )
        
        project_id = int(result.get("project_id"))
        print(f"SUCCESS: Director creó el Proyecto {project_id} con {len(result['shots'])} escenas.")
        
        # PASO 2: Generar Keyframes (Imágenes de Fal.ai)
        print("[2/4] Generando Keyframes con Fal.ai...")
        # In a real app this is a background task, here we call it directly
        await generation_service.generate_keyframes(db, project_id)
        
        # Verificar imágenes en la DB
        await db.commit() # Ensure shots are in DB
        result_shots = await db.execute(select(Shot).where(Shot.project_id == project_id))
        shots = result_shots.scalars().all()
        for s in shots:
            print(f" - Shot {s.order}: {s.preview_url}")
            
        # PASO 3: Generar Video (Modo Simulación)
        print("[3/4] Generando Video final (MOCK MODE)...")
        await generation_service.generate_project(db, project_id)
        await db.commit()
        
        # PASO 4: Resultado Final
        project_resp = await db.get(Project, project_id)
        print(f"\n--- RESULTADO FINAL ---")
        print(f"Proyecto ID: {project_resp.id}")
        print(f"Status: {project_resp.status}")
        print(f"Video URL: {project_resp.final_video_url}")
        
        if project_resp.status == "completed" and project_resp.final_video_url:
            print("\n¡PRUEBA EXITOSA! El sistema interactuó, generó imágenes y produjo el video.")
        else:
            print("\nFALLO: El video no se completó correctamente.")

if __name__ == "__main__":
    asyncio.run(run_full_test_cycle())
