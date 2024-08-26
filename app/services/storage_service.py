from typing import List

from app.models.product import Product
from app.repositories.base_repository import BaseRepository


class StorageService:
    """
    A service class for managing product storage operations.
    """

    def __init__(self, repository: BaseRepository):
        """
        Initialize the StorageService with a repository.

        Args:
            repository (BaseRepository): The repository to use for storage operations.
        """
        self.repository: BaseRepository = repository

    async def save_product(self, product: Product) -> None:
        """
        Save a single product to the storage.

        Args:
            product (Product): The product to save.

        Returns:
            None
        """
        await self.repository.save_product(product)

    async def save_products(self, products: List[Product]) -> None:
        """
        Save multiple products to the storage.

        Args:
            products (List[Product]): A list of products to save.

        Returns:
            None
        """
        await self.repository.save_products(products)

    async def get_all_products(self) -> List[Product]:
        """
        Retrieve all products from the storage.

        Returns:
            List[Product]: A list of all products in the storage.
        """
        return await self.repository.get_all_products()
