"""Generation orchestrator – coordinates GPU rental, ComfyUI execution, and post-processing."""

import asyncio
import logging
import tempfile
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings, TierConfig
from app.models.project import Project, Shot
from app.models.job import Job
from app.services.modal_service import STORAGE_ABS_PATH, save_image, generate_image
import os
import shutil

logger = logging.getLogger(__name__)


class GenerationService:
    """Orchestrates the full video generation pipeline per project."""

    MAX_PARALLEL_INSTANCES = 4

    async def generate_project(self, db: AsyncSession, project_id: int) -> str:
        """Entry point for project generation. Routes based on the selected engine."""
        project = await db.get(Project, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Routing logic
        engine = project.video_engine or "mock"
        
        if engine == "mock":
            logger.info(f"[GenerationService] Using MOCK/SIMULATION MODE for project {project_id}")
            return await self._generate_mock_project(db, project_id)
        
        logger.info(f"[GenerationService] Using {engine} engine for project {project_id}")
        return await self._generate_real_video_project(db, project_id, engine)


    async def _generate_real_video_project(self, db: AsyncSession, project_id: int, engine: str) -> str:
        """Video Generation using the selected real GPU engine (Wan, LTX, Hunyuan)."""
        from app.services.wan_service import generate_video
        from app.services.modal_service import STORAGE_ABS_PATH
        import httpx
        import base64
        from pathlib import Path
        import os

        project = await db.get(Project, project_id)
        result = await db.execute(select(Shot).where(Shot.project_id == project_id).order_by(Shot.order))
        shots = list(result.scalars().all())

        project.status = "generating"
        await db.flush()

        video_paths = []
        project_dir = STORAGE_ABS_PATH / "projects" / str(project_id)
        os.makedirs(project_dir, exist_ok=True)

        for shot in shots:
            shot.status = "generating"
            await db.flush()
            
            try:
                # 1. Identity Reinforcement: Use Shot Keyframe as source
                image_b64 = None
                if shot.preview_url:
                    local_preview = Path(shot.preview_url.lstrip("/"))
                    if local_preview.exists():
                        image_b64 = base64.b64encode(local_preview.read_bytes()).decode('utf-8')
                
                logger.info(f"[GenerationService] Calling {engine} for shot {shot.id}...")
                video_url = await generate_video(
                    engine=engine,
                    prompt=shot.prompt,
                    image_b64=image_b64
                )
                
                if video_url:
                    # Download video clip
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        v_resp = await client.get(video_url)
                        if v_resp.status_code == 200:
                            clip_filename = f"shot_{shot.id}.mp4"
                            clip_path = project_dir / clip_filename
                            with open(clip_path, "wb") as f:
                                f.write(v_resp.content)
                            
                            shot.clip_url = f"/storage/projects/{project_id}/{clip_filename}"
                            shot.status = "done"
                            video_paths.append(str(clip_path))
                        else:
                            shot.status = "failed"
                else:
                    shot.status = "failed"
            except Exception as e:
                logger.error(f"[GenerationService] Error in shot {shot.id}: {e}")
                shot.status = "failed"
            
            await db.flush()
            await db.commit()

        # Stitch videos (FFmpeg) - Simplified for now, using existing mock stitcher logic
        # In a real scenario, we'd use complex FFmpeg filters
        final_video_url = await self._stitch_project_videos(db, project_id, video_paths)
        return final_video_url

    async def _generate_modal_project(self, db: AsyncSession, project_id: int) -> str:
        """Video Generation using Modal SVD API and FFmpeg stitching."""
        from app.services.modal_service import generate_video_clip
        import base64
        from pathlib import Path

        project = await db.get(Project, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        project.status = "generating"
        await db.flush()

        result = await db.execute(select(Shot).where(Shot.project_id == project_id).order_by(Shot.order))
        shots = list(result.scalars().all())

        if not shots:
            raise ValueError("Project has no shots")

        tier_cfg = TierConfig.get(project.tier)
        
        # Load avatar image if available
        avatar_image_b64 = None
        if project.avatar_id:
            from app.models.avatar import Avatar
            avatar = await db.get(Avatar, project.avatar_id)
            if avatar and avatar.texture_url:
                local_path = Path(avatar.texture_url.lstrip("/"))
                if local_path.exists():
                    avatar_image_b64 = base64.b64encode(local_path.read_bytes()).decode('utf-8')
        
        clips_bytes = []
        
        for shot in shots:
            shot.status = "generating"
            await db.flush()
            
            try:
                # NEW: Priority for init image: 1. Shot Keyframe (preview_url), 2. Avatar
                init_image_b64 = None
                if shot.preview_url:
                    local_preview = Path(shot.preview_url.lstrip("/"))
                    if local_preview.exists():
                        init_image_b64 = base64.b64encode(local_preview.read_bytes()).decode('utf-8')
                
                if not init_image_b64:
                    init_image_b64 = avatar_image_b64

                if not init_image_b64:
                    # Generic fallback
                    init_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

                fps = tier_cfg.get("fps", 7)
                logger.info(f"Generating video for shot {shot.id} (init_image present: {bool(init_image_b64)}) via Modal...")
                
                video_b64 = await generate_video_clip(init_image_b64, fps=fps)
                video_bytes = base64.b64decode(video_b64)
                clips_bytes.append(video_bytes)
                shot.status = "done"
            except Exception as e:
                logger.error(f"Shot {shot.id} Modal generation failed: {e}")
                shot.status = "failed"
            
            await db.flush()

        # Check if all failed
        if not clips_bytes:
             project.status = "failed"
             await db.flush()
             raise RuntimeError("All shots failed to generate via Modal")

        project.status = "postprocessing"
        await db.flush()

        logger.info(f"Passing {len(clips_bytes)} clips to postprocess_service...")
        final_video_bytes = await self._postprocess(clips_bytes, tier_cfg)

        video_url = await storage_service.upload_video(final_video_bytes, f"projects/{project_id}/final.mp4")

        project.final_video_url = video_url
        project.status = "completed"
        project.completed_at = datetime.utcnow()
        await db.flush()

        user = await db.get(User, project.user_id)
        if user:
            asyncio.create_task(email_service.send_generation_complete(user.email, project.title or f"Proyecto {project.id}", project.id))

        return video_url

    async def generate_keyframes(self, db: AsyncSession, project_id: int):
        """Generates a high-quality keyframe for each shot in the project using FLUX."""
        from app.services.modal_service import generate_image, save_image
        import base64
        from pathlib import Path

        project = await db.get(Project, project_id)
        if not project: return

        result = await db.execute(select(Shot).where(Shot.project_id == project_id).order_by(Shot.order))
        shots = list(result.scalars().all())

        # Load avatar metadata if available for consistency
        avatar_metadata = None
        if project.avatar_id:
            from app.models.avatar import Avatar
            import json
            avatar = await db.get(Avatar, project.avatar_id)
            if avatar and avatar.morphs:
                avatar_metadata = avatar.morphs if isinstance(avatar.morphs, dict) else json.loads(avatar.morphs)

        for shot in shots:
            if shot.preview_url:
                logger.info(f"Shot {shot.id} (Project {project_id}) already has a preview_url: {shot.preview_url}. Skipping.")
                continue

            try:
                logger.info(f"[GenerationService] Generating keyframe for project {project_id} shot {shot.order} (Shot ID {shot.id}) via Wan 2.2...")
                
                from app.services.wan_service import generate_shot_wan22
                img_b64 = await generate_shot_wan22(
                    shot_prompt=shot.prompt,
                    avatar_metadata=avatar_metadata,
                    lighting=shot.lighting,
                    camera_movement=shot.camera_movement,
                    mood=shot.mood,
                    tier="professional"
                )
                
                if not img_b64:
                    logger.error(f"[GenerationService] Received empty image for shot {shot.id}")
                    shot.status = "failed"
                    await db.commit()
                    continue

                filename = f"shot_{shot.id}_keyframe.png"
                logger.info(f"[GenerationService] Image generated for shot {shot.id}. Saving to projects/{project_id}/shots/{filename}...")
                rel_url = await save_image(img_b64, f"projects/{project_id}/shots", filename)
                
                shot.preview_url = rel_url
                shot.status = "done"
                logger.info(f"[GenerationService] Shot {shot.id} preview_url SUCCESSFULLY set to: {rel_url}")
                await db.commit() # Commit each shot so polling sees it immediately
            except Exception as e:
                shot.status = "failed"
                logger.error(f"[GenerationService] CRITICAL: Failed to generate keyframe for shot {shot.id}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                await db.commit()
        
        await db.commit()
        logger.info(f"Finished keyframe generation for project {project_id}")

    async def generate_shot(self, db: AsyncSession, project_id: int, shot_id: int):
        """
        Generates a high-quality keyframe for a single shot.
        Automatically switches to Wan 2.2 if available, maintaining identity consistency.
        """
        from app.services.wan_service import generate_shot_wan22
        from app.models.avatar import Avatar
        import json
        
        project = await db.get(Project, project_id)
        shot = await db.get(Shot, shot_id)
        if not project or not shot:
            return None
            
        shot.status = "generating"
        await db.flush()
        await db.commit()
        
        try:
            # 1. Look for avatar visual traits (metadata)
            avatar_metadata = None
            if project.avatar_id:
                avatar = await db.get(Avatar, project.avatar_id)
                if avatar and avatar.morphs:
                    # Morphs contain the selected traits (metadata)
                    avatar_metadata = avatar.morphs if isinstance(avatar.morphs, dict) else json.loads(avatar.morphs)
            
            # 2. Call Wan 2.2 for "Natural Hiperrealismo"
            logger.info(f"[GenerationService] Generating shot {shot_id} via Wan 2.2...")
            img_b64 = await generate_shot_wan22(
                shot_prompt=shot.prompt,
                avatar_metadata=avatar_metadata,
                lighting=shot.lighting,
                camera_movement=shot.camera_movement,
                mood=shot.mood,
                tier="professional" # Standard for shots
            )
            
            if img_b64:
                from app.services.modal_service import save_image
                filename = f"shot_{shot_id}_remote.png"
                rel_url = await save_image(img_b64, f"projects/{project_id}/shots", filename)
                
                shot.preview_url = rel_url
                shot.status = "done"
                logger.info(f"[GenerationService] Shot {shot_id} updated with preview: {rel_url}")
            else:
                shot.status = "failed"
                logger.error(f"[GenerationService] Wan 2.2 failed for shot {shot_id}")
                
            await db.flush()
            await db.commit()
            return shot.preview_url
            
        except Exception as e:
            logger.error(f"[GenerationService] Error in generate_shot: {e}")
            shot.status = "failed"
            await db.commit()
            return None

    async def _old_generate_project(self, db: AsyncSession, project_id: int) -> str:
        """Old Full pipeline: rent GPUs → generate shots → post-process → upload."""
        project = await db.get(Project, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        tier_cfg = TierConfig.get(project.tier)
        
        # Check if we should use simulation mode (no API key or placeholder)
        is_placeholder_key = not settings.VAST_API_KEY or "change-me" in settings.VAST_API_KEY or "fe500" in settings.VAST_API_KEY
        if is_placeholder_key:
            logger.info(f"VAST_API_KEY not set or placeholder. Entering SIMULATION MODE for project {project_id}")
            return await self._generate_mock_project(db, project_id)

        project.status = "generating"
        await db.flush()

        # Get all shots ordered
        result = await db.execute(
            select(Shot)
            .where(Shot.project_id == project_id)
            .order_by(Shot.order)
        )
        shots = list(result.scalars().all())

        if not shots:
            raise ValueError("Project has no shots")

        # Determine how many parallel instances to rent
        instance_count = min(len(shots), self.MAX_PARALLEL_INSTANCES)

        instances = []
        try:
            # 1. Rent GPU instances
            logger.info(f"Renting {instance_count} GPUs for tier {project.tier}")
            instances = await self._rent_gpus(
                db, project, tier_cfg, instance_count
            )

            # 2. Wait for all instances to be ready
            ready_instances = []
            for inst_id in instances:
                if await vast_service.wait_ready(inst_id, timeout_sec=300):
                    ready_instances.append(inst_id)
                else:
                    logger.warning(f"Instance {inst_id} failed to start, skipping")

            if not ready_instances:
                raise RuntimeError("No GPU instances became ready")

            # 3. Generate shots in parallel across instances
            clips = await self._generate_shots_parallel(
                db, project, shots, ready_instances, tier_cfg
            )

            # 4. Post-process: stitch, interpolate, audio
            project.status = "postprocessing"
            await db.flush()

            final_video = await self._postprocess(clips, tier_cfg)

            # 5. Upload final video
            video_url = await storage_service.upload_video(
                final_video, f"projects/{project_id}/final.mp4"
            )

            project.final_video_url = video_url
            project.status = "completed"
            project.completed_at = datetime.utcnow()
            await db.flush()

            # Notify user
            user = await db.get(User, project.user_id)
            if user:
                asyncio.create_task(email_service.send_generation_complete(user.email, project.title or f"Proyecto {project.id}", project.id))

            return video_url

        except Exception as e:
            logger.error(f"Generation failed for project {project_id}: {e}")
            project.status = "failed"
            await db.flush()
            raise

        finally:
            # Always release GPU instances
            for inst_id in instances:
                try:
                    cost = await vast_service.get_cost(inst_id)
                    project.total_cost_usd += cost
                    await vast_service.destroy_instance(inst_id)
                except Exception as e:
                    logger.error(f"Cleanup error for {inst_id}: {e}")
            await db.flush()

    async def _rent_gpus(
        self,
        db: AsyncSession,
        project: Project,
        tier_cfg: dict,
        count: int,
    ) -> list[str]:
        """Search and rent GPU instances."""
        offers = await vast_service.search_gpus(project.tier, max_results=count * 2)
        if not offers:
            raise RuntimeError(f"No GPU offers available for tier {project.tier}")

        instance_ids = []
        for i, offer in enumerate(offers[:count]):
            # Determine onstart command to install ComfyUI + models
            onstart = self._build_onstart_script(tier_cfg)

            result = await vast_service.rent_instance(
                offer_id=offer["id"],
                docker_image="pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime",
                disk_gb=80 if project.tier >= 2 else 40,
                onstart_cmd=onstart,
            )

            inst_id = str(result.get("new_contract", result.get("id", "")))
            instance_ids.append(inst_id)

            # Create job record
            job = Job(
                project_id=project.id,
                job_type="clip_gen",
                vast_instance_id=inst_id,
                gpu_type=offer.get("gpu_name", "unknown"),
                status="renting_gpu",
            )
            db.add(job)

        await db.flush()
        return instance_ids

    def _build_onstart_script(self, tier_cfg: dict) -> str:
        """Build the startup script to install ComfyUI + models on the instance.

        Uses hosts with ComfyUI preinstalled when possible (vast.ai template).
        Installs all required custom nodes for multi-shot video generation:
        - ComfyUI-VideoHelperSuite (sequence management)
        - ComfyUI-Frame-Interpolation (RIFE/FILM smoothing)
        - WanVideoWrapper / HunyuanVideo nodes (Kijai / Comfy-Org)
        - Reactor / InstantID / IP-Adapter (avatar consistency)
        - ControlNet auxiliary preprocessors
        """
        lora_downloads = ""
        if "loras" in tier_cfg:
            for lora in tier_cfg["loras"]:
                lora_downloads += f"""
echo "Downloading LoRA: {lora['name']}"
cd /workspace/ComfyUI/models/loras
wget -q "{lora['url']}" -O "{lora['name']}.safetensors" || true
"""

        return f"""#!/bin/bash
set -e
echo "=== Setting up ComfyUI for AI Video Platform ==="

# If ComfyUI is preinstalled (vast.ai template), use it; otherwise clone
COMFY_DIR="${{COMFY_DIR:-/workspace/ComfyUI}}"
if [ ! -d "$COMFY_DIR" ]; then
    cd /workspace
    git clone https://github.com/comfyanonymous/ComfyUI.git 2>/dev/null || true
    COMFY_DIR="/workspace/ComfyUI"
fi
cd "$COMFY_DIR"
pip install -r requirements.txt 2>/dev/null || true

# ===== CUSTOM NODES (multi-shot video pipeline) =====
cd "$COMFY_DIR/custom_nodes"

# Video sequence management
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git 2>/dev/null || true

# Frame interpolation (RIFE/FILM for smooth transitions)
git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git 2>/dev/null || true

# Video generation models
git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git 2>/dev/null || true
git clone https://github.com/kijai/ComfyUI-HunyuanVideoWrapper.git 2>/dev/null || true
git clone https://github.com/Comfy-Org/ComfyUI_bitsandbytes_NF4.git 2>/dev/null || true

# Avatar consistency (face swap + identity preservation)
git clone https://github.com/Gourieff/comfyui-reactor-node.git 2>/dev/null || true
git clone https://github.com/cubiq/ComfyUI_InstantID.git 2>/dev/null || true
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git 2>/dev/null || true

# ControlNet preprocessors
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git 2>/dev/null || true

# Manager for additional node management
git clone https://github.com/ltdrdata/ComfyUI-Manager.git 2>/dev/null || true

# Install all node requirements
echo "Installing custom node dependencies..."
for d in */; do
    if [ -f "$d/requirements.txt" ]; then
        pip install -r "$d/requirements.txt" 2>/dev/null || true
    fi
    if [ -f "$d/install.py" ]; then
        python "$d/install.py" 2>/dev/null || true
    fi
done

cd "$COMFY_DIR"

{lora_downloads}

# Start ComfyUI headless
echo "Starting ComfyUI on port 8188..."
python main.py --listen 0.0.0.0 --port 8188 --disable-auto-launch &
echo "ComfyUI started"
"""

    async def _generate_shots_parallel(
        self,
        db: AsyncSession,
        project: Project,
        shots: List[Shot],
        instance_ids: list[str],
        tier_cfg: dict,
    ) -> list[bytes]:
        """Distribute shots across instances and generate in parallel."""
        # Build shot-to-instance mapping (round-robin)
        assignments = {}
        for i, shot in enumerate(shots):
            instance_idx = i % len(instance_ids)
            inst_id = instance_ids[instance_idx]
            if inst_id not in assignments:
                assignments[inst_id] = []
            assignments[inst_id].append(shot)

        # Generate on each instance
        tasks = []
        for inst_id, assigned_shots in assignments.items():
            tasks.append(
                self._generate_on_instance(db, project, assigned_shots, inst_id, tier_cfg)
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results and handle errors
        clips = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Shot generation failed: {result}")
            elif isinstance(result, list):
                clips.extend(result)

        return clips

    async def _generate_on_instance(
        self,
        db: AsyncSession,
        project: Project,
        shots: List[Shot],
        instance_id: str,
        tier_cfg: dict,
    ) -> list[bytes]:
        """Generate multiple shots on a single instance."""
        ip = await vast_service.get_instance_ip(instance_id)
        if not ip:
            raise RuntimeError(f"Could not get IP for instance {instance_id}")

        comfy = ComfyUIClient(ip)
        clips = []

        avatar = None
        if project.avatar_id:
            from app.models.avatar import Avatar
            avatar = await db.get(Avatar, project.avatar_id)

        for shot in shots:
            shot.status = "generating"
            await db.flush()

            try:
                # Load and configure workflow
                workflow = comfy.load_workflow(tier_cfg["workflow"])
                
                # Construct avatar URL for the remote instance
                avatar_url = None
                if avatar and avatar.reference_pack_url:
                    avatar_url = f"{settings.BACKEND_URL}{avatar.reference_pack_url}"

                params = {
                    "prompt": self._build_full_prompt(project, shot),
                    "negative_prompt": self._build_negative_prompt(project, shot),
                    "seed": hash(f"{project.id}-{shot.id}") % (2**32),
                    "lora_strength": tier_cfg.get("lora_strength", 0.8),
                    "avatar_id": project.avatar_id,
                    "avatar_url": avatar_url,
                    "controlnet_type": tier_cfg["controlnet"][0].lower() if tier_cfg.get("controlnet") else "pose",
                    "fps": tier_cfg["fps"],
                    "frames": int(shot.duration_target_sec * tier_cfg["fps"]),
                }

                if "loras" in tier_cfg:
                    params["lora_name"] = tier_cfg["loras"][0]["name"]

                workflow = comfy.inject_params(workflow, params)

                # Queue and wait
                prompt_id = await comfy.queue_prompt(workflow)
                result = await comfy.wait_for_completion(prompt_id, timeout_sec=600)

                # Download clip
                clip_data = await comfy.download_output(prompt_id)
                if clip_data:
                    clips.append(clip_data)
                    shot.status = "done"
                else:
                    shot.status = "failed"

            except Exception as e:
                logger.error(f"Shot {shot.id} generation failed: {e}")
                shot.status = "failed"

            await db.flush()

        return clips

    def _build_full_prompt(self, project: Project, shot: Shot) -> str:
        """Combine project global context, Bible 'Visual DNA', and shot parameters."""
        parts = []
        
        # 1. Bible Style Context (The 'Visual DNA')
        bible = project.director_bible or {}
        style_guide = bible.get("summary") or bible.get("style_guide", "")
        if style_guide:
            parts.append(f"Visual Style: {style_guide}")

        # 2. Character Context (If we have a main avatar)
        if project.avatar_id:
            # Try to find the description of the character that matches the avatar name
            # Or just use the summary of rules/characters to maintain consistency
            chars = bible.get("characters", [])
            char_desc = ""
            if chars and isinstance(chars, list):
                char_desc = chars[0].get("description", "") # Assume first character is main for now
            
            if char_desc:
                parts.append(f"Protagonist: {char_desc}")
            parts.append("maintaining consistent facial features from reference image")

        # 3. Global Prompt
        if project.global_prompt:
            parts.append(project.global_prompt)

        # 4. Shot specific prompt
        parts.append(shot.prompt)

        # 5. Technical details
        if shot.lighting: parts.append(f"{shot.lighting} lighting")
        if shot.mood: parts.append(f"{shot.mood} mood")
        
        return ", ".join(filter(None, parts))

    def _build_negative_prompt(self, project: Project, shot: Shot) -> str:
        """Merge global and shot-specific negative prompts."""
        base_neg = "deformed, blurry, bad anatomy, low quality, static, ugly"
        parts = [base_neg]
        if project.negative_prompt_global:
            parts.append(project.negative_prompt_global)
        if shot.negative_prompt:
            parts.append(shot.negative_prompt)
        return ", ".join(filter(None, parts))

    async def _postprocess(self, clips: list[bytes], tier_cfg: dict) -> bytes:
        """Post-process clips: stitch, interpolate, audio."""
        # This will be implemented in postprocess_service
        # For now, simple concatenation placeholder
        from app.services.postprocess_service import postprocess_service
        return await postprocess_service.process(clips, tier_cfg)


    async def _generate_mock_project(self, db: AsyncSession, project_id: int) -> str:
        """Simulate generation using shot keyframes as a slideshow."""
        project = await db.get(Project, project_id)
        if not project: return ""

        project.status = "generating"
        await db.flush()

        result = await db.execute(
            select(Shot).where(Shot.project_id == project_id).order_by(Shot.order)
        )
        shots = list(result.scalars().all())

        for shot in shots:
            if shot.status != "done":
                shot.status = "done"
        await db.flush()

        project.status = "postprocessing"
        await db.flush()
        await asyncio.sleep(0.5)

        project_dir = STORAGE_ABS_PATH / "projects" / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        final_video_path = str(project_dir / "final.mp4")

        ffmpeg_path = r"C:\ProgramData\chocolatey\bin\ffmpeg.EXE"
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = "ffmpeg"

        # Collect available shot keyframe images
        shot_images = []
        for shot in shots:
            if shot.preview_url:
                rel = shot.preview_url.replace("/storage/", "", 1)
                img_path = STORAGE_ABS_PATH / rel
                if img_path.exists():
                    shot_images.append(str(img_path))

        try:
            if shot_images:
                concat_list_path = str(project_dir / "concat.txt")
                with open(concat_list_path, "w") as f:
                    for img in shot_images:
                        f.write(f"file '{img}'\nduration 2\n")
                    f.write(f"file '{shot_images[-1]}'\n")

                vf_watermark = f"scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24,drawtext=text='ID\\: {project_id} | VELORA':fontcolor=white@0.6:fontsize=18:x=w-text_w-16:y=h-text_h-12:box=1:boxcolor=black@0.35:boxborderw=6"
                cmd = [
                    ffmpeg_path, "-y",
                    "-f", "concat", "-safe", "0", "-i", concat_list_path,
                    "-vf", vf_watermark,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    final_video_path
                ]
                logger.info(f"[MockProject] Building slideshow from {len(shot_images)} images (ID watermark: {project_id})...")
            else:
                cmd = [
                    ffmpeg_path, "-y",
                    "-f", "lavfi", "-i", "testsrc=duration=5:size=1280x720:rate=24",
                    "-vf", f"drawtext=text='Project {project_id} Preview':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2,drawtext=text='ID\\: {project_id} | VELORA':fontcolor=white@0.6:fontsize=18:x=w-text_w-16:y=h-text_h-12:box=1:boxcolor=black@0.35:boxborderw=6",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    final_video_path
                ]
                logger.warning("[MockProject] No shot images found, using test pattern with ID watermark.")

            import subprocess
            import shutil
            
            ffmpeg_resolved = shutil.which("ffmpeg")
            if ffmpeg_resolved:
                cmd[0] = ffmpeg_resolved
                
            def run_ffmpeg():
                return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            proc = await asyncio.to_thread(run_ffmpeg)
            if proc.returncode != 0:
                logger.error(f"[MockProject] ffmpeg error: {proc.stderr.decode()[-300:]}")
                with open(final_video_path, "wb") as f: f.write(b"MOCK_FALLBACK")
            else:
                logger.info(f"[MockProject] Video OK at {final_video_path}")
        except Exception as e:
            logger.error(f"[MockProject] ffmpeg exception: {e}")
            import traceback
            logger.error(traceback.format_exc())
            with open(final_video_path, "wb") as f: f.write(b"MOCK_ERROR")

        video_url = f"/storage/projects/{project_id}/final.mp4"
        project.final_video_url = video_url
        project.status = "completed"
        project.completed_at = datetime.utcnow()
        await db.flush()

        logger.info(f"[MockProject] COMPLETE for project {project_id}. Video: {video_url}")
        return video_url


generation_service = GenerationService()
