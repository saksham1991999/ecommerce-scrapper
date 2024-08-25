from typing import List, Optional, Tuple
from app.utils.scraper import Scraper
from app.models.product import Product
from app.exceptions.scraper_exceptions import ScraperException
from app.services.storage_service import StorageService
from app.services.caching_service import CachingService
from app.services.notification_service import NotificationService
from decimal import Decimal

class ScraperService:
    def __init__(self, storage_service: StorageService, caching_service: CachingService, notification_service: NotificationService):
        self.storage_service = storage_service
        self.caching_service = caching_service
        self.notification_service = notification_service

    async def scrape_catalog(self, page_limit: Optional[int] = None, proxy: Optional[str] = None) -> Tuple[List[Product], List[Product]]:
        try:
            scraper: Scraper = Scraper(proxy=proxy)
            all_products: List[Product] = await scraper.scrape_catalog(page_limit=page_limit)
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
            cached_price = await self.caching_service.get_product_price(product.id)
            if cached_price is None or cached_price != product.product_price:
                await self.storage_service.save_product(product)
                await self.caching_service.set_product_price(product.id, product.product_price)
                updated_products.append(product)
        return updated_products