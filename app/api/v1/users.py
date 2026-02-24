from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import List

from app.db import get_db
from app.domains.roles.schemas import RoleChangeRequest, UserRolesResponse
from app.domains.roles.service import RolesService
from app.domains.punishments.service import PunishmentsService
from app.domains.punishments.schemas import (
    PunishmentCreate, 
    PunishmentResponse, 
    AmnestyRequest,
    UserPermissionsResponse
)
from .internal import require_internal
from fastapi import Header

router = APIRouter()


@router.post("/{user_id}/role/init", response_model=UserRolesResponse)
def init_user_role(
    user_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_internal),
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
    _ = Depends(require_internal),
):
    """
    Зміна ролі користувача (Boss only).
    """
    srv = RolesService(db)
    logging.info("[rbac] Changing user_id=%d role to %s (executor_id: unknown - internal call)", user_id, body.role)
    roles = srv.change_user_role(user_id, body.role)
    return UserRolesResponse(user_id=user_id, roles=roles)


@router.get("/{user_id}/roles", response_model=UserRolesResponse)
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_internal),
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
    _ = Depends(require_internal),
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
    _ = Depends(require_internal),
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
    _ = Depends(require_internal),
    x_executor_id: int = Header(..., alias="X-Executor-ID"),
):
    """
    Issue a chat-specific ban.
    """
    srv = PunishmentsService(db)
    # Force context
    body.user_id = user_id
    body.context = "chat"
    body.action = "ban"
    logging.info("[rbac] Issuing chat ban for user_id=%d (executor_id=%s, duration=%s, reason=%s)", 
                 user_id, x_executor_id, body.duration_hours, body.reason)
    return srv.add_punishment(body, boss_id=x_executor_id)


@router.post("/amnesty/{punishment_id}")
def grant_amnesty(
    punishment_id: int,
    body: AmnestyRequest,
    db: Session = Depends(get_db),
    _ = Depends(require_internal),
    x_executor_id: int = Header(..., alias="X-Executor-ID"),
):
    """
    Clear a specific violation.
    """
    srv = PunishmentsService(db)
    logging.info("[rbac] Granting amnesty for punishment_id=%d (executor_id=%s, reason=%s)", 
                 punishment_id, x_executor_id, body.reason)
    success = srv.grant_amnesty(punishment_id, boss_id=x_executor_id, reason=body.reason)
    if not success:
        raise HTTPException(status_code=404, detail="Punishment not found")
    return {"status": "ok"}
