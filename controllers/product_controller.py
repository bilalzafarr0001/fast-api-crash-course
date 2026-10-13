from math import ceil
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, contains_eager

from models.category import Category
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


# Helper: the category_id sent by the client must point to a real category
def check_category_exists(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category {category_id} does not exist",
        )


# Which columns the client may sort by (a safe list, so users can't sort by anything else)
SORT_COLUMNS = {
    "id": Product.id,
    "name": Product.name,
    "price": Product.price,
    "category": Category.name,  # sorted by the category's NAME (from the joined table)
}


# READ all, with search, filters, sorting and pagination.
# - category / category_id / in_stock: a product matches if it fits ANY one of the given ones.
# - search / min_price / max_price: always must match (AND), on top of the above.
def list_products(
    db: Session,
    category: Optional[str] = None,
    category_id: Optional[int] = None,
    in_stock: Optional[bool] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "id",
    order: str = "asc",
    page: int = 1,
    limit: int = 10,
) -> dict:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price",
        )

    # JOIN the categories table, and load each product's category in the same query
    # (without contains_eager, SQLAlchemy would run one extra query per product)
    query = db.query(Product).join(Product.category).options(contains_eager(Product.category))

    # category / category_id / in_stock (OR)
    conditions = []
    if category is not None:
        conditions.append(func.lower(Category.name) == category.lower())
    if category_id is not None:
        conditions.append(Product.category_id == category_id)
    if in_stock is not None:
        conditions.append(Product.in_stock == in_stock)
    if conditions:
        query = query.filter(or_(*conditions))

    # search in the name, ignoring upper/lower case (autoescape: "%" and "_" are plain text)
    if search:
        query = query.filter(Product.name.icontains(search, autoescape=True))

    # price range
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # total BEFORE slicing the page, so the client knows how many results exist
    total = query.count()

    # sorting (id is the tie-breaker so pages never repeat or skip items)
    column = SORT_COLUMNS[sort_by]
    primary = column.desc() if order == "desc" else column.asc()
    query = query.order_by(primary, Product.id.asc())

    # pagination: skip the previous pages, then take "limit" items
    items = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": ceil(total / limit),  # 0 results -> 0 pages
    }


# READ one
def get_product(db: Session, product_id: int) -> Product:
    return get_product_or_404(db, product_id)


# CREATE
def create_product(db: Session, data: ProductCreate, user: User) -> Product:
    check_category_exists(db, data.category_id)
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
    check_category_exists(db, data.category_id)
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
    # exclude_none: every column is required, so "field": null is ignored instead of crashing
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "category_id" in changes:
        check_category_exists(db, changes["category_id"])
    for field, value in changes.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


# DELETE
def delete_product(db: Session, product_id: int, user: User) -> None:
    product = get_owned_product_or_403(db, product_id, user)
    db.delete(product)
    db.commit()
