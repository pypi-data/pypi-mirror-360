from typing import Optional, List
import httpx
from .maw_sdk_resource_models import Manifest, Resource


class ResourceManClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self.version = "v0.1.0"

    async def close(self):
        await self.client.aclose()

    async def submit_resource(self, name: str, resource: Resource) -> Optional[dict]:
        url = f"/records/{name}"
        response = await self.client.post(url, json=resource.__root__)
        response.raise_for_status()
        return response.json() if response.content else None

    async def list_resources(self, name: str) -> List[dict]:
        url = f"/records/{name}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def list_manifests(self) -> List[tuple[str, Manifest]]:
        url = "/resources"
        response = await self.client.get(url)
        response.raise_for_status()
        return [(m[0], Manifest(**m[1])) for m in response.json()]

    async def get_manifest(self, name: str) -> Optional[Manifest]:
        url = f"/resources/{name}"
        response = await self.client.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Manifest(**response.json())

    async def create_manifest(self, name: str, manifest: Manifest) -> None:
        url = f"/resources/{name}"
        response = await self.client.post(url, json=manifest.model_dump())
        response.raise_for_status()
