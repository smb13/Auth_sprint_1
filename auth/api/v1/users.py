from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from models.role import admin_role_name
from schemas.error import HttpExceptionModel
from models.permission import user_management
from services.role import RoleService, get_role_service
from services.user_role import UserRoleService, get_user_role_service

router = APIRouter(redirect_slashes=False, prefix="/users", tags=['Users'])


@router.post(
    '/{user_id}/roles/{role_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Добавление роли пользователю',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
async def assign_user_role(
        user_id: UUID,
        role_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
        role_service: RoleService = Depends(get_role_service),
) -> None:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([user_management])
    if not await user_role_service.get_user_by_id(user_id):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='User not found')
    if not await role_service.get_role_by_id(role_id):
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
    },
    dependencies=[Depends(HTTPBearer())]
)
async def delete_user_role(
        user_id: UUID,
        role_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
) -> None:
    if not await user_role_service.is_superuser():
        await user_role_service.check_access([user_management])
    if not await user_role_service.delete_user_role(user_id, role_id):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='User role not found')
