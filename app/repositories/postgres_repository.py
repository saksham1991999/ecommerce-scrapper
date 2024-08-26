from typing import List

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.models.db_models import ProductDB
from app.models.product import Product
from app.repositories.base_repository import BaseRepository


class PostgresRepository(BaseRepository):
    """
    PostgresRepository is responsible for managing product data in a PostgreSQL database.

    This class implements the methods defined in the BaseRepository for saving and retrieving products.
    """

    def __init__(self, db_url: str) -> None:
        """
        Initializes the PostgresRepository with the database URL.

        Args:
            db_url (str): The database connection URL.
        """
        self.engine = create_async_engine(db_url, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def save_product(self, product: Product) -> None:
        """
        Saves a single product to the PostgreSQL database.

        Args:
            product (Product): The Product instance to be saved.

        Raises:
            Exception: If there is an error during the save operation.
        """
        async with self.async_session() as session:
            db_product = ProductDB(
                id=product.id,
                source=product.source,
                source_id=product.source_id,
                product_title=product.product_title,
                product_price=product.product_price,
                path_to_image=product.path_to_image
            )
            session.add(db_product)
            await session.commit()

    async def save_products(self, products: List[Product]) -> None:
        """
        Saves a list of products to the PostgreSQL database.

        Args:
            products (List[Product]): A list of Product instances to be saved.

        Raises:
            Exception: If there is an error during the save operation.
        """
        async with self.async_session() as session:
            db_products = [
                ProductDB(
                    id=product.id,
                    source=product.source,
                    source_id=product.source_id,
                    product_title=product.product_title,
                    product_price=product.product_price,
                    path_to_image=product.path_to_image
                )
                for product in products
            ]
            session.add_all(db_products)
            await session.commit()

    async def get_all_products(self) -> List[Product]:
        """
        Retrieves all products from the PostgreSQL database.

        Returns:
            List[Product]: A list of Product instances retrieved from the database.

        Raises:
            Exception: If there is an error during the retrieval operation.
        """
        async with self.async_session() as session:
            result = await session.execute(select(ProductDB))
            db_products = result.scalars().all()
            return [
                Product(
                    id=db_product.id,
                    source=db_product.source,
                    source_id=db_product.source_id,
                    product_title=db_product.product_title,
                    product_price=db_product.product_price,
                    path_to_image=db_product.path_to_image
                )
                for db_product in db_products
            ]
