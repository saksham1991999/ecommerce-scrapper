from typing import List, Optional
from app.utils.scraper import Scraper
from app.models.product import Product
from app.exceptions.scraper_exceptions import ScraperException
from app.repositories.base_repository import BaseRepository
from app.services.notification_service import NotificationService

class ScraperService:
    def __init__(self, repository: BaseRepository, notification_service: NotificationService):
        self.scraper: Scraper = Scraper()
        self.repository: BaseRepository = repository
        self.notification_service: NotificationService = notification_service

    async def scrape_catalog(self, page_limit: Optional[int] = None) -> List[Product]:
        try:
            products: List[Product] = await self.scraper.scrape_catalog(page_limit=page_limit)
            await self.repository.save_products(products)
            
            message: str = f"Scraping completed. {len(products)} products were scraped and updated in the database."
            await self.notification_service.notify_all(message)
            
            return products
        except ScraperException as e:
            error_message: str = f"Scraping failed after retries: {str(e)}"
            await self.notification_service.notify_all(error_message)
            raise