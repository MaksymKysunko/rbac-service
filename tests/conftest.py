# tests/conftest.py
import os
import pathlib

import pytest
from fastapi.testclient import TestClient

# Путь до тестовой БД (файловая SQLite)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
TEST_DB_PATH = BASE_DIR / "test_rbac.db"

# Подменяем DB_URL ДО импорта app.db / app.main
os.environ["DB_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.db import Base, engine, SessionLocal, get_db  # noqa: E402
from app.main import app                               # noqa: E402
from app import models                                 # noqa: F401,E402  # чтобы Role/UserRole попали в Base.metadata


def _reset_database():
    """
    Перед каждым тестом полностью пересоздаём схему.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """
    Автоматически выполняется перед каждым тестом:
      - дропает и пересоздаёт таблицы.
    """
    _reset_database()
    yield


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подменяем зависимость БД в FastAPI
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    """
    Как в профайле: готовый TestClient(app).
    """
    return TestClient(app)
