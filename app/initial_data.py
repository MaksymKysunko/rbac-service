# app/initial_data.py
from sqlalchemy.orm import Session

from app.models.role import Role

# Набір ролей "із коробки"
DEFAULT_ROLES = [
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
