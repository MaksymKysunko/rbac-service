from typing import List
from pydantic import BaseModel


class RoleChangeRequest(BaseModel):
    """Пейлоад для зміни ролі користувача (promote/demote)."""
    role: str


class UserRolesResponse(BaseModel):
    """Відповідь із поточними ролями користувача (у нашому випадку 0/1 елемент)."""
    user_id: int
    roles: List[str]