import datetime
from functools import lru_cache
from http import HTTPStatus
from uuid import UUID

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
from schemas.user import JWTAccessToken, UserUpdateRequest, UserCreateRequest, RevokedSessions, CreatedSession, \
    RevokedTokens, UpdatedProfileFields, SessionsHistory


class AuthService:
    pass
    """
    UserService содержит бизнес-логику по работе с пользователями и доступами.
    """

    def __init__(self, db: AsyncSession, jwt: AuthJWT, redis: Redis) -> None:
        self.db = db
        self.jwt = jwt
        self.redis = redis

    async def create_user(self, request: UserCreateRequest) -> User:
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

    async def authenticate(self, login: str, password: str) -> CreatedSession:
        user_found = (await self.db.execute(select(User).where(User.login == login))).scalars().first()
        if not user_found or not user_found.check_password(password):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
        roles = [user_role.role.name for user_role in user_found.roles]

        access_token = await self.jwt.create_access_token(subject=str(user_found.id), user_claims={'roles': roles})
        refresh_token = await self.jwt.create_refresh_token(subject=str(user_found.id))

        session = Session(
            user_id=user_found.id,
            refresh_token=refresh_token,
            expire=datetime.datetime.utcfromtimestamp((await self.jwt.get_raw_jwt(refresh_token))["exp"])
        )
        self.db.add(session)

        try:
            await self.db.commit()
            await self.db.refresh(session)
        except IntegrityError as e:
            await self.db.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=HTTPStatus.CONFLICT, **ErrorConflict(e.orig).model_dump())
            raise e

        return CreatedSession(
            session_id=session.id,
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def logout(self, user_id: UUID | None) -> RevokedSessions:
        await self.jwt.jwt_required()
        if user_id is None:
            user_id = (await self.jwt.get_raw_jwt())['sub']
        sessions = (
            await self.db.execute(
                select(Session).
                where(Session.user_id == user_id).
                where(Session.expire >= datetime.datetime.utcnow())
            )
        ).scalars().all()
        revoked_sessions = []
        for session in sessions:
            token = await self.revoke_token(session.refresh_token, False)
            if token:
                revoked_sessions.append(token)

        revoked_sessions.append(await self.revoke_token())

        return RevokedSessions(sessions=revoked_sessions)

    async def refresh_token(self) -> JWTAccessToken:
        await self.jwt.jwt_refresh_token_required()
        return JWTAccessToken(access_token=await self.jwt.create_access_token(subject=await self.jwt.get_jwt_subject()))

    async def revoke_token(self, token: str = None, force: bool = True) -> str:
        jti = (await self.jwt.get_raw_jwt(token))
        revoked = force or (not await self.redis.get(jti["jti"]))
        await self.redis.setex(
            jti["jti"], datetime.datetime.utcfromtimestamp(jti["exp"]) - datetime.datetime.utcnow(), 'revoked'
        )
        return jti["jti"] if revoked else None

    async def revoke_refresh_token(self) -> RevokedTokens:
        await self.jwt.jwt_refresh_token_required()
        return RevokedTokens(tokens=[await self.revoke_token()])

    async def revoke_access_token(self) -> RevokedTokens:
        await self.jwt.jwt_required()
        return RevokedTokens(tokens=[await self.revoke_token()])

    async def update_profile(self, request: UserUpdateRequest) -> UpdatedProfileFields:
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
        # TODO: Доделать
        return UpdatedProfileFields(updated_fields=[])

    async def get_history(self) -> SessionsHistory:
        await self.jwt.jwt_required()
        # TODO: Сделать
        return SessionsHistory(sessions=[])


@lru_cache()
def get_auth_service(
        db: AsyncSession = Depends(get_session), jwt: AuthJWT = Depends(), redis: Redis = Depends(get_redis)
) -> AuthService:
    return AuthService(db, jwt, redis)
