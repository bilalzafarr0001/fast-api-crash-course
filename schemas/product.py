from typing import Optional

from pydantic import BaseModel, ConfigDict

from schemas.category import CategoryResponse


# Pydantic schemas define the shape of API request/response data.
# (Different from models/, which define the database table.)

# Data the client SENDS when creating a product (no id, the DB generates it)
class ProductCreate(BaseModel):
    name: str
    price: float
    category_id: int  # id of an existing category (see /categories)
    in_stock: bool = True


# Data the client sends when partially updating (PATCH): every field is optional
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    in_stock: Optional[bool] = None


# Data the server RETURNS: same fields + id + the owner's id + the full category
class ProductResponse(ProductCreate):
    id: int
    owner_id: int
    category: CategoryResponse

    # Allows reading data straight from a SQLAlchemy object
    model_config = ConfigDict(from_attributes=True)


# One page of products + the numbers a frontend needs to build "next/previous" buttons
class ProductListResponse(BaseModel):
    items: list[ProductResponse]  # the products on this page
    total: int  # how many products match the filters (all pages)
    page: int  # current page number
    limit: int  # products per page
    pages: int  # total number of pages
