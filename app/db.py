import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Reads from environment variable if present, else defaults to local SQLite file.
# To switch to Postgres later, just set DATABASE_URL env var, e.g.:
#   postgresql://user:password@localhost:5432/projectflow
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./projectflow.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
