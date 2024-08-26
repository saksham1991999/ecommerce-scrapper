from decimal import Decimal
from typing import Optional

from app.cache.redis_cache import RedisCache


class CachingService:
    """
    A service class for caching product prices using Redis.
    """

    def __init__(self, cache: RedisCache):
        """
        Initialize the CachingService with a Redis cache.

        Args:
            cache (RedisCache): An instance of RedisCache for caching operations.
        """
        self.cache = cache

    async def get_product_price(self, product_id: str) -> Optional[Decimal]:
        """
        Retrieve the cached price of a product.

        Args:
            product_id (str): The unique identifier of the product.

        Returns:
            Optional[Decimal]: The price of the product as a Decimal, or None if not found.
        """
        price_str = await self.cache.get_product_price(product_id)
        return Decimal(price_str) if price_str else None

    async def set_product_price(self, product_id: str, price: Decimal) -> None:
        """
        Cache the price of a product.

        Args:
            product_id (str): The unique identifier of the product.
            price (Decimal): The price of the product to be cached.

        Returns:
            None
        """
        await self.cache.set_product_price(product_id, str(price))
