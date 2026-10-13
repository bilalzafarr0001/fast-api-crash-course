from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from models.product import Product
from models.user import User
from schemas.product import ProductCreate, ProductUpdate


# Controller = the logic that talks to the database.
# The router calls these functions; they do the actual work.

# Helper: get a product by id, or raise a 404 error
def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Helper: same as above, but also checks the logged-in user owns the product
def get_owned_product_or_403(db: Session, product_id: int, user: User) -> Product:
    product = get_product_or_404(db, product_id)
    if product.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own products",
        )
    return product


# READ all. With both filters, a product matches if it fits EITHER one.
def list_products(
    db: Session, category: Optional[str] = None, in_stock: Optional[bool] = None
) -> list[Product]:
    query = db.query(Product)

    conditions = []
    if category is not None:
        conditions.append(func.lower(Product.category) == category.lower())
    if in_stock is not None:
        conditions.append(Product.in_stock == in_stock)

    if conditions:
        query = query.filter(or_(*conditions))

    return query.order_by(Product.id).all()


# READ one
def get_product(db: Session, product_id: int) -> Product:
    return get_product_or_404(db, product_id)


# CREATE
def create_product(db: Session, data: ProductCreate, user: User) -> Product:
    product = Product(**data.model_dump(), owner_id=user.id)
    db.add(product)
    db.commit()
    db.refresh(product)  # loads the generated id
    return product


# UPDATE (full): replaces all fields
def replace_product(
    db: Session, product_id: int, data: ProductCreate, user: User
) -> Product:
    product = get_owned_product_or_403(db, product_id, user)
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


# UPDATE (partial): changes only the fields that were sent
def update_product(
    db: Session, product_id: int, data: ProductUpdate, user: User
) -> Product:
    product = get_owned_product_or_403(db, product_id, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


# DELETE
def delete_product(db: Session, product_id: int, user: User) -> None:
    product = get_owned_product_or_403(db, product_id, user)
    db.delete(product)
    db.commit()
