from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.category import Category
from models.product import Product
from schemas.category import CategoryCreate, CategoryUpdate


# Controller = the logic that talks to the database.

# Helper: get a category by id, or raise a 404 error
def get_category_or_404(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Helper: names must be unique (ignoring upper/lower case), except for the category itself
def _check_name_unique(db: Session, name: str, current_id: int | None = None) -> None:
    other = db.query(Category).filter(func.lower(Category.name) == name.lower()).first()
    if other and other.id != current_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Category name already exists")


# READ all
def list_categories(db: Session) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


# READ one
def get_category(db: Session, category_id: int) -> Category:
    return get_category_or_404(db, category_id)


# CREATE
def create_category(db: Session, data: CategoryCreate) -> Category:
    name = data.name.strip()
    _check_name_unique(db, name)
    category = Category(name=name, description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# UPDATE (partial): changes only the fields that were sent
def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = get_category_or_404(db, category_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("name") is None:
        changes.pop("name", None)  # name is required in the table, so it can't become null
    else:
        changes["name"] = changes["name"].strip()
        _check_name_unique(db, changes["name"], category.id)
    for field, value in changes.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


# DELETE: refused while the category still has products
def delete_category(db: Session, category_id: int) -> None:
    category = get_category_or_404(db, category_id)
    in_use = db.query(Product).filter(Product.category_id == category.id).count()
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category has {in_use} product(s). Move or delete them first.",
        )
    db.delete(category)
    db.commit()
