# app/api/v1/internal.py
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.role import Role, UserRole
from app.core.config import INTERNAL_API_KEY
from pydantic import BaseModel

router = APIRouter()

class BossResponse(BaseModel):
    user_id: int
    username: str = "boss" # Default if we don't have it in RBAC

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
    Used by other services (like deals-service) to identify the arbitrator.
    """
    # Find the 'boss' role
    boss_role = db.query(Role).filter(Role.name == "boss").first()
    if not boss_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss role not defined in system",
        )

    # Find the first user with this role
    mapping = db.query(UserRole).filter(UserRole.role_id == boss_role.id).first()
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with boss role",
        )

    return BossResponse(user_id=mapping.user_id)
