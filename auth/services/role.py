from functools import lru_cache

from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.role import Role
from schemas.role import RoleBase, RoleResponse


class RoleService:
    def __init__(self, db: AsyncSession, jwt: AuthJWT):
        self.db = db
        self.jwt = jwt

    async def list_roles(self) -> list[RoleResponse]:
        await self.jwt.jwt_required()
        result = await self.db.execute(select(Role))
        return result.scalars().all()

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
        result = await self.db.execute(
            update(Role).where(Role.id == role_id)
            .values(**values).returning(Role)
        )
        await self.db.commit()
        return result.first()

    async def delete_role(self, role_id: UUID) -> bool:
        await self.jwt.jwt_required()
        result = await self.db.execute(delete(Role).where(Role.id == role_id))
        await self.db.commit()
        return result.rowcount != 0


@lru_cache()
def get_role_service(
    db: AsyncSession = Depends(get_session),
    jwt: AuthJWT = Depends()
) -> RoleService:
    return RoleService(db, jwt)
