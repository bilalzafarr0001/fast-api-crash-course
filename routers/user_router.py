from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers import user_controller
from core.dependencies import get_current_user
from database import get_db
from models.user import User
from schemas.product import ProductResponse
from schemas.user import PasswordChange, UserResponse, UserUpdate

# All routes here need a valid token and only work on the logged-in user.
router = APIRouter(prefix="/users", tags=["Users"])


# GET /users/me
@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


# PATCH /users/me
@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_controller.update_user(db, current_user, data)


# PUT /users/me/password
@router.put("/me/password", status_code=204)
def change_my_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_controller.change_password(db, current_user, data)


# GET /users/me/products: only my products
@router.get("/me/products", response_model=list[ProductResponse])
def read_my_products(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return user_controller.list_user_products(db, current_user)


# DELETE /users/me: delete my account (and my products)
@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    user_controller.delete_user(db, current_user)
