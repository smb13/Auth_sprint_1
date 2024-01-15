from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
from http import HTTPStatus

from fastapi.security import HTTPBearer

from db.redisdb import get_redis
from schemas.user import UserCreated, UserCreateRequest, UserAuthRequest, JWTAccessToken, UserUpdateRequest, \
    RevokedSessions, CreatedSession, RevokedTokens, UpdatedProfileFields, SessionsHistory
from services.auth import AuthService, get_auth_service

router = APIRouter(redirect_slashes=False, prefix="/auth", tags=['Auth'])


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    return (await (await get_redis()).get(decrypted_token["jti"]) or "") == b"revoked"


@router.post('/signup', status_code=HTTPStatus.CREATED)
async def create_user(request: UserCreateRequest, auth: AuthService = Depends(get_auth_service)) -> UserCreated:
    """Регистрация нового пользователя"""
    return await auth.create_user(request)


@router.post("/login")
async def login(request: UserAuthRequest, auth: AuthService = Depends(get_auth_service)) -> CreatedSession:
    """Аутентификация пользователя и создание новой сессии"""
    return await auth.authenticate(**request.model_dump())


@router.post("/logout", dependencies=[Depends(HTTPBearer())])
async def logout(auth: AuthService = Depends(get_auth_service)) -> RevokedSessions:
    """Выход из всех активных сессий пользователя"""
    return await auth.logout()


@router.post("/refresh", dependencies=[Depends(HTTPBearer())])
async def refresh(auth: AuthService = Depends(get_auth_service)) -> JWTAccessToken:
    """Обновление токена доступа"""
    return await auth.refresh_token()


@router.delete("/refresh-revoke", dependencies=[Depends(HTTPBearer())])
async def refresh_revoke(auth: AuthService = Depends(get_auth_service)) -> RevokedTokens:
    """Отзыв токена обновления"""
    return await auth.revoke_refresh_token()


@router.delete("/access-revoke", dependencies=[Depends(HTTPBearer())])
async def access_revoke(auth: AuthService = Depends(get_auth_service)) -> RevokedTokens:
    """Отзыв токена доступа"""
    return await auth.revoke_access_token()


@router.patch("/profile", dependencies=[Depends(HTTPBearer())])
async def profile(request: UserUpdateRequest, auth: AuthService = Depends(get_auth_service)) -> UpdatedProfileFields:
    """Обновление профилья пользователя"""
    return await auth.update_profile(request)


@router.get("/history", dependencies=[Depends(HTTPBearer())])
async def history(auth: AuthService = Depends(get_auth_service)) -> SessionsHistory:
    """Получение истории входов пользователя"""
    return await auth.get_history()
