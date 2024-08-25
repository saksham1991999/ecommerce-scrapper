from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class ScrapingJobSchema(BaseModel):
    page_limit: Optional[int] = Field(default=None, ge=1, description="Number of pages to scrape")
    proxy: Optional[HttpUrl] = Field(default=None, description="Proxy URL to use for scraping")

    class Config:
        json_schema_extra = {
            "example": {
                "page_limit": 5,
                "proxy": "http://proxy.example.com:8080"
            }
        }


class ScrapingJobResultSchema(BaseModel):
    total_products_scraped: int = Field(..., ge=0, description="Total number of products scraped")
    total_products_updated: int = Field(..., ge=0, description="Total number of products updated in the database")
    status: str = Field(..., description="Status of the scraping job")

    class Config:
        json_schema_extra = {
            "example": {
                "total_products_scraped": 100,
                "total_products_updated": 50,
                "status": "Completed successfully"
            }
        }