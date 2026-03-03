# app/initial_data.py
from sqlalchemy.orm import Session

from app.domains.roles.models import Role

# Набір ролей "із коробки"
DEFAULT_ROLES = [
     ('guest', 'Новый пользователь', 100),
     ('soldier','Обычный участник',50),
     ('sotto_capo','Доверенный участник',40),
     ('capo', 'Модератор района',30),
     ('consigliere','Администратор',20),
     ('boss', 'Руководитель',10),
]


def create_default_roles(db: Session) -> None:
    """
    Створює стандартні ролі, якщо їх ще немає.
    Ідемпотентна: повторний виклик не створює дублікатів.
    """
    for name, description, rank in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.name == name).first()
        if role is None:
            role = Role(name=name, description=description, rank=rank)
            db.add(role)
    db.commit()


def create_default_settings(db: Session) -> None:
    """
    Creates default system settings if they don't exist.
    """
    from app.domains.roles.models import Setting
    
    defaults = [
        ("blockUnverifiedUsers", "true", "bool", "Whether to block unverified users or give them soldier-like access"),
    ]
    
    for key, value, stype, desc in defaults:
        existing = db.query(Setting).filter(Setting.key == key).first()
        if not existing:
            setting = Setting(key=key, value=value, type=stype, description=desc)
            db.add(setting)
    db.commit()
