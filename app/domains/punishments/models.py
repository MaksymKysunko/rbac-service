from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    JSON
)

from app.db import Base


class Punishment(Base):
    __tablename__ = "punishments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    action = Column(String(32), nullable=False)  # 'ban', 'block'
    context = Column(String(32), nullable=False) # 'chat', 'full'
    reason = Column(String(512), nullable=True)
    expires_at = Column(DateTime, nullable=True) # Null means permanent
    status = Column(String(32), nullable=False, default="active") # active, expired, amnestied
    
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, nullable=True) # ID of the boss who issued it
    amnestied_by = Column(Integer, nullable=True)
    amnestied_at = Column(DateTime, nullable=True)
    amnesty_reason = Column(String(512), nullable=True)
