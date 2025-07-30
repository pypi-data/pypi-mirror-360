import os
import httpx
from .manifest import ManifestModel

class ResourceManClient:
    def __init__(self, base_url: str = None):
        self._client = httpx.AsyncClient(base_url=base_url or os.getenv("RESOURCE_MAN_URL", "http://localhost:3000"))
        self._registered = set()

    async def register_manifest(self, name: str, manifest: ManifestModel):
        if name not in self._registered:
            await self._client.post(f"/resources/{name}", json=manifest.dict())
            self._registered.add(name)

    async def submit_resource(self, name: str, resource: dict):
        await self._client.post(f"/records/{name}", json=resource)

    async def close(self):
        await self._client.aclose()
