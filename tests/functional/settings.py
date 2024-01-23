from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SessionSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200')

    redis_host: str = Field('127.0.0.1')
    redis_port: int = Field(6379)

    postgres_dbname: str = Field('movies_database')
    postgres_user: str = ...
    postgres_password: str = ...
    postgres_host: str = Field('localhost')
    postgres_port: int = Field(5432)
    postgres_dbschema: str = Field('public')

    model_config = SettingsConfigDict(env_file='.env')

    def get_pg_dsn(self):
        return (f'user={self.postgres_user} password={self.postgres_password} '
                f'host={self.postgres_host} port={self.postgres_port} '
                f'dbname={self.postgres_dbname}')


class BaseTestSettings(BaseSettings):
    service_url: str = Field('http://127.0.0.1:8000')


class AuthTestSettings(BaseTestSettings):
    pass


session_settings = SessionSettings()
test_settings = AuthTestSettings()
