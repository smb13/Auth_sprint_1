from logging import config as logging_config

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class ProjectSettings(BaseSettings):
    name: str = Field('Auth Service')

    model_config = SettingsConfigDict(env_prefix='project_', env_file='.env')


# Класс настройки Postgres
class PostgresSettings(BaseSettings):
    dbname: str = Field('movies_database')
    user: str = ...
    password: str = ...
    host: str = Field('localhost')
    port: int = Field(5432)
    echo: bool = Field(True)
    dbschema: str = Field('public')

    model_config = SettingsConfigDict(env_prefix='postgres_', env_file='.env')

    def get_dsn(self):
        return f'postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'

    def get_connection_info(self):
        return {
            'url': self.get_dsn(),
            'connect_args': {'options': f"-c search_path={self.dbschema},public"}
        }


# Класс настройки Redis
class RedisSettings(BaseSettings):
    host: str = Field('127.0.0.1')
    port: int = Field(6379)

    model_config = SettingsConfigDict(env_prefix='redis_', env_file='.env')


# Класс настройки Elasticsearch
class GunicornSettings(BaseSettings):
    host: str = Field('0.0.0.0')
    port: int = Field(8000)
    workers: int = Field(2)
    loglevel: str = Field('debug')
    model_config = SettingsConfigDict(env_prefix='gunicorn_', env_file='.env')


project_settings = ProjectSettings()
redis_settings = RedisSettings()
postgres_settings = PostgresSettings()
gunicorn_settings = GunicornSettings()
