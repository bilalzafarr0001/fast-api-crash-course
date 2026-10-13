from fastapi import FastAPI

import models  # noqa: F401  (imported so the tables are registered on Base)
from database import Base, engine
from routers import auth_router, category_router, product_router, user_router

# Create the tables in PostgreSQL if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(category_router.router)
app.include_router(product_router.router)


@app.get("/")
def home():
    return "Welcome to the home page bilal"
