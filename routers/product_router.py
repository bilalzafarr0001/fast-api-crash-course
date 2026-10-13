from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import product_controller
from core.dependencies import get_current_user
from database import get_db
from models.user import User
from schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

# Router = defines the URLs. Each route just calls the controller.
# Every product route requires a logged-in user (valid Bearer token).
router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)],
)


# READ all: GET /products
# Filters : ?category=Kitchen  ?category_id=2  ?in_stock=true  ?search=pan  ?min_price=10  ?max_price=50
# Sorting : ?sort_by=price&order=desc
# Paging  : ?page=2&limit=5
@router.get("", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = Query(None, description="Category NAME, e.g. Kitchen"),
    category_id: Optional[int] = Query(None, description="Category id, e.g. 2"),
    in_stock: Optional[bool] = None,
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Text to look for in the product name"),
    min_price: Optional[float] = Query(None, ge=0, description="Lowest price"),
    max_price: Optional[float] = Query(None, ge=0, description="Highest price"),
    sort_by: Literal["id", "name", "price", "category"] = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    limit: int = Query(10, ge=1, le=100, description="Products per page (max 100)"),
    db: Session = Depends(get_db),
):
    return product_controller.list_products(
        db, category, category_id, in_stock, search, min_price, max_price, sort_by, order, page, limit
    )


# READ one: GET /products/1
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_controller.get_product(db, product_id)


# CREATE: POST /products (the logged-in user becomes the owner)
@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_controller.create_product(db, data, current_user)


# UPDATE (full): PUT /products/1 (owner only)
@router.put("/{product_id}", response_model=ProductResponse)
def replace_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_controller.replace_product(db, product_id, data, current_user)


# UPDATE (partial): PATCH /products/1 (owner only)
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_controller.update_product(db, product_id, data, current_user)


# DELETE: DELETE /products/1 (owner only)
@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product_controller.delete_product(db, product_id, current_user)
