import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException, Request

# 1. Set Environment BEFORE any app imports
os.environ["DB_URL"] = "sqlite:///:memory:"

# 2. Mock require_internal BEFORE app imports it
import app.api.v1.internal
from fastapi import Header, HTTPException

def mock_require_internal(x_api_key: str = Header(default="")):
    from app.core.config import INTERNAL_API_KEY
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid internal api key")
    return None

app.api.v1.internal.require_internal = mock_require_internal

# require_role no longer used in endpoints

# Now import the app
import app.db
from app.db import Base, init_db
from fastapi.testclient import TestClient
from app.main import app as fastapi_app

# 3. Configure the shared in-memory engine correctly
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, expire_on_commit=False, future=True)

# Monkeypatch the app's DB components
app.db.engine = test_engine
app.db.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    yield

@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client():
    fastapi_app.dependency_overrides.clear()
    return TestClient(fastapi_app)

@pytest.fixture
def boss_client(client):
    client.headers["X-API-Key"] = "change-me"
    client.headers["X-Executor-ID"] = "2"
    return client
