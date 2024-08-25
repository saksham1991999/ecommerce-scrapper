from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.product import Product
from app.repositories.base_repository import BaseRepository
from app.models.db_models import ProductDB

class PostgresRepository(BaseRepository):
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def save_product(self, product: Product) -> None:
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