from typing import List, Optional, Tuple
from app.utils.scraper import Scraper
from app.models.product import Product
from app.exceptions.scraper_exceptions import ScraperException
from app.repositories.base_repository import BaseRepository
from app.services.notification_service import NotificationService
from app.cache.redis_cache import RedisCache
from decimal import Decimal

class ScraperService:
    def __init__(self, repository: BaseRepository, notification_service: NotificationService, cache: RedisCache):
        self.scraper: Scraper = Scraper()
        self.repository: BaseRepository = repository
        self.notification_service: NotificationService = notification_service
        self.cache: RedisCache = cache

    async def scrape_catalog(self, page_limit: Optional[int] = None) -> Tuple[List[Product], List[Product]]:
        try:
            all_products: List[Product] = await self.scraper.scrape_catalog(page_limit=page_limit)
            updated_products = await self.update_changed_products(all_products)
            
            message: str = f"Scraping completed. {len(all_products)} products were scraped, {len(updated_products)} were updated in the database."
            await self.notification_service.notify_all(message)
            
            return all_products, updated_products
        except ScraperException as e:
            error_message: str = f"Scraping failed after retries: {str(e)}"
            await self.notification_service.notify_all(error_message)
            raise

    async def update_changed_products(self, products: List[Product]) -> List[Product]:
        updated_products = []
        for product in products:
            cached_price = await self.cache.get_product_price(product.id)
            if cached_price is None or Decimal(cached_price) != product.product_price:
                await self.repository.save_product(product)
                await self.cache.set_product_price(product.id, str(product.product_price))
                updated_products.append(product)
        return updated_products