from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from models.product import Product
from models.user import User
from schemas.user import PasswordChange, UserCreate, UserUpdate


# Controller = the logic that talks to the database.

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(func.lower(User.email) == email.lower()).first()


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(func.lower(User.username) == username.lower()).first()


# Helper: make sure username/email are not already used by ANOTHER user
def _check_unique(
    db: Session, username: str | None, email: str | None, current_id: int | None = None
) -> None:
    if username is not None:
        other = get_by_username(db, username)
        if other and other.id != current_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    if email is not None:
        other = get_by_email(db, email)
        if other and other.id != current_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")


# REGISTER
def register_user(db: Session, data: UserCreate) -> User:
    _check_unique(db, data.username, data.email)
    user = User(
        username=data.username,
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# LOGIN: the login form's "username" field can be a username OR an email
def authenticate_user(db: Session, identifier: str, password: str) -> User:
    user = get_by_username(db, identifier) or get_by_email(db, identifier)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")
    return user


# UPDATE profile (only the fields that were sent)
def update_user(db: Session, user: User, data: UserUpdate) -> User:
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "email" in changes:
        changes["email"] = changes["email"].lower()
    _check_unique(db, changes.get("username"), changes.get("email"), user.id)
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# CHANGE password
def change_password(db: Session, user: User, data: PasswordChange) -> None:
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.hashed_password = hash_password(data.new_password)
    db.commit()


# LIST the products owned by a user
def list_user_products(db: Session, user: User) -> list[Product]:
    return db.query(Product).filter(Product.owner_id == user.id).order_by(Product.id).all()


# DELETE account (their products are deleted too, by the cascade)
def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
