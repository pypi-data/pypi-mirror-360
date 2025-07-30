import asyncio
from .client import ResourceManClient
from .manifest import build_manifest

client = ResourceManClient()

class AutoResource:
    def __init_subclass__(cls, **kwargs):
        cls._manifest = build_manifest(cls)
        cls._resource_name = cls.__name__.lower()

    def __init__(self, **kwargs):
        self.data = kwargs
        asyncio.create_task(self._register_and_submit())

    async def _register_and_submit(self):
        await client.register_manifest(self._resource_name, self.__class__._manifest)
        await client.submit_resource(self._resource_name, self.data)
