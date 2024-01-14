from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Query
from pydantic import BaseModel, EmailStr


class NewUserCredentials(BaseModel):
    """Данные нового пользователя"""
    login: Annotated[str, Query(description='Имя пользователя', examples=['username'])]
    password: Annotated[str, Query(description='Пароль пользовател', examples=['qwerty'])]
    first_name: Annotated[str, Query(description="Имя пользователя", examples=['Юзер'])]
    last_name: Annotated[str, Query(description="Фамилия пользователя", examples=['Юзерович'])]
    email: Annotated[EmailStr, Query(description="Адрес электронной почты", examples=['username@domain.ru'])]


class UserInDB(BaseModel):
    id: Annotated[UUID, Query(description='Идентификатор пользователя', examples=[uuid4()])]

    class Config:
        orm_mode = True
