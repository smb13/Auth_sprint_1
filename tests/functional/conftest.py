import sys
from random import randint
from typing import Callable
from uuid import uuid4

import psycopg
import aiohttp
import pytest
import pytest_asyncio
from psycopg import Connection
from werkzeug.security import generate_password_hash

from settings import session_settings, BaseTestSettings

from redis.asyncio import Redis


@pytest_asyncio.fixture(scope='session')
async def pg_client() -> Connection:
    client = psycopg.connect(conninfo=session_settings.get_pg_dsn())
    yield client
    client.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> Redis:
    client = Redis(host=session_settings.redis_host, port=session_settings.redis_port)
    yield client
    await client.aclose()


@pytest_asyncio.fixture
def redis_flush_db(redis_client) -> Callable:
    async def inner() -> None:
        await redis_client.flushdb()

    return inner


@pytest_asyncio.fixture(scope='session')
async def http_session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(http_session):
    async def inner(url: str, settings: BaseTestSettings, **kwargs):
        async with http_session.get(
                settings.service_url + url, **kwargs
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

    return inner


@pytest.fixture
def make_post_request(http_session):
    async def inner(url: str, settings: BaseTestSettings, **kwargs):
        async with http_session.post(
                settings.service_url + url, **kwargs
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

        pass

    return inner


@pytest.fixture
def make_delete_request(http_session):
    async def inner(url: str, settings: BaseTestSettings, **kwargs):
        async with http_session.delete(
                settings.service_url + url, **kwargs
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

        pass

    return inner


@pytest.fixture
def make_patch_request(http_session):
    async def inner(url: str, settings: BaseTestSettings, **kwargs):
        async with http_session.patch(
                settings.service_url + url, **kwargs
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

        pass

    return inner


@pytest.fixture(scope='session', autouse=True)
def faker_seed():
    return randint(0, sys.maxsize)


@pytest.fixture
def generate_fake_users(faker):
    async def inner(quantity: int = None) -> list[dict[str, str]]:
        return list([{
            'login': faker.user_name() + str(randint(0, sys.maxsize)),
            'password': faker.password(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'email': str(randint(0, sys.maxsize)) + faker.email(),
            'superuser': faker.boolean(),
            'id': str(uuid4()),
            'created_at': faker.date_time_this_decade(),
            'modified_at': faker.date_time_this_decade()
        } for _ in range(quantity or 100)])

    return inner


@pytest.fixture
def pg_drop_users(pg_client):
    async def inner():
        pg_client.execute('DELETE FROM sessions')
        pg_client.execute('DELETE FROM users')
        pg_client.commit()

    return inner


@pytest.fixture
def pg_set_users(pg_client, clear_all):
    async def inner(users: list[dict[str, str]]):
        await clear_all()
        if users:
            query = ("INSERT INTO users (" + ", ".join(users[0].keys()) +
                     ") VALUES (" + ", ".join(['%s'] * len(users[0])) + ")")
            for user in users:
                user = dict(user)
                user['password'] = generate_password_hash(user['password'])
                pg_client.execute(query, tuple(user.values()))
            pg_client.commit()

    return inner


@pytest.fixture
def clear_all(pg_drop_users, redis_flush_db):
    async def inner():
        await pg_drop_users()
        await redis_flush_db()

    return inner


@pytest.fixture
def auth_header():
    async def inner(access_token: str):
        return {'Authorization': f"Bearer {access_token}"}

    return inner


@pytest.fixture
def method_login(pg_client, http_session):
    async def inner(settings: BaseTestSettings, login: str, password: str):
        request = {
            'login': login,
            'password': password
        }
        async with http_session.post(
                settings.service_url + '/api/v1/auth/login', json=request
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

    return inner


# @pytest.fixture
# def method_access_revoke(http_session, auth_header):
#     async def inner(settings: BaseTestSettings, access_token: str):
#         async with http_session.delete(
#                 settings.service_url + '/api/v1/auth/access-revoke', headers=await auth_header(access_token)
#         ) as response:
#             body = await response.json()
#             headers = response.headers
#             status = response.status
#         return {'status': status, 'body': body, 'headers': headers}
#
#     return inner


@pytest.fixture
def method_refresh(http_session, auth_header):
    async def inner(settings: BaseTestSettings, refresh_token: str):
        async with http_session.post(
                settings.service_url + '/api/v1/auth/refresh', headers=await auth_header(refresh_token)
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

    return inner


@pytest.fixture
def method_get_profile(http_session, auth_header):
    async def inner(settings: BaseTestSettings, access_token: str):
        async with http_session.get(
                settings.service_url + '/api/v1/auth/profile', headers=await auth_header(access_token)
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return {'status': status, 'body': body, 'headers': headers}

    return inner
