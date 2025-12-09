# app/db.py
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("DB_URL", "sqlite:///./rbac.db")

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


def get_db() -> Generator:
    """
    Аналог deps.get_db в idp/profile:
    даёт сессию, закрывает после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Создаём таблицы при старте сервиса (для dev).
    В тестах схема пересоздаётся через conftest, startup там не используется.
    """
    from app.models.role import Role, UserRole  # noqa: F401

    Base.metadata.create_all(bind=engine)
