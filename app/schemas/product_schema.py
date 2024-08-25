from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ProductSchema(BaseModel):
    id: str = Field(..., description="Unique identifier constructed using source and source_id")
    source: str = Field(..., description="Complete domain of the URL")
    source_id: str = Field(..., description="ID received from scraping")
    product_title: str = Field(..., description="Title of the product")
    product_price: Decimal = Field(..., description="Price of the product")
    path_to_image: str = Field(..., description="Path to the product image on local storage")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the product was first scraped")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the product was last updated")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "dentalstall.com_12345",
                "source": "https://dentalstall.com",
                "source_id": "12345",
                "product_title": "Dental Implant Kit",
                "product_price": 199.99,
                "path_to_image": "/path/to/images/dental_implant_kit.jpg",
                "created_at": "2023-04-01T12:00:00",
                "updated_at": "2023-04-01T12:00:00"
            }
        }


class ProductCreateSchema(BaseModel):
    source: str = Field(..., description="Complete domain of the URL")
    source_id: str = Field(..., description="ID received from scraping")
    product_title: str = Field(..., description="Title of the product")
    product_price: Decimal = Field(..., description="Price of the product")
    path_to_image: str = Field(..., description="Path to the product image on local storage")


class ProductUpdateSchema(BaseModel):
    product_title: Optional[str] = Field(None, description="Title of the product")
    product_price: Optional[Decimal] = Field(None, description="Price of the product")
    path_to_image: Optional[str] = Field(None, description="Path to the product image on local storage")


class ProductResponseSchema(ProductSchema):
    pass