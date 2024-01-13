import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import auth, genres, persons
from core.config import redis_settings, elastic_settings
from core.logger import LOGGING
from db import cache
from db import database
from db.elastic import Elastic
from db.redisdb import RedisDb


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Создаем подключение к базам при старте сервера.
    cache.cache = RedisDb(Redis(host=redis_settings.host, port=redis_settings.port))
    database.db = Elastic(AsyncElasticsearch(hosts=[f'http://{elastic_settings.host}:{elastic_settings.port}']))

    # Проверяем соединения с базами.
    await cache.cache.ping()
    await database.db.ping()

    yield

    # Отключаемся от баз при выключении сервера
    await cache.cache.close()
    await database.db.close()


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
app.include_router(films.router, prefix='/api/v1/films', tags=['Films'])

# Подключаем роутер к серверу с указанием префикса для API (/v1/genres).
app.include_router(genres.router, prefix='/api/v1/genres', tags=['Genres'])

# Подключаем роутер к серверу с указанием префикса для API (/v1/persons).
app.include_router(persons.router, prefix='/api/v1/persons', tags=['Persons'])

if __name__ == '__main__':
    # Запускаем приложение с помощью uvicorn сервера.
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
