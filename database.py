import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Read DATABASE_URL from the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Add it to your .env file.")

# The engine is the actual connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# Each request gets its own session (a conversation with the database)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# All SQLAlchemy models inherit from this Base
Base = declarative_base()


# Dependency: gives a DB session to a route, and closes it afterwards
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
