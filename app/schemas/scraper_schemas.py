from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.product_schema import ProductSchema

class ScraperRequest(BaseModel):
    page_limit: Optional[int] = Field(None, ge=1, description="Maximum number of pages to scrape")

class ScraperResponse(BaseModel):
    status: str = Field(..., description="Status of the scraping operation")
    data: List[ProductSchema] = Field(..., description="List of scraped products")