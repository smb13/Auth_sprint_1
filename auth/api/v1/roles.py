from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from http import HTTPStatus

from db.redisdb import get_redis
from schemas.error import HttpExceptionModel
from schemas.role import RoleResponse, RoleBase
from services.role import RoleService, get_role_service
from models.role import admin_role_name
from services.user_role import UserRoleService, get_user_role_service

router = APIRouter(redirect_slashes=False, prefix="/roles", tags=['Roles'])

jwt = HTTPBearer(auto_error=False)


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    return (await (await get_redis()).get(decrypted_token["jti"]) or "") == b"revoked"


@router.post(
    '',
    response_model=RoleResponse,
    summary='Создание роли',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    }
)
async def create_role(
        role_create: RoleBase,
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
        access_token: str = Depends(jwt)
) -> RoleResponse:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([admin_role_name])
    if await role_service.get_role_by_name(role_create.name):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Role already exists')
    return await role_service.create_role(role_create)


@router.patch(
    '/{role_id}',
    response_model=RoleResponse,
    summary='Изменение роли',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    }
)
async def patch_role(
        role_id: UUID,
        role_patch: RoleBase,
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
        access_token: str = Depends(jwt)
) -> RoleResponse:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([admin_role_name])
    role = await role_service.patch_role(role_id, role_patch)
    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Role not found')
    return role


@router.delete(
    '/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Удаление роли',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
)
async def delete_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
        access_token: str = Depends(jwt)
) -> None:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([admin_role_name])
    if not (await role_service.delete_role(role_id)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Role not found')


@router.get(
    '',
    response_model=list[RoleResponse],
    summary='Получение списка ролей',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
async def list_roles(
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
        access_token: str = Depends(jwt)
) -> list[RoleResponse]:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([admin_role_name])
    return await role_service.list_roles()
