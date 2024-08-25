from typing import List
from app.models.product import Product
from app.repositories.base_repository import BaseRepository

class StorageService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def save_product(self, product: Product) -> None:
        await self.repository.save_product(product)

    async def save_products(self, products: List[Product]) -> None:
        await self.repository.save_products(products)

    async def get_all_products(self) -> List[Product]:
        return await self.repository.get_all_products()