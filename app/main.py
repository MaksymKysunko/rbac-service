# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db import init_db
from app.api.v1.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # аналог startup()
    init_db()
    yield
    # аналог shutdown()
    # (пока ничего не нужно)


app = FastAPI(title="RBAC Service", lifespan=lifespan)

app.include_router(
    users_router,
    prefix="/api/rbac/users",
    tags=["rbac-users"],
)
