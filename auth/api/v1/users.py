from http import HTTPStatus
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from db.redisdb import get_redis
from models.role import admin_role_name
from schemas.error import HttpExceptionModel
from services.user_role import UserRoleService, get_user_role_service

router = APIRouter(redirect_slashes=False, prefix="/users", tags=['Users'])

jwt = HTTPBearer(auto_error=False)


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    return (await (await get_redis()).get(decrypted_token["jti"]) or "") == b"revoked"


@router.post(
    '/{user_id}/roles/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Добавление роли пользователю',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    }
)
async def create_user_role(
        user_id: UUID,
        role_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
        access_token: str = Depends(jwt)
) -> None:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([admin_role_name])
    if not await user_role_service.get_user_by_id(user_id):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='User not found')
    if not await user_role_service.get_role_by_id(role_id):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Role not found')
    if await user_role_service.get_user_role(user_id, role_id):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='User role already exists')
    await user_role_service.create_user_role(user_id, role_id)


@router.delete(
    '/{user_id}/roles/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Удаление роли у пользователя',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    }
)
async def delete_user_role(
        user_id: UUID,
        role_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
        access_token: str = Depends(jwt)
) -> None:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([admin_role_name])
    if not await user_role_service.delete_user_role(user_id, role_id):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='User role not found')
