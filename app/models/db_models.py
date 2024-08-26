from sqlalchemy import Column, Numeric, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductDB(Base):
    """
    Represents the Product database model.

    Attributes:
        id (str): The unique identifier for the product.
        source (str): The source of the product.
        source_id (str): The unique identifier from the source.
        product_title (str): The title of the product.
        product_price (Numeric): The price of the product.
        path_to_image (str): The file path or URL to the product image.
    """
    __tablename__ = "products"

    id: str = Column(String, primary_key=True)
    source: str = Column(String, nullable=False)
    source_id: str = Column(String, nullable=False)
    product_title: str = Column(String, nullable=False)
    product_price: Numeric = Column(Numeric, nullable=False)
    path_to_image: str = Column(String, nullable=False)
