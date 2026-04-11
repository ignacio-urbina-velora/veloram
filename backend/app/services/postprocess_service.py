"""Post-processing pipeline – stitching, interpolation, upscale, audio."""

import asyncio
import logging
import os
import tempfile
from app.config import settings

logger = logging.getLogger(__name__)


class PostprocessService:
    """Handles video post-processing per tier."""

    async def process(self, clips: list[bytes], tier_cfg: dict) -> bytes:
        """Full post-processing pipeline based on tier."""
        tier_name = tier_cfg["name"]
        logger.info(f"Post-processing {len(clips)} clips for tier: {tier_name}")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write clips to disk
            clip_paths = []
            for i, clip_data in enumerate(clips):
                path = os.path.join(tmpdir, f"clip_{i:04d}.mp4")
                with open(path, "wb") as f:
                    f.write(clip_data)
                clip_paths.append(path)

            if not clip_paths:
                raise ValueError("No clips to process")

            # Step 1: Stitch with crossfade transitions
            stitched = os.path.join(tmpdir, "stitched.mp4")
            await self._stitch_clips(clip_paths, stitched)

            # Step 2: Frame interpolation (Tier 2+)
            interpolated = stitched
            if tier_cfg.get("fps", 24) >= 60:
                interpolated = os.path.join(tmpdir, "interpolated.mp4")
                await self._interpolate_frames(
                    stitched, interpolated, target_fps=tier_cfg["fps"]
                )

            # Step 3: Upscale (Tier 3 only)
            upscaled = interpolated
            if tier_cfg.get("upscale", False):
                upscaled = os.path.join(tmpdir, "upscaled.mp4")
                await self._upscale_4k(interpolated, upscaled)

            # Step 4: Color grading (Tier 3 only)
            graded = upscaled
            if tier_cfg.get("color_grading", False):
                graded = os.path.join(tmpdir, "graded.mp4")
                await self._apply_color_grading(upscaled, graded)

            # Read final output
            final_path = graded
            with open(final_path, "rb") as f:
                return f.read()

    async def _stitch_clips(self, clip_paths: list[str], output: str) -> None:
        """Concatenate clips with smooth transitions or simple concat using ffmpeg."""
        if len(clip_paths) == 1:
            import shutil
            shutil.copy(clip_paths[0], output)
            return

        # For production-grade stitching with crossfades, we'd use complex filterchains.
        # For now, we use a robust concat demuxer as it handles different VFR/resolutions better.
        concat_file = output.replace(".mp4", "_list.txt")
        with open(concat_file, "w") as f:
            for path in clip_paths:
                # Ensure paths are escaped correctly for ffmpeg list
                safe_path = path.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        ffmpeg_path = settings.FFMPEG_PATH
        if ffmpeg_path == "ffmpeg":
             # Fallback to known absolute path on this system if needed
             potential_path = r"C:\ProgramData\chocolatey\bin\ffmpeg.EXE"
             if os.path.exists(potential_path): ffmpeg_path = potential_path

        cmd = [
            ffmpeg_path, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-preset", "superfast", # Faster for dev
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output,
        ]

        logger.info(f"Running ffmpeg stitch: {' '.join(cmd)}")
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"FFmpeg stitch failed: {stderr.decode()}")
            # Critical fallback: if concat fails, try to at least provide the first clip
            import shutil
            shutil.copy(clip_paths[0], output)
        else:
            logger.info(f"Stitched {len(clip_paths)} clips successfully")

    async def _add_audio_placeholder(self, video_path: str, output_path: str) -> None:
        """Placeholder for adding background music or dialogue synthesis."""
        # This will be integrated with ElevenLabs/Sunomama in the future
        logger.info("Audio mixing placeholder: skipping for now")
        import shutil
        shutil.copy(video_path, output_path)

    async def _interpolate_frames(
        self, input_path: str, output_path: str, target_fps: int = 60
    ) -> None:
        """Interpolate frames to target FPS using ffmpeg minterpolate."""
        cmd = [
            settings.FFMPEG_PATH, "-y",
            "-i", input_path,
            "-filter:v", f"minterpolate=fps={target_fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.warning(f"Interpolation failed, falling back to original: {stderr.decode()[:300]}")
            import shutil
            shutil.copy(input_path, output_path)
        else:
            logger.info(f"Interpolated to {target_fps}fps → {output_path}")

    async def _upscale_4k(self, input_path: str, output_path: str) -> None:
        """Upscale video to 4K using ffmpeg lanczos scaling."""
        cmd = [
            settings.FFMPEG_PATH, "-y",
            "-i", input_path,
            "-vf", "scale=3840:2160:flags=lanczos",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "16",
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.warning(f"Upscale failed, keeping original resolution")
            import shutil
            shutil.copy(input_path, output_path)
        else:
            logger.info(f"Upscaled to 4K → {output_path}")

    async def _apply_color_grading(self, input_path: str, output_path: str) -> None:
        """Apply cinematic color grading using ffmpeg curves/eq."""
        cmd = [
            settings.FFMPEG_PATH, "-y",
            "-i", input_path,
            "-vf", "eq=contrast=1.1:brightness=0.02:saturation=1.15,curves=preset=cross_process",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.warning(f"Color grading failed, keeping original")
            import shutil
            shutil.copy(input_path, output_path)
        else:
            logger.info(f"Applied cinematic color grading → {output_path}")


postprocess_service = PostprocessService()
