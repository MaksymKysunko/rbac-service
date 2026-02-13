import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException, Request

# 1. Set Environment BEFORE any app imports
os.environ["DB_URL"] = "sqlite:///:memory:"

# 2. Mock require_role factor BEFORE app imports it to have stable function objects for overrides
import app.domains.roles.service
_role_checkers = {}

def require_role_patched(role: str):
    if role not in _role_checkers:
        def role_checker(request: Request):
            # Mock original logic: check request.state.principal
            raise HTTPException(status_code=401, detail="Authentication required")
        _role_checkers[role] = role_checker
    return _role_checkers[role]

app.domains.roles.service.require_role = require_role_patched

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
    # Use the stable checker from our patched factory
    checker = app.domains.roles.service.require_role("boss")
    
    def mock_require_boss(request: Request):
        return {"user_id": 2, "username": "boss", "role": "boss"}
    
    fastapi_app.dependency_overrides[checker] = mock_require_boss
    client.headers["Authorization"] = "Bearer boss"
    return client
