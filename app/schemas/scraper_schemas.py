from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from app.schemas.product_schema import ProductSchema

class ScraperRequest(BaseModel):
    page_limit: Optional[int] = Field(None, ge=1, description="Maximum number of pages to scrape")
    proxy: Optional[HttpUrl] = Field(default=None, description="Proxy URL to use for scraping")

class ScraperResponse(BaseModel):
    status: str = Field(..., description="Status of the scraping operation")
    total_scraped: int = Field(..., description="Total number of products scraped")
    total_updated: int = Field(..., description="Number of products updated in the database")
    updated_products: List[ProductSchema] = Field(..., description="List of updated products")