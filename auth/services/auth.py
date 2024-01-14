import datetime
from functools import lru_cache
from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from psycopg.errors import UniqueViolation
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.redisdb import get_redis
from models.session import Session
from models.user import User
from schemas.error import ErrorConflict
from schemas.user import JWTTokens, JWTAccessToken, UserUpdateRequest, UserCreateRequest


class AuthService:
    pass
    """
    UserService содержит бизнес-логику по работе с пользователями и доступами.
    """

    def __init__(self, db: AsyncSession, jwt: AuthJWT, redis: Redis) -> None:
        self.db = db
        self.jwt = jwt
        self.redis = redis

    async def create_user(self, request: UserCreateRequest) -> User | None:
        user = User(**jsonable_encoder(request))
        self.db.add(user)
        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.CONFLICT, **ErrorConflict(e.orig).model_dump())
            raise e
        await self.db.refresh(user)
        return user

    async def authenticate(self, login: str, password: str) -> JWTTokens | None:
        user_found = (await self.db.execute(select(User).where(User.login == login))).scalars().first()
        if not user_found or not user_found.check_password(password):
            return None

        tokens = JWTTokens(
            access_token=await self.jwt.create_access_token(subject=str(user_found.id)),
            refresh_token=await self.jwt.create_refresh_token(subject=str(user_found.id))
        )

        self.db.add(Session(
            user_id=user_found.id,
            refresh_token=tokens.refresh_token,
            expire=datetime.datetime.utcfromtimestamp(
                (await self.jwt.get_raw_jwt(tokens.refresh_token))["exp"]
            )
        ))

        try:
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.CONFLICT, **ErrorConflict(e.orig).model_dump())
            raise e
        return tokens

    async def refresh_token(self) -> JWTAccessToken:
        await self.jwt.jwt_refresh_token_required()
        return JWTAccessToken(access_token=await self.jwt.create_access_token(subject=await self.jwt.get_jwt_subject()))

    async def revoke_refresh_token(self):
        await self.jwt.jwt_refresh_token_required()
        jti = (await self.jwt.get_raw_jwt())
        await self.redis.setex(
            jti["jti"], datetime.datetime.utcfromtimestamp(jti["exp"])-datetime.datetime.utcnow(), 'revoked'
        )

    async def revoke_access_token(self):
        await self.jwt.jwt_required()
        jti = (await self.jwt.get_raw_jwt())
        await self.redis.setex(
            jti["jti"], datetime.datetime.utcfromtimestamp(jti["exp"])-datetime.datetime.utcnow(), 'revoked'
        )

    async def update_profile(self, request: UserUpdateRequest):
        await self.jwt.jwt_required()
        user = await self.db.get(User, await self.jwt.get_jwt_subject())
        if not user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        user.update(**request.model_dump())

        try:
            await self.db.merge(user)
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.CONFLICT, **ErrorConflict(e.orig).model_dump())
            raise e
        await self.db.commit()


@lru_cache()
def get_auth_service(
        db: AsyncSession = Depends(get_session),
        jwt: AuthJWT = Depends(),
        redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, jwt, redis)
