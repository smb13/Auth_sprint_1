from functools import lru_cache
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg.errors import UniqueViolation
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.permission import RolePermission, Permission
from models.role import Role
from schemas.permission import PermissionResponse
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

    async def create_role(self, role_create: RoleBase) -> RoleResponse | Exception:
        await self.jwt.jwt_required()
        role = Role(**jsonable_encoder(role_create))
        self.db.add(role)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Role already exists')
            raise e
        await self.db.refresh(role)
        return role

    async def patch_role(
            self, role_id: UUID, role_patch: RoleBase
    ) -> Optional[RoleResponse]:
        await self.jwt.jwt_required()
        values = jsonable_encoder(role_patch)
        try:
            await self.db.execute(
                update(Role).where(Role.id == role_id)
                .values(**values)
            )
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                if 'roles_name_key' in str(e):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail='Another role has the same name')
            raise e
        await self.db.commit()
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def delete_role(self, role_id: UUID) -> bool:
        await self.jwt.jwt_required()
        result = await self.db.execute(delete(Role).where(Role.id == role_id))
        await self.db.commit()
        return result.rowcount != 0

    async def delete_role_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        result = await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id,
                                         RolePermission.permission_id == permission_id)
        )
        await self.db.commit()
        return result.rowcount != 0

    async def get_role_permissions(self, role_id: UUID) -> list[PermissionResponse]:
        result = (await self.db.execute(
            select(Permission).where(Permission.id.in_(select(RolePermission.permission_id).
                                                       where(RolePermission.role_id == role_id).subquery()))
        )).scalars().all()
        return result

    async def assign_role_permission(self, role_id: UUID, permission_id: UUID) -> None:
        permission_role = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(permission_role)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                if 'role_permissions_role_id_fkey' in str(e):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail='Role not found')
                if 'role_permissions_permission_id_fkey' in str(e):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail='Permission not found')
                if 'role_permissions_role_id_permission_id_key' in str(e):
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                        detail='Role permission already exists')
            raise e
        await self.db.refresh(permission_role)

    async def get_role_by_id(self, role_id: UUID) -> Role:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()


@lru_cache()
def get_role_service(
        db: AsyncSession = Depends(get_session),
        jwt: AuthJWT = Depends()
) -> RoleService:
    return RoleService(db, jwt)
