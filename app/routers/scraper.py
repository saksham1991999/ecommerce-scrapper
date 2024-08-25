import os
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.scraper_schemas import ScraperRequest, ScraperResponse
from app.services.scraper_service import ScraperService
from app.services.storage_service import StorageService
from app.services.caching_service import CachingService
from app.exceptions.scraper_exceptions import ScraperException
from app.repositories.postgres_repository import PostgresRepository
from app.services.notification_service import NotificationService
from app.notifications.console_notifier import ConsoleNotifier
from app.notifications.twilio_notifier import TwilioNotifier
from app.notifications.email_notifier import EmailNotifier
from app.cache.redis_cache import RedisCache
from app.models.product import Product

router = APIRouter()

async def get_scraper_service() -> ScraperService:
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres/scraper_db")
    repository = PostgresRepository(db_url)
    storage_service = StorageService(repository)
    
    cache = RedisCache()
    await cache.initialize()
    caching_service = CachingService(cache)
    
    notifiers = []
    if all([os.getenv(env_var) for env_var in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_NUMBER', 'TWILIO_TO_NUMBER']]):
        notifiers.append(TwilioNotifier())
    if all([os.getenv(env_var) for env_var in ['EMAIL_SENDER', 'EMAIL_PASSWORD', 'EMAIL_RECEIVER']]):
        notifiers.append(EmailNotifier())
    if not notifiers:
        notifiers.append(ConsoleNotifier())
    
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