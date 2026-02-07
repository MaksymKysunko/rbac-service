# app/api/v1/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.domains.roles.schemas import RoleChangeRequest, UserRolesResponse
from app.domains.roles.service import RolesService, require_role

router = APIRouter()


@router.post("/{user_id}/role/init", response_model=UserRolesResponse)
def init_user_role(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Ініціалізація ролі при створенні користувача.
    """
    srv = RolesService(db)
    roles = srv.init_user_role(user_id)
    return UserRolesResponse(user_id=user_id, roles=roles)


@router.put("/{user_id}/role", response_model=UserRolesResponse)
def change_user_role(
    user_id: int,
    body: RoleChangeRequest,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_role("boss")),
):
    """
    Зміна ролі користувача (Boss only).
    """
    srv = RolesService(db)
    roles = srv.change_user_role(user_id, body.role)
    return UserRolesResponse(user_id=user_id, roles=roles)


@router.get("/{user_id}/roles", response_model=UserRolesResponse)
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserRolesResponse:
    """
    Повертає поточну роль користувача.
    """
    srv = RolesService(db)
    role_names = srv.get_user_role_names(user_id)
    return UserRolesResponse(user_id=user_id, roles=role_names)
