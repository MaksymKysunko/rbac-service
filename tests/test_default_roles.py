# tests/test_default_roles.py
from app.db import SessionLocal, init_db
from app.models import Role


def test_default_roles_created_on_init_db():
    # Імітуємо старт сервісу
    init_db()

    db = SessionLocal()
    try:
        roles = db.query(Role).all()
        role_names = sorted(r.name for r in roles)

        assert "soldier" in role_names
        assert "capo" in role_names
        assert "sotto_capo" in role_names
        assert 'consigliere' in role_names
        assert 'boss' in role_names
    finally:
        db.close()
