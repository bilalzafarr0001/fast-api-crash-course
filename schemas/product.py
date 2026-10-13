from typing import Optional

from pydantic import BaseModel, ConfigDict


# Pydantic schemas define the shape of API request/response data.
# (Different from models/, which define the database table.)

# Data the client SENDS when creating a product (no id, the DB generates it)
class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool = True


# Data the client sends when partially updating (PATCH): every field is optional
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    in_stock: Optional[bool] = None


# Data the server RETURNS: same fields + id + the owner's id
class ProductResponse(ProductCreate):
    id: int
    owner_id: int

    # Allows reading data straight from a SQLAlchemy object
    model_config = ConfigDict(from_attributes=True)
