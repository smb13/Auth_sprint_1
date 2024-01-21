from http import HTTPStatus
import orjson
from typing import Annotated

from psycopg.errors import UniqueViolation
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse


class ErrorConflict(BaseModel):
    """Объект с такими данными уже существует"""
    class Detail(BaseModel):
        message: Annotated[str, Field(description="", examples=["Key (login)=(username) already exists."])]
        name: Annotated[str, Field(description="", examples=["users_login_key"])]

    detail: Detail

    def __init__(self, uv: UniqueViolation):
        super().__init__(detail=ErrorConflict.Detail(message=uv.diag.message_detail, name=uv.diag.constraint_name))

    def to_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content=self.model_dump()
        )


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class HttpExceptionModel(OrjsonBaseModel):
    detail: str
