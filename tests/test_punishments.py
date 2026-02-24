import pytest
from datetime import datetime, timedelta, timezone
from app.domains.punishments.service import PunishmentsService
from app.domains.punishments.schemas import PunishmentCreate
from app.domains.punishments.models import Punishment

def test_add_punishment(db_session):
    srv = PunishmentsService(db_session)
    data = PunishmentCreate(user_id=1, action="ban", context="chat", reason="Spam", duration_hours=1)
    
    p = srv.add_punishment(data, boss_id=2)
    
    assert p.user_id == 1
    assert p.status == "active"
    assert p.expires_at is not None
    assert p.created_by == 2

def test_progressive_logic(db_session):
    srv = PunishmentsService(db_session)
    user_id = 10
    
    # Add 1st punishment
    srv.add_punishment(PunishmentCreate(user_id=user_id, action="ban", context="chat", reason="1st", duration_hours=1))
    
    # Check history count logic (even if we don't use it for duration yet in service, it's counted)
    history_count = db_session.query(Punishment).filter(
        Punishment.user_id == user_id,
        Punishment.context == "chat"
    ).count()
    assert history_count == 1
    
    # Add 2nd punishment - old one should become expired
    srv.add_punishment(PunishmentCreate(user_id=user_id, action="ban", context="chat", reason="2nd", duration_hours=6))
    
    active_count = db_session.query(Punishment).filter(
        Punishment.user_id == user_id,
        Punishment.context == "chat",
        Punishment.status == "active"
    ).count()
    assert active_count == 1
    
    total_count = db_session.query(Punishment).filter(
        Punishment.user_id == user_id,
        Punishment.context == "chat"
    ).count()
    assert total_count == 2

def test_active_limits(db_session):
    srv = PunishmentsService(db_session)
    user_id = 20
    
    # Permanent chat ban
    srv.add_punishment(PunishmentCreate(user_id=user_id, action="ban", context="chat", reason="Spam", duration_hours=None))
    
    limits = srv.get_active_limits(user_id)
    assert limits["chatlimited"] == "permanent"
    
    # Full block for 1 hour
    srv.add_punishment(PunishmentCreate(user_id=user_id, action="block", context="full", reason="Abuse", duration_hours=1))
    
    limits = srv.get_active_limits(user_id)
    assert "accountblocked" in limits
    assert "chatlimited" in limits

def test_amnesty(db_session):
    srv = PunishmentsService(db_session)
    user_id = 30
    
    p = srv.add_punishment(PunishmentCreate(user_id=user_id, action="ban", context="chat", reason="Oops"))
    assert p.status == "active"
    
    success = srv.grant_amnesty(p.id, boss_id=2, reason="Apologized")
    assert success is True
    
    db_session.refresh(p)
    assert p.status == "amnestied"
    assert p.amnesty_reason == "Apologized"

def test_permissions_api(boss_client, db_session):
    user_id = 40
    # Add a punishment directly to DB for the test
    srv = PunishmentsService(db_session)
    srv.add_punishment(PunishmentCreate(user_id=user_id, action="ban", context="chat", reason="Spam", duration_hours=2))
    
    response = boss_client.get(f"/api/rbac/users/{user_id}/permissions")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert "chatlimited" in data["limits"]
