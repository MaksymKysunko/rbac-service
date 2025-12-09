# app/api/v1/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Role, UserRole
from app.schemas import UserRoleCreate, UserRolesResponse

router = APIRouter()


@router.post("/{user_id}/roles", response_model=UserRolesResponse)
def add_role_to_user(
    user_id: str,
    payload: UserRoleCreate,
    db: Session = Depends(get_db),
) -> UserRolesResponse:
    # 1. Находим или создаём роль
    role = db.query(Role).filter(Role.name == payload.role_name).first()
    if role is None:
        role = Role(name=payload.role_name)
        db.add(role)
        db.commit()
        db.refresh(role)

    # 2. Проверяем, нет ли уже такой связи user↔role
    mapping = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
        .first()
    )

    if mapping is None:
        mapping = UserRole(user_id=user_id, role_id=role.id)
        db.add(mapping)
        db.commit()

    # 3. Возвращаем все роли пользователя
    roles = (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    role_names = [r.name for r in roles]

    return UserRolesResponse(user_id=user_id, roles=role_names)


@router.get("/{user_id}/roles", response_model=UserRolesResponse)
def get_user_roles(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserRolesResponse:
    roles = (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    role_names = [r.name for r in roles]

    return UserRolesResponse(user_id=user_id, roles=role_names)
