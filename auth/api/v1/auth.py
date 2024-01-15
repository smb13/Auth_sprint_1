from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus

from starlette.responses import JSONResponse

from db.redisdb import get_redis
from models.user import User
from schemas.error import ErrorConflict
from schemas.user import UserCreated, UserCreateRequest, UserAuthRequest, JWTAccessToken, JWTTokens, UserUpdateRequest
from services.auth import AuthService, get_auth_service

router = APIRouter(redirect_slashes=False, prefix="/auth", tags=['Auth'])


@AuthJWT.token_in_denylist_loader
async def check_if_token_in_denylist(decrypted_token):
    entry = await (await get_redis()).get(decrypted_token["jti"])
    return entry and entry == b"revoked"


@router.post('/signup', response_model=UserCreated, status_code=HTTPStatus.CREATED, responses={
    HTTPStatus.CONFLICT: {"model": ErrorConflict, "description": "Conflict error"}
})
async def create_user(request: UserCreateRequest, auth: AuthService = Depends(get_auth_service)) -> JSONResponse | User:
    return await auth.create_user(request)


@router.post("/login")
async def login(request: UserAuthRequest, auth: AuthService = Depends(get_auth_service)) -> JWTTokens:
    tokens = await auth.authenticate(**request.model_dump())
    if not tokens:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    return tokens


@router.post("/logout")
async def logout(_: AuthService = Depends(get_auth_service)):
    # TODO: Убить все refresh токены
    return {}


@router.post("/refresh")
async def refresh(auth: AuthService = Depends(get_auth_service)) -> JWTAccessToken:
    return await auth.refresh_token()


@router.delete("/refresh-revoke")
async def refresh_revoke(auth: AuthService = Depends(get_auth_service)):
    await auth.revoke_refresh_token()
    return {"detail": "Refresh token has been revoked"}


@router.delete("/access-revoke")
async def access_revoke(auth: AuthService = Depends(get_auth_service)):
    await auth.revoke_access_token()
    return {"detail": "Access token has been revoked"}


@router.patch("/profile")
async def profile(request: UserUpdateRequest, auth: AuthService = Depends(get_auth_service)):
    await auth.update_profile(request)


@router.get("/history")
async def history(auth: AuthService = Depends(get_auth_service)):
    # TODO: Выдать спсиок предыдущих входов (сессий) с паджинаццией.
    return {}
