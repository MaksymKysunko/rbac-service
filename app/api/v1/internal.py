# app/api/v1/internal.py
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.domains.roles.service import RolesService
from app.domains.roles.models import Role, UserRole
from app.domains.roles.schemas import BossResponse
from app.core.config import INTERNAL_API_KEY

router = APIRouter()

def require_internal(x_api_key: str = Header(default="")) -> None:
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal api key",
        )

@router.get("/boss", response_model=BossResponse)
def get_boss_id(
    db: Session = Depends(get_db),
    _: None = Depends(require_internal),
):
    """
    Returns the user_id of the first user with 'boss' role.
    """
    srv = RolesService(db)
    boss_user_id = srv.get_first_user_with_role("boss")
    return BossResponse(user_id=boss_user_id)


@router.get("/settings/{key}")
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_internal),
):
    srv = RolesService(db)
    val = srv.get_setting(key)
    return {"key": key, "value": val}


@router.post("/settings/{key}")
def set_setting(
    key: str,
    body: dict, # {"value": "..."}
    db: Session = Depends(get_db),
    _: None = Depends(require_internal),
):
    srv = RolesService(db)
    srv.set_setting(key, str(body.get("value")).lower())
    return {"status": "ok"}


