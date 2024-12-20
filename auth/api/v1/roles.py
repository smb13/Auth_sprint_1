from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from models.permission import role_management
from schemas.error import HttpExceptionModel
from schemas.permission import PermissionResponse
from schemas.role import RoleResponse, RoleBase
from services.role import RoleService, get_role_service, check_access
from services.user_role import UserRoleService, get_user_role_service

router = APIRouter(redirect_slashes=False, prefix="/roles", tags=['Roles'])


@router.post(
    '',
    response_model=RoleResponse,
    summary='Создание роли',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def create_role(
        role_create: RoleBase,
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service)
) -> RoleResponse:
    return await role_service.create_role(role_create)


@router.patch(
    '/{role_id}',
    response_model=RoleResponse,
    summary='Изменение роли',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def patch_role(
        role_id: UUID,
        role_patch: RoleBase,
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
) -> RoleResponse:
    role = await role_service.patch_role(role_id, role_patch)
    if not role:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role not found')
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
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def delete_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
) -> None:
    if not (await role_service.delete_role(role_id)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Role not found')


@router.get(
    '',
    response_model=list[RoleResponse],
    summary='Получение списка ролей',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def list_roles(
        role_service: RoleService = Depends(get_role_service),
        user_role_service: UserRoleService = Depends(get_user_role_service),
) -> list[RoleResponse]:
    return await role_service.list_roles()


@router.post(
    '/{role_id}/permissions/{permission_id}',
    status_code=HTTPStatus.CREATED,
    summary='Добавление доступа роли',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def assign_role_permission(
        role_id: UUID,
        permission_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
        role_service: RoleService = Depends(get_role_service),
) -> None:
    await role_service.assign_role_permission(role_id, permission_id)


@router.delete(
    '/{role_id}/permissions/{permission_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Удаление доступа у роли',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def delete_role_permission(
        role_id: UUID,
        permission_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
        role_service: RoleService = Depends(get_role_service),
) -> None:
    if not await role_service.delete_role_permission(role_id, permission_id):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='User role not found')


@router.get(
    '/{role_id}/permissions',
    status_code=HTTPStatus.OK,
    summary='Получение доступов роли',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
@check_access(role_management)
async def get_role_permissions(
        role_id: UUID,
        user_role_service: UserRoleService = Depends(get_user_role_service),
        role_service: RoleService = Depends(get_role_service),
) -> list[PermissionResponse]:
    return await role_service.get_role_permissions(role_id)
