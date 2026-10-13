from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers import product_controller
from core.dependencies import get_current_user
from database import get_db
from models.user import User
from schemas.product import ProductCreate, ProductResponse, ProductUpdate

# Router = defines the URLs. Each route just calls the controller.
# Every product route requires a logged-in user (valid Bearer token).
router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)],
)


# READ all: GET /products (optionally ?category=Kitchen&in_stock=true)
@router.get("", response_model=list[ProductResponse])
def list_products(
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    return product_controller.list_products(db, category, in_stock)


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
