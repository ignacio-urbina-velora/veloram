"""vast.ai GPU rental service."""

import asyncio
import logging
from typing import Optional

import httpx

from app.config import settings, TierConfig

logger = logging.getLogger(__name__)


class VastService:
    """Client for vast.ai REST API – search, rent, manage GPU instances."""

    def __init__(self):
        self.api_key = settings.VAST_API_KEY
        self.base_url = settings.VAST_API_BASE
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method,
                f"{self.base_url}{path}",
                headers=self.headers,
                **kwargs,
            )
            resp.raise_for_status()
            return resp.json()

    async def search_gpus(self, tier: int, max_results: int = 10) -> list[dict]:
        """Search available GPU offers matching tier requirements."""
        tier_cfg = TierConfig.get(tier)
        gpu_types = tier_cfg["gpu_types"]
        min_vram = tier_cfg["min_vram_gb"]

        # vast.ai search query
        query = {
            "verified": {"eq": True},
            "external": {"eq": False},
            "rentable": {"eq": True},
            "gpu_ram": {"gte": min_vram * 1024},  # MB
            "num_gpus": {"eq": 1},
            "inet_down": {"gte": 200},  # Min 200 Mbps download
            "reliability2": {"gte": 0.95},
            "order": [["dph_total", "asc"]],  # Cheapest first
            "type": "on-demand",
            "limit": max_results,
        }

        try:
            result = await self._request("GET", "/bundles/", params={"q": str(query)})
            offers = result.get("offers", [])

            # Filter by GPU type name
            filtered = []
            for offer in offers:
                gpu_name = offer.get("gpu_name", "").upper().replace(" ", "_")
                if any(gt in gpu_name for gt in gpu_types):
                    filtered.append(offer)

            if not filtered:
                # Fallback: return all offers if no exact GPU match
                logger.warning(f"No exact GPU match for tier {tier}, returning best available")
                return offers[:max_results]

            return filtered[:max_results]
        except Exception as e:
            logger.error(f"vast.ai search failed: {e}")
            raise

    async def rent_instance(
        self,
        offer_id: int,
        docker_image: str,
        disk_gb: int = 40,
        onstart_cmd: str = "",
    ) -> dict:
        """Rent a GPU instance with specified Docker image."""
        payload = {
            "client_id": "me",
            "image": docker_image,
            "disk": disk_gb,
            "onstart": onstart_cmd,
            "runtype": "args",
        }

        result = await self._request("PUT", f"/asks/{offer_id}/", json=payload)
        logger.info(f"Rented instance from offer {offer_id}: {result}")
        return result

    async def get_instance(self, instance_id: str) -> dict:
        """Get instance details."""
        result = await self._request("GET", f"/instances/{instance_id}/")
        return result

    async def get_instance_ip(self, instance_id: str) -> Optional[str]:
        """Get the public IP:port for ComfyUI on the instance."""
        instance = await self.get_instance(instance_id)
        if instance.get("actual_status") == "running":
            # vast.ai provides port mapping
            ports = instance.get("ports", {})
            comfy_port = str(settings.COMFYUI_PORT)
            if comfy_port in ports:
                port_info = ports[comfy_port]
                return f"{port_info['HostIp']}:{port_info['HostPort']}"
            # Fallback to direct IP
            public_ip = instance.get("public_ipaddr")
            if public_ip:
                return f"{public_ip}:{comfy_port}"
        return None

    async def wait_ready(
        self, instance_id: str, timeout_sec: int = 300, poll_interval: int = 10
    ) -> bool:
        """Poll until instance is running and ComfyUI is healthy."""
        elapsed = 0
        while elapsed < timeout_sec:
            try:
                instance = await self.get_instance(instance_id)
                status = instance.get("actual_status", "")

                if status == "running":
                    # Check if ComfyUI is responding
                    ip = await self.get_instance_ip(instance_id)
                    if ip:
                        try:
                            async with httpx.AsyncClient(timeout=5) as client:
                                resp = await client.get(f"http://{ip}/system_stats")
                                if resp.status_code == 200:
                                    logger.info(f"Instance {instance_id} ready at {ip}")
                                    return True
                        except Exception:
                            pass  # ComfyUI not ready yet

                elif status in ("exited", "error"):
                    logger.error(f"Instance {instance_id} failed: {status}")
                    return False

            except Exception as e:
                logger.warning(f"Polling instance {instance_id}: {e}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        logger.error(f"Instance {instance_id} timed out after {timeout_sec}s")
        return False

    async def destroy_instance(self, instance_id: str) -> None:
        """Terminate and release a GPU instance."""
        try:
            await self._request("DELETE", f"/instances/{instance_id}/")
            logger.info(f"Destroyed instance {instance_id}")
        except Exception as e:
            logger.error(f"Failed to destroy instance {instance_id}: {e}")

    async def get_cost(self, instance_id: str) -> float:
        """Get current accumulated cost for an instance."""
        instance = await self.get_instance(instance_id)
        return float(instance.get("total_cost", 0.0))


# Singleton
vast_service = VastService()
