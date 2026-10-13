from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# SQLAlchemy model: describes the "products" TABLE in PostgreSQL
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)  # auto-incremented by the DB
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    in_stock = Column(Boolean, nullable=False, default=True)

    # Foreign key: every product belongs to one user
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner = relationship("User", back_populates="products")
