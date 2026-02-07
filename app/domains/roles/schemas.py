from typing import List
from pydantic import BaseModel


class RoleChangeRequest(BaseModel):
    """Пейлоад для зміни ролі користувача (promote/demote)."""
    role: str


class UserRolesResponse(BaseModel):
    """Відповідь із поточними ролями користувача."""
    user_id: int
    roles: List[str]


class BossResponse(BaseModel):
    """Відповідь для внутрішнього API (пошук Boss ID)."""
    user_id: int
    username: str = "boss"
