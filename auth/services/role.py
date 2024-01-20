from functools import lru_cache

from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.permission import permissions, RolePermission, Permission
from models.role import Role
from schemas.role import RoleBase, RoleResponse


class RoleService:
    def __init__(self, db: AsyncSession, jwt: AuthJWT):
        self.db = db
        self.jwt = jwt

    async def list_roles(self) -> list[RoleResponse]:
        await self.jwt.jwt_required()
        result = await self.db.execute(select(Role))
        roles = result.scalars().all()
        return roles

    async def get_role_by_name(self, name: str) -> Optional[RoleResponse]:
        await self.jwt.jwt_required()
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalars().first()

    async def create_role(self, role_create: RoleBase) -> RoleResponse:
        await self.jwt.jwt_required()
        role = Role(**jsonable_encoder(role_create))
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def patch_role(
            self, role_id: UUID, role_patch: RoleBase
    ) -> Optional[RoleResponse]:
        await self.jwt.jwt_required()
        values = jsonable_encoder(role_patch)
        await self.db.execute(
            update(Role).where(Role.id == role_id)
            .values(**values)
        )
        await self.db.commit()
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def delete_role(self, role_id: UUID) -> bool:
        await self.jwt.jwt_required()
        result = await self.db.execute(delete(Role).where(Role.id == role_id))
        await self.db.commit()
        return result.rowcount != 0

    async def create_permissions(self):
        for permission in permissions:
            self.db.add(permission)
            await self.db.commit()
            await self.db.refresh(permission)
        return permissions

    async def delete_role_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        result = await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id,
                                         RolePermission.permission_id == permission_id)
        )
        await self.db.commit()
        return result.rowcount != 0

    async def get_permission_by_id(self, permission_id: UUID):
        result = await self.db.execute(select(Permission).where(Permission.id == permission_id))
        return result.scalars().first()

    async def get_role_permission(self, role_id: UUID, permission_id: UUID):
        result = await self.db.execute(
            select(RolePermission).where(RolePermission.role_id == role_id,
                                         RolePermission.permission_id == permission_id)
        )
        return result.scalars().first()

    async def create_user_role(self, role_id: UUID, permission_id: UUID):
        permission_role = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(permission_role)
        await self.db.commit()

    async def get_role_by_id(self, role_id: UUID) -> Role:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()


@lru_cache()
def get_role_service(
        db: AsyncSession = Depends(get_session),
        jwt: AuthJWT = Depends()
) -> RoleService:
    return RoleService(db, jwt)
