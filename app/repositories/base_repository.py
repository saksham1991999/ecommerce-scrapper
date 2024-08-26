from abc import ABC, abstractmethod
from typing import List

from app.models.product import Product


class BaseRepository(ABC):
    """
    Abstract base class for product repository.

    This class defines the interface for product data access methods.
    Implementations of this class should provide the actual data access logic.
    """

    @abstractmethod
    async def save_products(self, products: List[Product]) -> None:
        """
        Save a list of products to the database.

        Args:
            products (List[Product]): A list of Product instances to be saved.

        Raises:
            Exception: If there is an error during the save operation.
        """
        pass

    @abstractmethod
    async def save_product(self, product: Product) -> None:
        """
        Save a single product to the database.

        Args:
            product (Product): A Product instance to be saved.

        Raises:
            Exception: If there is an error during the save operation.
        """
        pass

    @abstractmethod
    async def get_all_products(self) -> List[Product]:
        """
        Retrieve all products from the database.

        Returns:
            List[Product]: A list of Product instances.

        Raises:
            Exception: If there is an error during the retrieval operation.
        """
        pass
