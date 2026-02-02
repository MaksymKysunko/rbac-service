# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from club_shared import install_monitoring, setup_logging

setup_logging("rbac-service")

from app.db import init_db
from app.api.v1.users import router as users_router
from app.api.v1.internal import router as internal_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # аналог startup()
    init_db()
    yield
    # аналог shutdown()
    # (пока ничего не нужно)


app = FastAPI(title="RBAC Service", lifespan=lifespan)
install_monitoring(app, "rbac-service")

app.include_router(
    users_router,
    prefix="/api/rbac/users",
    tags=["rbac-users"],
)

app.include_router(
    internal_router,
    prefix="/api/rbac/internal",
    tags=["rbac-internal"],
)
