# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_microkit import (
    setup_logging, 
    install_monitoring, 
    install_contract_exceptions, 
    TraceIdMiddleware
)

setup_logging("rbac-service")

from app.db import init_db
from app.api.v1.users import router as users_router
from app.api.v1.internal import router as internal_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # аналог startup()
    init_db()
    try:
        from app.migrations import migrate_punishments_table
        migrate_punishments_table()
    except Exception as e:
        import logging
        logging.error(f"Migration failed: {e}")
    yield
    # аналог shutdown()
    # (пока ничего не нужно)


app = FastAPI(title="RBAC Service", lifespan=lifespan)

# 1. Standardized Infrastructure
app.add_middleware(TraceIdMiddleware)
install_monitoring(app, "rbac-service")
install_contract_exceptions(app)

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

@app.get("/api/healthz", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "rbac-service"}
