"""Storage service – S3/local file storage."""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class StorageService:
    """Handles file uploads and downloads. Uses local storage for dev, S3 for prod."""

    def __init__(self):
        self.local_dir = os.path.join(os.getcwd(), "storage")
        os.makedirs(self.local_dir, exist_ok=True)

    async def upload_video(self, video_data: bytes, key: str) -> str:
        """Upload video and return URL/path."""
        # For dev: save locally
        path = os.path.join(self.local_dir, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            f.write(video_data)

        logger.info(f"Uploaded video: {key} ({len(video_data)} bytes)")
        return f"/storage/{key}"

    async def upload_image(self, image_data: bytes, key: str) -> str:
        """Upload image and return URL/path."""
        path = os.path.join(self.local_dir, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            f.write(image_data)

        return f"/storage/{key}"

    async def get_file(self, key: str) -> Optional[bytes]:
        """Retrieve a file by key."""
        path = os.path.join(self.local_dir, key)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        return None

    async def delete_file(self, key: str) -> bool:
        """Delete a file."""
        path = os.path.join(self.local_dir, key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False


storage_service = StorageService()
