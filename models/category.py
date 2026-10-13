from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


# SQLAlchemy model: describes the "categories" TABLE in PostgreSQL
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # One category has many products
    products = relationship("Product", back_populates="category")
