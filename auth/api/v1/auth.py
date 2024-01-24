from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
from http import HTTPStatus

from fastapi.security import HTTPBearer

from db.redisdb import get_redis
from schemas.user import UserId, UserProfile, UserCredentials, JWTAccessToken, \
    RevokedSessions, NewSession, RevokedTokens, UpdatedProfileFields, UserAttributes, SessionRecord
from services.auth import AuthService, get_auth_service

router = APIRouter(redirect_slashes=False, prefix="/auth", tags=['Auth'])


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    return (await (await get_redis()).get(decrypted_token["jti"]) or "") == b"revoked"


@router.post('/signup', status_code=HTTPStatus.CREATED)
async def create_user(request: UserProfile, auth: AuthService = Depends(get_auth_service)) -> UserId:
    """Регистрация нового пользователя"""
    return await auth.create_user(request)


@router.post("/login")
async def login(request: UserCredentials, auth: AuthService = Depends(get_auth_service)) -> NewSession:
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
async def patch_profile(request: UserCredentials, auth: AuthService = Depends(get_auth_service))\
        -> UpdatedProfileFields:
    """Обновление профилья пользователя"""
    return await auth.update_profile(request)


@router.get("/profile", dependencies=[Depends(HTTPBearer())])
async def get_profile(auth: AuthService = Depends(get_auth_service)) -> UserAttributes:
    """Обновление профилья пользователя"""
    return await auth.get_profile()


@router.get("/history", dependencies=[Depends(HTTPBearer())])
async def history(auth: AuthService = Depends(get_auth_service)) -> list[SessionRecord]:
    """Получение истории входов пользователя"""
    return await auth.get_history()
