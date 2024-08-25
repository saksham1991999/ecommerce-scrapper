from sqlalchemy import Column, String, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductDB(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    product_title = Column(String, nullable=False)
    product_price = Column(Numeric, nullable=False)
    path_to_image = Column(String, nullable=False)