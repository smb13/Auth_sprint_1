from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    full_name: str = Field(title='Имя')
    email: EmailStr = Field(title='Email')


class UserCreate(UserBase):
    login: str = Field(title='Логин')
    password: str


class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True


class UserPatch(BaseModel):
    email: EmailStr | None
    login: str | None = Field(title='Логин')
    full_name: str | None = Field(title='Имя')
    password: str | None = Field(title='Пароль')
