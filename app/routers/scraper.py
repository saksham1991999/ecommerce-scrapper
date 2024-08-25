from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.scraper_schemas import ScraperRequest, ScraperResponse
from app.services.scraper_service import ScraperService
from app.services.storage_service import StorageService
from app.services.caching_service import CachingService
from app.exceptions.scraper_exceptions import ScraperException
from app.repositories.json_file_repository import JsonFileRepository
from app.services.notification_service import NotificationService
from app.notifications.console_notifier import ConsoleNotifier
from app.cache.redis_cache import RedisCache
from app.models.product import Product

router = APIRouter()

async def get_scraper_service() -> ScraperService:
    repository = JsonFileRepository()
    storage_service = StorageService(repository)
    
    cache = RedisCache()
    await cache.initialize()
    caching_service = CachingService(cache)
    
    notifiers: List[ConsoleNotifier] = [ConsoleNotifier()]
    notification_service = NotificationService(notifiers)
    
    return ScraperService(storage_service, caching_service, notification_service)

@router.post("/scrape", response_model=ScraperResponse)
async def scrape(
    request: ScraperRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> ScraperResponse:
    try:
        all_products, updated_products = await scraper_service.scrape_catalog(
            page_limit=request.page_limit,
            proxy=str(request.proxy) if request.proxy else None
        )
        return ScraperResponse(
            status="success",
            total_scraped=len(all_products),
            total_updated=len(updated_products),
            updated_products=[product.dict() for product in updated_products]
        )
    except ScraperException as e:
        raise HTTPException(status_code=500, detail=str(e))