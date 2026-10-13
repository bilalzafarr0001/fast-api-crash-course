from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers import category_controller
from core.dependencies import get_current_user
from database import get_db
from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

# Router = defines the URLs. Each route just calls the controller.
# Every category route requires a logged-in user.
router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
)


# READ all: GET /categories
@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return category_controller.list_categories(db)


# READ one: GET /categories/1
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_controller.get_category(db, category_id)


# CREATE: POST /categories
@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_controller.create_category(db, data)


# UPDATE (partial): PATCH /categories/1
@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    return category_controller.update_category(db, category_id, data)


# DELETE: DELETE /categories/1 (409 if it still has products)
@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_controller.delete_category(db, category_id)
