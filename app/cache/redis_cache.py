from typing import Optional

import aioredis

from app.constants import PRODUCT_PRICE_CACHE_KEY, REDIS_URL


class RedisCache:
    """
    A class to handle Redis caching operations.
    """

    def __init__(self):
        """
        Initialize the RedisCache instance.
        """
        self.redis: Optional[aioredis.Redis] = None
        self.redis_url: str = REDIS_URL

    async def initialize(self) -> None:
        """
        Initialize the Redis connection if it hasn't been established yet.
        """
        if self.redis is None:
            self.redis = await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)

    async def get_product_price(self, product_id: str) -> Optional[str]:
        """
        Retrieve the price of a product from the cache.

        Args:
            product_id (str): The ID of the product.

        Returns:
            Optional[str]: The price of the product if found, None otherwise.
        """
        await self.initialize()
        if self.redis:
            return await self.redis.get(PRODUCT_PRICE_CACHE_KEY.format(product_id))
        return None

    async def set_product_price(self, product_id: str, price: str) -> None:
        """
        Set the price of a product in the cache.

        Args:
            product_id (str): The ID of the product.
            price (str): The price of the product.
        """
        await self.initialize()
        if self.redis:
            await self.redis.set(PRODUCT_PRICE_CACHE_KEY.format(product_id), price)

    async def close(self) -> None:
        """
        Close the Redis connection if it exists.
        """
        if self.redis:
            await self.redis.close()
            self.redis = None
