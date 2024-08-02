from fastapi import Depends, HTTPException

from auth.authenticate import authenticate
from models.users import User, RoleEnum


def has_role(*roles: RoleEnum):
    def role_validator(current_user: User = Depends(authenticate)):
        # Проверка на супер администратора или на наличие роли среди разрешенных
        if current_user.role == RoleEnum.super_admin or (roles and current_user.role in roles):
            return current_user
        # Если проверки не прошли, доступ запрещен
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return role_validator

