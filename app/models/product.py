import os
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator


class Product(BaseModel):
    """
    Represents a product with its details.

    Attributes:
        id (str): Unique identifier constructed using source and source_id.
        source (str): Complete domain of the URL.
        source_id (str): ID received from scraping.
        product_title (str): Title of the product.
        product_price (Decimal): Price of the product, must be non-negative.
        path_to_image (str): Local path to the product image.
    """
    id: str = Field(..., description="Unique identifier constructed using source and source_id")
    source: str = Field(..., description="Complete domain of the URL")
    source_id: str = Field(..., description="ID received from scraping")
    product_title: str = Field(..., min_length=1, max_length=255, description="Title of the product")
    product_price: Decimal = Field(..., ge=0, description="Price of the product")
    path_to_image: str = Field(..., description="Local path to the product image")

    @validator('product_price')
    def validate_price(cls, v: Decimal) -> Decimal:
        """
        Validates the product price to ensure it is rounded to two decimal places.

        Args:
            cls: The class itself.
            v (Decimal): The price value to validate.

        Returns:
            Decimal: The validated price rounded to two decimal places.
        """
        return Decimal(round(v, 2))

    @validator('path_to_image')
    def validate_image_path(cls, v: str) -> str:
        """
        Validates the path to the image file to ensure it exists.

        Args:
            cls: The class itself.
            v (str): The path to the image file.

        Raises:
            ValueError: If the image file does not exist.

        Returns:
            str: The validated image path.
        """
        if not os.path.isfile(v):
            raise ValueError(f"Image file does not exist: {v}")
        return v

    class Config:
        """Configuration for the Pydantic model."""
        json_encoders = {Decimal: str}
