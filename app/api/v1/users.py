# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Role, UserRole
from app.schemas import RoleChangeRequest, UserRolesResponse
from app.services import get_claims, get_principal, require_role

router = APIRouter()


def _get_role_by_name(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown role: {name}",
        )
    return role


@router.post("/{user_id}/role/init", response_model=UserRolesResponse)
def init_user_role(
    user_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_claims),
):
    """
    Ініціалізація ролі при створенні користувача.
    За замовчуванням усі стають 'soldier'.
    Вимагає валідний JWT від IdP (але без перевірки конкретної ролі).
    """
    soldier_role = _get_role_by_name(db, "soldier")

    mapping = db.query(UserRole).filter(UserRole.user_id == user_id).first()
    if mapping is None:
        mapping = UserRole(user_id=user_id, role_id=soldier_role.id)
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        roles = ["soldier"]
    else:
        # якщо вже є роль – просто повертаємо поточну
        roles = (
            db.query(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        roles = [r[0] for r in roles]

    return UserRolesResponse(user_id=user_id, roles=roles)


@router.put("/{user_id}/role", response_model=UserRolesResponse)
def change_user_role(
    user_id: int,
    body: RoleChangeRequest,
    db: Session = Depends(get_db),
    claims: dict = Depends(require_role("boss")),
):
    """
    Зміна ролі користувача.
    Доступна тільки для тих, у кого role == 'boss' у токені.
    """
    # Переконуємось, що така роль існує
    target_role = _get_role_by_name(db, body.role)

    # Переконуємось, що у користувача вже є роль (init мав бути викликаний раніше)
    existing = db.query(UserRole).filter(UserRole.user_id == user_id).first()
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no role yet, init role first",
        )

    existing.role_id = target_role.id
    db.commit()

    return UserRolesResponse(user_id=user_id, roles=[body.role])


@router.get("/{user_id}/roles", response_model=UserRolesResponse)
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_claims),
) -> UserRolesResponse:
    """
    Повертає поточну роль користувача (як список з 0/1 елементом).
    Поки що достатньо просто валідного токена.
    """
    roles = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    role_names = [r[0] for r in roles]

    return UserRolesResponse(user_id=user_id, roles=role_names)
