import httpx
import json
import re
from typing import Optional, Any

# Import the new LangGraph Director Brain
from app.agents.director.graph import graph_director_service

class DirectorService:
    def __init__(self):
        # Mantenemos esto temporalmente para refine_shot (single shot)
        self.ollama_url = "https://ignaciourbinakonecta--reasoning-agent-reasoningagent-reason.modal.run"
        self.model = "langgraph-agent"

    async def _call_ollama(self, system_prompt: str, user_prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "prompt": user_prompt,
                        "system_prompt": system_prompt
                    }
                )
                response.raise_for_status()
                content = response.json().get("response", "{}")
                content = re.sub(r"```json\s*", "", content)
                content = re.sub(r"```\s*", "", content)
                return json.loads(content)
            except Exception as e:
                print(f"[DirectorService] Ollama Error: {e}")
                return {"shots": []}

    async def plan_video(self, idea: str, target_duration_sec: int, style: str, project_id: str, db: Optional[Any] = None) -> dict:
        """Plan a video using the new stateful LangGraph Director Brain and persist the Bible."""
        try:
            print(f"[DirectorService] Starting LangGraph pipeline for project {project_id}...")
            final_state = await graph_director_service.initial_plan(idea, target_duration_sec, style, project_id)
            
            shots = []
            for s in final_state.get("shots", []):
                # Ensure DB schema compatibility (image_prompt -> prompt)
                if s.get("prompt") is None and s.get("image_prompt"):
                    s["prompt"] = s["image_prompt"]
                shots.append(s)
            
            # Persist to DB if session provided
            actual_id = project_id
            if db:
                try:
                    from app.models.project import Project, Shot as ShotModel
                    from sqlalchemy import delete
                    
                    # If it's a temp ID, we create a new Project
                    if str(project_id).startswith("temp_"):
                        user_id = int(project_id.split("_")[1])
                        project = Project(
                            user_id=user_id,
                            title=f"Borrador: {idea[:30]}...",
                            tier=3, 
                            target_duration_sec=target_duration_sec,
                            global_prompt=idea,
                            status="draft"
                        )
                        db.add(project)
                        await db.flush() # Get the new ID
                        actual_id = str(project.id)
                        print(f"[DirectorService] Created new project {actual_id} from temp ID")
                    else:
                        project = await db.get(Project, int(project_id))
                    
                    if project:
                        project.director_bible = {
                            "style_guide": final_state.get("style_guide"),
                            "characters": final_state.get("characters"),
                            "rules": final_state.get("rules"),
                            "summary": final_state.get("bible_summary")
                        }
                        project.bible_version = final_state.get("bible_version", 1)
                        project.thread_id = f"project_{actual_id}"
                        
                        # Sync shots to DB - Delete old ones first
                        await db.execute(delete(ShotModel).where(ShotModel.project_id == project.id))
                        
                        for i, s in enumerate(shots):
                            new_shot = ShotModel(
                                project_id=project.id,
                                order=i,
                                prompt=s.get("prompt", ""),
                                camera_movement=s.get("camera_movement", "static"),
                                lighting=s.get("lighting", "natural"),
                                mood=s.get("mood", "neutral"),
                                dialogue=s.get("dialogue"),
                                negative_prompt=s.get("negative_prompt"),
                                duration_target_sec=s.get("duration_target_sec", 5.0),
                                status="pending"
                            )
                            db.add(new_shot)
                        
                        await db.commit()
                        print(f"[DirectorService] SUCCESSFULLY Persisted Bible and {len(shots)} shots for project {actual_id}")
                    else:
                        print(f"[DirectorService] CRITICAL: Project {actual_id} not found in DB")
                        
                except Exception as db_err:
                    print(f"[DirectorService] Warning: Could not persist to DB: {db_err}")
                    import traceback
                    traceback.print_exc()

            return {
                "shots": shots,
                "explanation": final_state.get("explanation", ""),
                "director_critique": final_state.get("director_critique"),
                "interaction_mode": final_state.get("interaction_mode"),
                "project_id": str(actual_id)
            }
        except Exception as e:
            err_str = str(e)
            print(f"[DirectorService] LangGraph error on plan_video: {err_str}")
            import traceback
            traceback.print_exc()
            # Always return an explanation so the frontend shows something useful
            if "402" in err_str or "Insufficient credits" in err_str:
                msg = "⚠️ Sin créditos en OpenRouter. Carga créditos en openrouter.ai/settings/credits para activar el Director."
            elif "401" in err_str or "api_key" in err_str.lower():
                msg = "⚠️ Clave de API inválida. Revisa tu OPENROUTER_API_KEY en el archivo .env."
            elif "timeout" in err_str.lower():
                msg = "⏱️ El modelo tardó demasiado en responder. Intenta de nuevo."
            else:
                msg = f"❌ Error interno del Director: {err_str[:120]}"
            return {"shots": [], "explanation": msg}
        
    async def refine_shot(self, shot: dict, feedback: str) -> dict:
        """Refines a single shot using the legacy Ollama fallback for now."""
        system_prompt = """
You are an expert AI Video Director. Refine the given shot based on user feedback.
Return ONLY the updated shot object in STRICT JSON.
Do not wrap it in any list or extra keys.
        """
        user_prompt = f"Original shot:\n{json.dumps(shot, indent=2)}\n\nUser Feedback: {feedback}\n\nRefine the shot."
        return await self._call_ollama(system_prompt, user_prompt)
        
    async def refine_sequence(self, shots: list, feedback: str, project_id: str, db: Optional[Any] = None) -> dict:
        """Refine the entire sequence using LangGraph and the persisted Bible."""
        try:
            print(f"[DirectorService] Starting LangGraph refinement for project {project_id}...")
            
            bible_data = {}
            if db and not str(project_id).startswith("temp_"):
                try:
                    from app.models.project import Project
                    project = await db.get(Project, int(project_id))
                    if project and project.director_bible:
                        bible_data = project.director_bible
                except Exception as db_err:
                    print(f"[DirectorService] Warning: Could not fetch DB project: {db_err}")

            target_duration = sum(s.get("duration_target_sec", 0) for s in shots)
            if target_duration == 0: target_duration = 15
                
            existing_state = {
                "project_id": project_id,
                "idea": "Reviewing existing sequence",
                "duration_target_sec": target_duration,
                "style": "cinematic",
                "style_guide": bible_data.get("style_guide", ""),
                "characters": bible_data.get("characters", {}),
                "rules": bible_data.get("rules", []),
                "bible_summary": bible_data.get("summary"),
                "bible_version": bible_data.get("bible_version", 1),
                "shots": shots,
                "validation_issues": [],
                "user_feedback": feedback,
                "director_critique": bible_data.get("director_critique"),
                "interaction_mode": "feedback", # The router will refine this
                "explanation": None,
                "current_step": "refining"
            }
            final_state = await graph_director_service.refine_plan(existing_state, feedback)
            shots = []
            for s in final_state.get("shots", []):
                if "image_prompt" in s and "prompt" not in s:
                    s["prompt"] = s["image_prompt"]
                shots.append(s)
                
            # Update DB shots if refined
            if db and not str(project_id).startswith("temp_"):
                try:
                    from app.models.project import Shot as ShotModel
                    from sqlalchemy import delete
                    pid = int(project_id)
                    await db.execute(delete(ShotModel).where(ShotModel.project_id == pid))
                    for i, s in enumerate(shots):
                        new_shot = ShotModel(
                            project_id=pid,
                            order=i,
                            prompt=s.get("prompt", ""),
                            camera_movement=s.get("camera_movement", "static"),
                            lighting=s.get("lighting", "natural"),
                            mood=s.get("mood", "neutral"),
                            dialogue=s.get("dialogue"),
                            negative_prompt=s.get("negative_prompt"),
                            duration_target_sec=s.get("duration_target_sec", 5.0),
                            status="pending"
                        )
                        db.add(new_shot)
                    await db.commit()
                except Exception as db_err:
                    print(f"[DirectorService] Refine DB sync error: {db_err}")

            return {
                "shots": shots, 
                "project_id": project_id,
                "explanation": final_state.get("explanation", ""),
                "interaction_mode": final_state.get("interaction_mode")
            }
        except Exception as e:
            print(f"[DirectorService] LangGraph error on refine_sequence: {e}")
            return {"shots": shots}

director_service = DirectorService()
