# app/schemas/roles.py
from typing import List
from pydantic import BaseModel


class UserRoleCreate(BaseModel):
    role_name: str


class UserRolesResponse(BaseModel):
    user_id: str
    roles: List[str]
