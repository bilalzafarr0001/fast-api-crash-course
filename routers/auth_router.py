from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from controllers import user_controller
from core.email import send_welcome_email
from core.security import create_access_token
from database import get_db
from schemas.user import Token, UserCreate, UserResponse

# Router = defines the URLs. Each route just calls the controller.
router = APIRouter(prefix="/auth", tags=["Auth"])


# REGISTER: POST /auth/register (also sends a welcome email)
@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    data: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    user = user_controller.register_user(db, data)
    # Sent after the response is returned, so registration doesn't wait for the email
    background_tasks.add_task(send_welcome_email, user.email, user.username)
    return user


# LOGIN: POST /auth/login (form fields: username, password) -> JWT token
@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_controller.authenticate_user(db, form.username, form.password)
    return Token(access_token=create_access_token(user.id))
