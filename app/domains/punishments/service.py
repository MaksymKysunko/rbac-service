from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from fastapi import HTTPException, status

from .models import Punishment
from .schemas import PunishmentCreate

class PunishmentsService:
    def __init__(self, db: Session):
        self.db = db

    def add_punishment(self, data: PunishmentCreate, boss_id: Optional[int] = None) -> Punishment:
        # Check active punishments for this context
        active = self.db.execute(
            select(Punishment).where(
                and_(
                    Punishment.user_id == data.user_id,
                    Punishment.context == data.context,
                    Punishment.status == "active"
                )
            )
        ).scalars().first()

        if active:
            # If we are blocking an already blocked user, we expire the old one
            active.status = "expired"

        # Progressive logic: Count previous NON-AMNESTIED punishments in this context
        # to determine history level
        history_count = self.db.query(Punishment).filter(
            and_(
                Punishment.user_id == data.user_id,
                Punishment.context == data.context,
                Punishment.status != "amnestied"
            )
        ).count()

        # If data.duration_hours is provided, we use it, 
        # but the UI will be filtered based on history_count
        
        expires_at = None
        if data.duration_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=data.duration_hours)

        punishment = Punishment(
            user_id=data.user_id,
            action=data.action,
            context=data.context,
            reason=data.reason,
            expires_at=expires_at,
            status="active",
            created_by=boss_id
        )
        self.db.add(punishment)
        self.db.flush()
        self.db.refresh(punishment)
        return punishment

    def get_moderation_history(self, user_id: int) -> List[Punishment]:
        return self.db.query(Punishment).filter(
            Punishment.user_id == user_id
        ).order_by(desc(Punishment.created_at)).all()

    def get_active_limits(self, user_id: int) -> Dict[str, Any]:
        """
        Returns a dict of active limits for JWT inclusion.
        e.g. {"chatlimited": "2026-02-24T20:00:00Z"}
        """
        now = datetime.now(timezone.utc)
        active_punishments = self.db.query(Punishment).filter(
            and_(
                Punishment.user_id == user_id,
                Punishment.status == "active"
            )
        ).all()

        limits = {}
        for p in active_punishments:
            # Check if expired naturally
            if p.expires_at and p.expires_at.replace(tzinfo=timezone.utc) < now:
                p.status = "expired"
                self.db.flush()
                continue
            
            if p.context == "chat":
                limits["chatlimited"] = p.expires_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if p.expires_at else "permanent"
            elif p.context == "full":
                limits["accountblocked"] = p.expires_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if p.expires_at else "permanent"
        
        return limits

    def grant_amnesty(self, punishment_id: int, boss_id: int, reason: str) -> bool:
        p = self.db.get(Punishment, punishment_id)
        if not p:
            return False
            
        p.status = "amnestied"
        p.amnestied_by = boss_id
        p.amnestied_at = datetime.now(timezone.utc)
        p.amnesty_reason = reason
        self.db.flush()
        return True
