from abc import ABC, abstractmethod
from typing import List
from app.models.product import Product

class BaseRepository(ABC):
    @abstractmethod
    async def save_products(self, products: List[Product]) -> None:
        pass

    @abstractmethod
    async def get_all_products(self) -> List[Product]:
        pass