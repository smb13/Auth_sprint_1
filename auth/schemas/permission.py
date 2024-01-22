from uuid import UUID

from pydantic import Field, BaseModel


class PermissionResponse(BaseModel):
    name: str = Field(title='Название')
    id: UUID

    class Config:
        orm_mode = True
