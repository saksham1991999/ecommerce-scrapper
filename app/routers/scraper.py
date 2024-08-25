import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.scraper_schemas import ScraperRequest, ScraperResponse
from app.services.scraper_service import ScraperService
from app.services.storage_service import StorageService
from app.services.caching_service import CachingService
from app.exceptions.scraper_exceptions import ScraperException
from app.exceptions.storage_exceptions import StorageException
from app.exceptions.caching_exceptions import CacheException
from app.exceptions.notification_exceptions import NotificationException
from app.exceptions.authentication_exceptions import AuthenticationException
from app.repositories.postgres_repository import PostgresRepository
from app.services.notification_service import NotificationService
from app.notifications.console_notifier import ConsoleNotifier
from app.notifications.twilio_notifier import TwilioNotifier
from app.notifications.email_notifier import EmailNotifier
from app.cache.redis_cache import RedisCache
from app.models.product import Product
from starlette.status import HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_503_SERVICE_UNAVAILABLE, HTTP_500_INTERNAL_SERVER_ERROR

from app.constants import DATABASE_URL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_scraper_service() -> ScraperService:
    logger.info("Initializing scraper service")
    try:
        db_url = DATABASE_URL
        repository = PostgresRepository(db_url)
        storage_service = StorageService(repository)
        
        cache = RedisCache()
        await cache.initialize()
        caching_service = CachingService(cache)
        
        notifiers = []
        if all([os.getenv(env_var) for env_var in [TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER]]):
            logger.info("Twilio notifier enabled")
            notifiers.append(TwilioNotifier())
        if all([os.getenv(env_var) for env_var in [EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]]):
            logger.info("Email notifier enabled")
            notifiers.append(EmailNotifier())
        if not notifiers:
            logger.info("No external notifiers configured, using console notifier")
            notifiers.append(ConsoleNotifier())
        
        notification_service = NotificationService(notifiers)
        
        logger.info("Scraper service initialized")
        return ScraperService(storage_service, caching_service, notification_service)
    except AuthenticationException as e:
        logger.error(f"Authentication error initializing scraper service: {str(e)}")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Authentication failed initializing scraper service")
    except (StorageException, CacheException, NotificationException) as e:
        logger.error(f"Failed to initialize scraper service: {str(e)}")
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Service Unavailable: Failed to initialize scraper service")

@router.post("/scrape", response_model=ScraperResponse)
async def scrape(
    request: ScraperRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> ScraperResponse:
    logger.info(f"Received scrape request with page_limit: {request.page_limit}, proxy: {request.proxy}")
    try:
        all_products, updated_products = await scraper_service.scrape_catalog(
            page_limit=request.page_limit,
            proxy=str(request.proxy) if request.proxy else None
        )
        logger.info(f"Scraping completed. Total products: {len(all_products)}, Updated products: {len(updated_products)}")
        return ScraperResponse(
            status="success",
            total_scraped=len(all_products),
            total_updated=len(updated_products),
            updated_products=[product.dict() for product in updated_products]
        )
    except AuthenticationException as e:
        logger.error(f"Authentication failed during scraping: {str(e)}")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Authentication failed during scraping")
    except ScraperException as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unprocessable Entity: {str(e)}")
    except (StorageException, CacheException, NotificationException) as e:
        logger.error(f"Service error during scraping process: {str(e)}")
        raise HTTPException(status_code=HTTP_503_SERVICE_UNAVAILABLE, detail="Service Unavailable: Internal service error")
    except Exception as e:
        logger.error(f"Unexpected error during scraping process: {str(e)}")
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")