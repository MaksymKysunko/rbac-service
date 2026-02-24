from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class PunishmentCreate(BaseModel):
    user_id: Optional[int] = None
    action: Optional[str] = None  # 'ban', 'block'
    context: Optional[str] = None # 'chat', 'full'
    reason: Optional[str] = None
    duration_hours: Optional[int] = None # None means permanent

class PunishmentResponse(BaseModel):
    id: int
    user_id: int
    action: str
    context: str
    reason: Optional[str]
    expires_at: Optional[datetime]
    status: str
    created_at: datetime
    created_by: Optional[int]
    
    class ConfigDict:
        from_attributes = True

class AmnestyRequest(BaseModel):
    reason: str

class UserPermissionsResponse(BaseModel):
    user_id: int
    roles: List[str]
    limits: dict # e.g. {"chatlimited": "2026-02-24T18:00:00Z"}
