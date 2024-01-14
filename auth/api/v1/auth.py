from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from http import HTTPStatus

from psycopg.errors import UniqueViolation
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from db.postgres import get_session
from models.user import User
from schemas.user import UserInDB, NewUserCredentials

router = APIRouter(redirect_slashes=False, prefix="/auth", tags=['Auth'])


class ConflictError(BaseModel):
    """Неуникальные данные"""
    message: Annotated[str, Query(description="", examples=["Key (login)=(username) already exists."])]
    name: Annotated[str, Query(description="", examples=["users_login_key"])]


@router.post('/signup', response_model=UserInDB, status_code=HTTPStatus.CREATED, responses={
    HTTPStatus.CONFLICT: {"model": ConflictError, "description": "Confilct Error"}
})
async def create_user(user_create: NewUserCredentials, db: AsyncSession = Depends(get_session)) -> JSONResponse | User:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        if isinstance(e.orig, UniqueViolation):
            return JSONResponse(status_code=HTTPStatus.CONFLICT,
                                content=ConflictError(
                                    message=e.orig.diag.message_detail,
                                    name=e.orig.diag.constraint_name).model_dump())
        raise e
    await db.refresh(user)
    return user
