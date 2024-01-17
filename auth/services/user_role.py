from functools import lru_cache
from uuid import UUID
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.role import Role, UserRole
from models.user import User
from services.auth import AuthService, get_auth_service


class UserRoleService:
    def __init__(self, db: AsyncSession, auth_service: AuthService, jwt: AuthJWT):
        self.db = db
        self.auth_service = auth_service
        self.jwt = jwt

    async def get_user_by_id(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_role_by_id(self, role_id: UUID) -> Role:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def get_user_role(
        self, user_id: UUID, role_id: UUID
    ) -> UserRole:
        result = await self.db.execute(
            select(UserRole).where(UserRole.user_id == user_id,
                                   UserRole.role_id == role_id)
        )
        return result.scalars().first()

    async def create_user_role(
        self, user_id: UUID, role_id: UUID
    ) -> None:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()
        await self.auth_service.logout(user_id)

    async def delete_user_role(
        self, user_id: UUID, role_id: UUID
    ) -> bool:
        result = await self.db.execute(
            delete(UserRole).where(UserRole.role_id == role_id,
                                   UserRole.user_id == user_id)
        )
        await self.db.commit()
        await self.auth_service.logout(user_id)
        return result.rowcount != 0

    async def check_access(self, allow_roles: list[str] = None) -> None:
        await self.jwt.jwt_required()

        if allow_roles is None:
            return

        access_jwt = await self.jwt.get_raw_jwt()
        if not set(allow_roles) & set(access_jwt['roles']):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail='Insufficient permissions')

    async def is_superuser(self) -> bool:
        await self.jwt.jwt_required()
        user = await self.db.get(User, await self.jwt.get_jwt_subject())
        return user.superuser


@lru_cache()
def get_user_role_service(
    db: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    jwt: AuthJWT = Depends()
) -> UserRoleService:
    return UserRoleService(db, auth_service, jwt)
