import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Updated to your PostgreSQL credentials
DATABASE_URL = "postgresql://todo_user:password@localhost:5432/todo_db"

engine = create_engine(
    DATABASE_URL,
    # 'check_same_thread' is only for SQLite; remove it for PostgreSQL
    echo=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()