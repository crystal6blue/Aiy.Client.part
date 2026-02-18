from utils.logger_conf import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://todo_user:password@localhost:5432/todo_db"

engine = create_engine(
    DATABASE_URL,
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