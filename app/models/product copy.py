from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from urllib.parse import urlparse


class Product(BaseModel):
    id: str = Field(..., description="Unique identifier constructed using source and source_id")
    source: str = Field(..., description="Complete domain of the URL")
    source_id: str = Field(..., description="ID received from scraping")
    product_title: str = Field(..., description="Title of the product")
    product_price: Decimal = Field(..., description="Price of the product", ge=0)
    path_to_image: str = Field(..., description="Path to the image on local storage")

    @classmethod
    def create(cls, source: str, source_id: str, product_title: str, product_price: Decimal, path_to_image: str) -> 'Product':
        domain = urlparse(source).netloc
        product_id = f"{domain}_{source_id}"
        return cls(
            id=product_id,
            source=domain,
            source_id=source_id,
            product_title=product_title,
            product_price=product_price,
            path_to_image=path_to_image
        )

    class Config:
        populate_by_name = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }