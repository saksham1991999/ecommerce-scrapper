from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.product_schema import ProductSchema


class ScraperRequest(BaseModel):
    """
    Schema for the scraper request payload.

    Attributes:
        page_limit (Optional[int]): Maximum number of pages to scrape. Must be greater than or equal to 1.
        proxy (Optional[HttpUrl]): Proxy URL to use for scraping.
    """
    page_limit: Optional[int] = Field(None, ge=1, description="Maximum number of pages to scrape")
    proxy: Optional[HttpUrl] = Field(None, description="Proxy URL to use for scraping")


class ScraperResponse(BaseModel):
    """
    Schema for the scraper response payload.

    Attributes:
        status (str): Status of the scraping operation.
        total_scraped (int): Total number of products scraped.
        total_updated (int): Number of products updated in the database.
        updated_products (List[ProductSchema]): List of updated products.
    """
    status: str = Field(..., description="Status of the scraping operation")
    total_scraped: int = Field(..., ge=0, description="Total number of products scraped")
    total_updated: int = Field(..., ge=0, description="Number of products updated in the database")
    updated_products: List[ProductSchema] = Field(default_factory=list, description="List of updated products")
