import json
import os
from typing import List
from app.repositories.base_repository import BaseRepository
from app.models.product import Product

class JsonFileRepository(BaseRepository):
    def __init__(self, file_path: str = "storage/products.json"):
        self.file_path = file_path

    async def save_products(self, products: List[Product]) -> None:
        existing_products = await self.get_all_products()
        product_dict = {p.id: p for p in existing_products}
        
        for product in products:
            product_dict[product.id] = product

        with open(self.file_path, "w") as f:
            json.dump([p.dict() for p in product_dict.values()], f, indent=2, default=str)

    async def get_all_products(self) -> List[Product]:
        if not os.path.exists(self.file_path):
            return []
        
        with open(self.file_path, "r") as f:
            data = json.load(f)
        
        return [Product(**item) for item in data]