from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

class ScrapingJob(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier for the scraping job")
    target_url: HttpUrl = Field(..., description="URL of the website to scrape")
    page_limit: Optional[int] = Field(default=None, description="Maximum number of pages to scrape")
    proxy: Optional[str] = Field(default=None, description="Proxy server to use for scraping")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of job creation")
    status: str = Field(default="pending", description="Current status of the scraping job")
    products_scraped: int = Field(default=0, description="Number of products scraped in this job")
    products_updated: int = Field(default=0, description="Number of products updated in the database")

    class Config:
        json_schema_extra = {
            "example": {
                "target_url": "https://dentalstall.com/shop/",
                "page_limit": 5,
                "proxy": "http://proxy.example.com:8080",
                "status": "pending",
                "products_scraped": 0,
                "products_updated": 0
            }
        }