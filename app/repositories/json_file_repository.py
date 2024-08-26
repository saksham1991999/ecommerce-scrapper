import json
import os
from typing import List

from app.models.product import Product
from app.repositories.base_repository import BaseRepository


class JsonFileRepository(BaseRepository):
    """
    A repository for managing products stored in a JSON file.

    This class provides methods to save and retrieve products from a specified JSON file.
    """

    def __init__(self, file_path: str = "storage/products.json"):
        """
        Initializes the JsonFileRepository with the given file path.

        Args:
            file_path (str): The path to the JSON file where products are stored.
        """
        self.file_path = file_path

    async def save_products(self, products: List[Product]) -> None:
        """
        Saves a list of products to the JSON file, updating existing products.

        Args:
            products (List[Product]): A list of Product instances to save.
        """
        existing_products = await self.get_all_products()
        product_dict = {p.id: p for p in existing_products}

        for product in products:
            product_dict[product.id] = product

        await self._write_to_file(list(product_dict.values()))

    async def save_product(self, product: Product) -> None:
        """
        Saves a single product to the JSON file, updating if it already exists.

        Args:
            product (Product): The Product instance to save.
        """
        existing_products = await self.get_all_products()
        product_dict = {p.id: p for p in existing_products}
        product_dict[product.id] = product
        await self._write_to_file(list(product_dict.values()))

    async def get_all_products(self) -> List[Product]:
        """
        Retrieves all products from the JSON file.

        Returns:
            List[Product]: A list of Product instances retrieved from the file.
        """
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r") as f:
            data = json.load(f)

        return [Product(**item) for item in data]

    async def _write_to_file(self, products: List[Product]) -> None:
        """
        Writes a list of products to the JSON file.

        Args:
            products (List[Product]): A list of Product instances to write to the file.
        """
        with open(self.file_path, "w") as f:
            json.dump([p.dict() for p in products], f, indent=2, default=str)
