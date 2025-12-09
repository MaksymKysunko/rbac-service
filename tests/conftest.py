import os
import pathlib

import pytest
from fastapi.testclient import TestClient

# Шлях до тестової БД (файлова SQLite)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
TEST_DB_PATH = BASE_DIR / "test_rbac.db"

# Підміняємо DB_URL ДО імпорту app.db / app.main
os.environ["DB_URL"] = f"sqlite:///{TEST_DB_PATH}"

from app.db import Base, engine, SessionLocal, get_db, init_db  # noqa: E402
from app.main import app                                       # noqa: E402
from app import models                                         # noqa: F401,E402  # щоб Role/UserRole зареєструвались
from app.services import get_claims                            # noqa: E402


def _reset_database():
    """
    Перед кожним тестом:
      1) дропаєм усі таблиці
      2) викликаємо init_db(), який і створює схему, і сідає дефолтні ролі
    """
    Base.metadata.drop_all(bind=engine)
    init_db()


@pytest.fixture(autouse=True)
def setup_database():
    _reset_database()
    yield


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_claims():
    """
    У тестах не ганяємо реальний JWT/JWKS.
    Просто вважаємо, що до нас прийшов токен:
      sub = "1"
      role = "boss"
    """
    return {"sub": "1", "role": "boss"}


# Підміняємо залежності в FastAPI
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_claims] = override_get_claims


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
