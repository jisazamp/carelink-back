from app.controllers.carelink_controller import get_current_user
from typing import List
from app.models.authorized_users import AuthorizedUsers
from fastapi import HTTPException, status, Depends


def role_required(roles: List[str]):
    def role_checker(current_user: AuthorizedUsers = Depends(get_current_user)):
        if not any(role.name in roles for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operación no permitida"
            )
        return current_user

    return role_checker


def permission_required(permission: str):
    def permission_checker(current_user: AuthorizedUsers = Depends(get_current_user)):
        permissions = [
            perm.name for role in current_user.roles for perm in role.permissions
        ]
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operación no permitida"
            )
        return current_user

    return permission_checker
