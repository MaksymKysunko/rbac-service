from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .models import Role, UserRole

class RolesService:
    def __init__(self, db: Session):
        self.db = db

    def get_role_by_name(self, name: str) -> Role:
        role = self.db.query(Role).filter(Role.name == name).first()
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown role: {name}",
            )
        return role

    def init_user_role(self, user_id: int) -> List[str]:
        """Initialize role for a new user, default is 'guest'."""
        guest_role = self.get_role_by_name("guest")

        mapping = self.db.query(UserRole).filter(UserRole.user_id == user_id).first()
        if mapping is None:
            mapping = UserRole(user_id=user_id, role_id=guest_role.id)
            self.db.add(mapping)
            self.db.commit()
            self.db.refresh(mapping)
            return ["guest"]
        else:
            # if already has role, return current roles
            return self.get_user_role_names(user_id)

    def change_user_role(self, user_id: int, new_role_name: str) -> List[str]:
        """Change user's role. Support creating role if not exists."""
        target_role = self.get_role_by_name(new_role_name)
        
        mapping = self.db.query(UserRole).filter(UserRole.user_id == user_id).first()
        if mapping:
            mapping.role_id = target_role.id
        else:
            mapping = UserRole(user_id=user_id, role_id=target_role.id)
            self.db.add(mapping)
            
        self.db.commit()
        return [new_role_name]

    def get_user_role_names(self, user_id: int) -> List[str]:
        """Get user's current roles as list of names."""
        roles = (
            self.db.query(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        return [r[0] for r in roles]

    def get_first_user_with_role(self, role_name: str) -> int:
        """Find the first user_id with the given role name."""
        role = self.db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not defined in system",
            )

        mapping = self.db.query(UserRole).filter(UserRole.role_id == role.id).first()
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with role '{role_name}'",
            )

        return mapping.user_id

    def get_setting(self, key: str, default: str = None) -> str:
        from .models import Setting
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            return setting.value
        return default

    def set_setting(self, key: str, value: str, stype: str = "bool") -> None:
        from .models import Setting
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value, type=stype)
            self.db.add(setting)
        self.db.commit()

def require_role(role: str):
    """Dependency factory for checking user role from request state (Principal)."""
    from fastapi import Request
    
    def role_checker(request: Request):
        principal = getattr(request.state, "principal", None)
        if not principal:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if user has the required role
        user_role = (principal.role or "").lower()
        if user_role != role.lower() and user_role != "boss":
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        
        return principal
    
    return role_checker
