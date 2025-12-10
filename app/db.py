import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("DB_URL", "postgresql://rbac:rbac@db:5432/rbac")

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Старт сервісу:
      1) створюємо таблиці
      2) додаємо дефолтні ролі, якщо їх немає
    """
    from app.models.role import Role, UserRole  # noqa: F401
    from app.initial_data import create_default_roles

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        create_default_roles(db)
    finally:
        db.close()