from typing import Optional
from app.cache.redis_cache import RedisCache
from decimal import Decimal

class CachingService:
    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def get_product_price(self, product_id: str) -> Optional[Decimal]:
        price_str = await self.cache.get_product_price(product_id)
        return Decimal(price_str) if price_str else None

    async def set_product_price(self, product_id: str, price: Decimal) -> None:
        await self.cache.set_product_price(product_id, str(price))