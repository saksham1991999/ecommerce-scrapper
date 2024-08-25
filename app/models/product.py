from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
import os

class Product(BaseModel):
    id: str = Field(..., description="Unique identifier constructed using source and source_id")
    source: str = Field(..., description="Complete domain of the URL")
    source_id: str = Field(..., description="ID received from scraping")
    product_title: str = Field(..., min_length=1, max_length=255, description="Title of the product")
    product_price: Decimal = Field(..., ge=0, description="Price of the product")
    path_to_image: str = Field(..., description="Local path to the product image")

    @validator('product_price')
    def validate_price(cls, v):
        return Decimal(round(v, 2))

    # @validator('path_to_image')
    # def validate_image_path(cls, v):
    #     if not os.path.isfile(v):
    #         raise ValueError(f"Image file does not exist: {v}")
    #     return v

    class Config:
        json_encoders = {Decimal: str}