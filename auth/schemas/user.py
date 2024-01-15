from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserAuthRequest(BaseModel):
    """Данные для аутентификации пользователя"""
    login: Annotated[str, Field(description='Имя пользователя', examples=['username'])]
    password: Annotated[str, Field(description='Пароль пользователя', examples=['qwerty'])]


class UserCreateRequest(UserAuthRequest):
    """Данные нового пользователя"""
    first_name: Annotated[str, Field(description="Имя пользователя", examples=['Юзер'])]
    last_name: Annotated[str, Field(description="Фамилия пользователя", examples=['Юзерович'])]
    email: Annotated[EmailStr, Field(description="Адрес электронной почты", examples=['username@domain.ru'])]


class UserCreated(BaseModel):
    """Созданный пользователь"""
    id: Annotated[UUID, Field(description='Идентификатор пользователя', examples=[uuid4()])]

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Данные для аутентификации пользователя"""
    login: Annotated[str | None, Field(description='Имя пользователя', examples=['username'])] = None
    password: Annotated[str | None, Field(description='Пароль пользователя', examples=['qwerty'])] = None


class JWTAccessToken(BaseModel):
    """Токен доступа"""
    access_token: Annotated[str, Field(
        description='Токен доступа',
        examples=[
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZSIsImlhdCI6MTcwNTI1NjYyMSwibmJmIjoxNzA1MjU2NjIx'
            'LCJqdGkiOiIyN2JhODA5Zi1iNjRmLTQ5ZmEtYjRjOS0zOWNlNmIxOWVlZjIiLCJleHAiOjE3MDUzNDMwMjEsInR5cGUiOiJhY2Nlc3MiL'
            'CJmcmVzaCI6ZmFsc2V9.VVsFbdH4qXSto1tCOHJIC8kyFIgLJ-ql0T-KPzU7Ia4'
        ]
    )]


class CreatedSession(JWTAccessToken):
    """Новая пользовательская сессия"""
    refresh_token: Annotated[str, Field(
        description='Токен обновления',
        examples=[
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZSIsImlhdCI6MTcwNTI1NjYyMSwibmJmIjoxNzA1MjU2NjIx'
            'LCJqdGkiOiIyNjY5OWUxMS05YThlLTQzZTctOTY0Zi0xNDBjNGU2ZmFiODkiLCJleHAiOjE3MDUyNTY5MjEsInR5cGUiOiJyZWZyZXNoI'
            'n0.GwE4P6O3ug03cqeQVNoZqd_fRV7m_O-nrmWk31FoUOM'
        ]
    )]
    session_id: Annotated[UUID, Field(description="Идентификатор созданной сессии", example=[uuid4()])]


class RevokedTokens(BaseModel):
    """Список отозванных токенов"""
    tokens: list[Annotated[str, Field(
        description='Отозванный токен',
        examples=[
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZSIsImlhdCI6MTcwNTI1NjYyMSwibmJmIjoxNzA1MjU2NjIx'
            'LCJqdGkiOiIyNjY5OWUxMS05YThlLTQzZTctOTY0Zi0xNDBjNGU2ZmFiODkiLCJleHAiOjE3MDUyNTY5MjEsInR5cGUiOiJyZWZyZXNoI'
            'n0.GwE4P6O3ug03cqeQVNoZqd_fRV7m_O-nrmWk31FoUOM'
        ]
    )]]


class RevokedSessions(BaseModel):
    """Список сессий с отозвамыми токенами обновления"""
    sessions: list[Annotated[UUID, Field(description='Идентификатор сессии', examples=[uuid4()])]]


class UpdatedProfileFields(BaseModel):
    updated_fields: list[
        Annotated[str, Field(
            description='Обновленных поля профиля пользователя', examples=['login', 'password', 'email']
        )]
    ]


class SessionsHistory(BaseModel):
    sessions: list[
        str
    ]
