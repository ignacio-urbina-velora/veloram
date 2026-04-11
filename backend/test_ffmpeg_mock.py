import asyncio
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_test():
    project_dir = Path(r"c:\Users\user\.gemini\antigravity\scratch\ai-video-platform\backend\storage\projects\13")
    final_video_path = str(project_dir / "test_final.mp4")
    concat_list_path = str(project_dir / "concat.txt")
    
    ffmpeg_path = r"C:\ProgramData\chocolatey\bin\ffmpeg.EXE"
    
    vf_watermark = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24,drawtext=text='ID\\: 13 | VELORA':fontcolor=white@0.6:fontsize=18:x=w-text_w-16:y=h-text_h-12:box=1:boxcolor=black@0.35:boxborderw=6"
    cmd = [
        ffmpeg_path, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-vf", vf_watermark,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        final_video_path
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"ffmpeg error: {stderr.decode()[-300:]}")
        else:
            logger.info("Success! ffmpeg ran cleanly.")
    except Exception as e:
        logger.error(f"Exception: {e}")

asyncio.run(run_test())
