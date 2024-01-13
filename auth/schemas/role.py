from uuid import UUID

from pydantic import Field, BaseModel


class RoleBase(BaseModel):
    name: str = Field(title='Название')


class RoleResponse(RoleBase):
    id: UUID

    class Config:
        orm_mode = True
