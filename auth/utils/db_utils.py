from sqlalchemy import insert, select, update

from db.postgres import async_session
from models.permission import Permission, RolePermission, permissions
from fastapi.encoders import jsonable_encoder


async def create_permissions() -> Permission:
    async with async_session() as db:
        for permission in permissions:
            permission_db_id = (
                await db.execute(select(Permission.id).where(Permission.name == permission.name))).first()
            if not permission_db_id:
                values = jsonable_encoder(permission)
                permission_db_id = (await db.execute(insert(Permission).
                                                     values(values).
                                                     returning(Permission.id))
                                    ).first()
                await db.commit()
            permission.id = permission_db_id
    return permissions
