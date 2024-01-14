import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import auth, users, roles
# from redis.asyncio import Redis

# from api.v1 import auth, genres, persons
from core.config import project_settings, redis_settings
from core.logger import LOGGING
from db.postgres import create_database, purge_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Создаем подключение к базам при старте сервера.
    # redis.redis = Redis(**redis_settings.get_connection_info())

    # Проверяем соединения с базами.
    # await redis.redis.ping()

    from models.user import User
    # TODO: Перейти на миграции
    await create_database()

    yield

    # Отключаемся от баз при выключении сервера
    # TODO: Перейти на миграции
    await purge_database()
    # await redis.redis.close()


app = FastAPI(
    # Название проекта, используемое в документации.
    title=project_settings.name,
    # Адрес документации (swagger).
    docs_url='/api/openapi',
    # Адрес документации (openapi).
    openapi_url='/api/openapi.json',
    # Оптимизация работы с JSON-сериализатором.
    default_response_class=ORJSONResponse,
    # Указываем функцию, обработки жизненного цикла приложения.
    lifespan=lifespan,
    # Описание сервиса
    description="API для получения информации о фильмах, жанрах и людях, участвовавших в их создании",
)

# Подключаем роутер к серверу с указанием префикса для API (/v1/films).
app.include_router(auth.router, prefix='/api/v1')
app.include_router(users.router, prefix='/api/v1')
app.include_router(roles.router, prefix='/api/v1')

if __name__ == '__main__':
    # Запускаем приложение с помощью uvicorn сервера.
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
