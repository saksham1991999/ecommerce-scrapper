import aioredis
from typing import Optional
import os
from app.constants import REDIS_URL, PRODUCT_PRICE_CACHE_KEY

class RedisCache:
    def __init__(self):
        self.redis = None
        self.redis_url = REDIS_URL

    async def initialize(self):
        if self.redis is None:
            self.redis = await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

    async def get_product_price(self, product_id: str) -> Optional[str]:
        await self.initialize()
        return await self.redis.get(PRODUCT_PRICE_CACHE_KEY.format(product_id))

    async def set_product_price(self, product_id: str, price: str) -> None:
        await self.initialize()
        await self.redis.set(PRODUCT_PRICE_CACHE_KEY.format(product_id), price)

    async def close(self) -> None:
        if self.redis:
            await self.redis.close()