from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.scraper_schemas import ScraperRequest, ScraperResponse
from app.services.scraper_service import ScraperService
from app.exceptions.scraper_exceptions import ScraperException
from app.repositories.json_file_repository import JsonFileRepository
from app.services.notification_service import NotificationService
from app.notifications.console_notifier import ConsoleNotifier
from app.cache.redis_cache import RedisCache
from app.models.product import Product

router = APIRouter()

async def get_scraper_service() -> ScraperService:
    repository: JsonFileRepository = JsonFileRepository()
    notifiers: List[ConsoleNotifier] = [ConsoleNotifier()]
    notification_service: NotificationService = NotificationService(notifiers)
    cache: RedisCache = RedisCache()
    await cache.initialize()
    return ScraperService(repository, notification_service, cache)

@router.post("/scrape", response_model=ScraperResponse)
async def scrape(
    request: ScraperRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> ScraperResponse:
    try:
        all_products, updated_products = await scraper_service.scrape_catalog(page_limit=request.page_limit)
        return ScraperResponse(
            status="success",
            total_scraped=len(all_products),
            total_updated=len(updated_products),
            updated_products=[product.dict() for product in updated_products]
        )
    except ScraperException as e:
        raise HTTPException(status_code=500, detail=str(e))