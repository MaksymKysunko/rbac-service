from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.domains.roles.schemas import RoleChangeRequest, UserRolesResponse
from app.domains.roles.service import RolesService
from app.auth import require_role
from app.domains.punishments.service import PunishmentsService
from app.domains.punishments.schemas import (
    PunishmentCreate, 
    PunishmentResponse, 
    AmnestyRequest,
    UserPermissionsResponse
)

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


@router.get("/{user_id}/permissions", response_model=UserPermissionsResponse)
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Combined roles and active punishments.
    """
    roles_srv = RolesService(db)
    punish_srv = PunishmentsService(db)
    
    return UserPermissionsResponse(
        user_id=user_id,
        roles=roles_srv.get_user_role_names(user_id),
        limits=punish_srv.get_active_limits(user_id)
    )


@router.get("/{user_id}/moderation-history", response_model=List[PunishmentResponse])
def get_moderation_history(
    user_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_role("boss")),
):
    """
    Full history for the Boss UI.
    """
    srv = PunishmentsService(db)
    return srv.get_moderation_history(user_id)


@router.post("/{user_id}/chat-ban", response_model=PunishmentResponse)
def issue_chat_ban(
    user_id: int,
    body: PunishmentCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_role("boss")),
):
    """
    Issue a chat-specific ban.
    """
    srv = PunishmentsService(db)
    # Force context
    body.user_id = user_id
    body.context = "chat"
    body.action = "ban"
    return srv.add_punishment(body, boss_id=int(claims["sub"]))


@router.post("/amnesty/{punishment_id}")
def grant_amnesty(
    punishment_id: int,
    body: AmnestyRequest,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_role("boss")),
):
    """
    Clear a specific violation.
    """
    srv = PunishmentsService(db)
    success = srv.grant_amnesty(punishment_id, boss_id=int(claims["sub"]), reason=body.reason)
    if not success:
        raise HTTPException(status_code=404, detail="Punishment not found")
    return {"status": "ok"}
