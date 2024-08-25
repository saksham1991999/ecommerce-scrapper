from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.scraper_schemas import ScraperRequest, ScraperResponse
from app.services.scraper_service import ScraperService
from app.exceptions.scraper_exceptions import ScraperException
from app.repositories.json_file_repository import JsonFileRepository
from app.services.notification_service import NotificationService
from app.notifications.console_notifier import ConsoleNotifier

router = APIRouter()

def get_scraper_service() -> ScraperService:
    repository: JsonFileRepository = JsonFileRepository()
    notifiers: List[ConsoleNotifier] = [ConsoleNotifier()]
    notification_service: NotificationService = NotificationService(notifiers)
    return ScraperService(repository, notification_service)

@router.post("/scrape", response_model=ScraperResponse)
async def scrape(
    request: ScraperRequest,
    scraper_service: ScraperService = Depends(get_scraper_service)
) -> ScraperResponse:
    try:
        products: List[Product] = await scraper_service.scrape_catalog(page_limit=request.page_limit)
        return ScraperResponse(
            status="success",
            data=[product.dict() for product in products]
        )
    except ScraperException as e:
        raise HTTPException(status_code=500, detail=str(e))