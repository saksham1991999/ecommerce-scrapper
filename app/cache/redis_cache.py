import aioredis
from typing import Optional
import os

class RedisCache:
    def __init__(self):
        self.redis = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost")

    async def initialize(self):
        if self.redis is None:
            self.redis = await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

    async def get_product_price(self, product_id: str) -> Optional[str]:
        await self.initialize()
        return await self.redis.get(f"product_price:{product_id}")

    async def set_product_price(self, product_id: str, price: str) -> None:
        await self.initialize()
        await self.redis.set(f"product_price:{product_id}", price)

    async def close(self) -> None:
        if self.redis:
            await self.redis.close()