import http
from random import randint

import pytest

from tests.functional.settings import test_settings


@pytest.mark.asyncio(scope="session")
async def test_signup(
        clear_all, generate_fake_users, pg_set_users, make_post_request
):
    method_name = '/api/v1/auth/signup'

    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование создания новых пользователей
    fake_users_test = await generate_fake_users(2)
    for user in fake_users_test:
        response = await make_post_request(method_name, test_settings, json={
            key: user[key] for key in ('password', 'login', 'first_name', 'last_name', 'email')
        })
        assert response['status'] == http.HTTPStatus.CREATED
        assert 'id' in response['body']

    # 3. Тестирование создания повторных пользователей
    fake_users_test = await generate_fake_users(2)
    for user in fake_users_test:
        response = await make_post_request(method_name, test_settings, json={
            key: user[key] for key in ('password', 'login', 'first_name', 'last_name', 'email')
        } | {
            'login': fake_users[randint(0, len(fake_users) - 1)]['login']
        })
        assert response['status'] == http.HTTPStatus.CONFLICT

        response = await make_post_request(method_name, test_settings, json={
            key: user[key] for key in ('password', 'login', 'first_name', 'last_name', 'email')
        } | {
            'email': fake_users[randint(0, len(fake_users) - 1)]['email']
        })
        assert response['status'] == http.HTTPStatus.CONFLICT

    # 4. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_login(
        clear_all, generate_fake_users, pg_set_users, method_login
):
    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование аутентификации зарегистрированных пользователей.
    for user in fake_users:
        assert (
                   await method_login(test_settings, login=user['login'], password=user['password'])
               )['status'] == http.HTTPStatus.OK

    # 3. Тестирование аутентификации незарегистрированных пользователей.
    fake_users_test = await generate_fake_users(2)
    for user in fake_users_test:
        assert (
                   await method_login(test_settings, login=user['login'], password=user['password'])
               )['status'] == http.HTTPStatus.FORBIDDEN

    # 4. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_logout(
        generate_fake_users, pg_set_users, method_login, make_post_request, redis_flush_db, clear_all, auth_header
):
    method_name = '/api/v1/auth/logout'

    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование выхода.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        headers = await auth_header(response['body']['access_token'])
        assert (await make_post_request(method_name, test_settings, headers=headers))['status'] == http.HTTPStatus.OK

        assert (
                   await make_post_request(method_name, test_settings, headers=headers)
               )['status'] == http.HTTPStatus.UNAUTHORIZED

        await redis_flush_db()

        assert (await make_post_request(method_name, test_settings, headers=headers))['status'] == http.HTTPStatus.OK

    # 3. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_refresh(
        generate_fake_users, pg_set_users, method_login, clear_all, method_get_profile, method_refresh
):
    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование обновление токена доступа.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'refresh_token' in response['body']

        response = await method_refresh(test_settings, response['body']['refresh_token'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        response = await method_get_profile(test_settings, response['body']['access_token'])
        assert response['status'] == http.HTTPStatus.OK

    # 3. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_refresh_revoke(
        generate_fake_users, pg_set_users, method_login, make_delete_request,
        clear_all, auth_header, method_refresh, redis_flush_db
):
    method_name = '/api/v1/auth/refresh-revoke'

    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование отзыва токена обновления.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'refresh_token' in response['body']

        assert (
                   await make_delete_request(
                       method_name,
                       test_settings,
                       headers=(await auth_header(response['body']['refresh_token']))
                   )
               )['status'] == http.HTTPStatus.OK

        assert (
           await method_refresh(test_settings, response['body']['refresh_token'])
        )['status'] == http.HTTPStatus.UNAUTHORIZED

        await redis_flush_db()

        assert (await method_refresh(test_settings, response['body']['refresh_token']))['status'] == http.HTTPStatus.OK

    # 3. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_access_revoke(
        generate_fake_users, pg_set_users, method_login, make_delete_request,
        clear_all, auth_header, redis_flush_db, method_get_profile
):
    method_name = '/api/v1/auth/access-revoke'

    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование отзыва токена доступа.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        assert (
                   await make_delete_request(
                       method_name,
                       test_settings,
                       headers=(await auth_header(response['body']['access_token']))
                   )
               )['status'] == http.HTTPStatus.OK

        assert (
                   await method_get_profile(test_settings, response['body']['access_token'])
               )['status'] == http.HTTPStatus.UNAUTHORIZED

        await redis_flush_db()

        assert (
                   await method_get_profile(test_settings, response['body']['access_token'])
               )['status'] == http.HTTPStatus.OK

    # 3. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_get_profile(
        generate_fake_users, pg_set_users, method_login, method_get_profile, clear_all
):
    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование получение профиля
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        response = await method_get_profile(test_settings, response['body']['access_token'])
        assert response['status'] == http.HTTPStatus.OK
        assert response['body']['login'] == user['login']
        assert response['body']['first_name'] == user['first_name']
        assert response['body']['last_name'] == user['last_name']
        assert response['body']['email'] == user['email']

    # 3. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_patch_profile(
        generate_fake_users, pg_set_users, method_login, clear_all, auth_header, make_patch_request
):
    method_name = '/api/v1/auth/profile'

    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование изменения логина.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        assert (
                   await make_patch_request(
                       method_name,
                       test_settings,
                       headers=await auth_header(response['body']['access_token']),
                       json={'login': user['login']+'_upd', 'password': ''}
                   )
               )['status'] == http.HTTPStatus.OK

        assert (
                   await method_login(test_settings, login=user['login'], password=user['password'])
               )['status'] == http.HTTPStatus.FORBIDDEN

        assert (
                   await method_login(test_settings, login=user['login'] + '_upd', password=user['password'])
               )['status'] == http.HTTPStatus.OK

    # 3. Тестирование изменения пароля.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login']+'_upd', password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        assert (
                   await make_patch_request(
                       method_name,
                       test_settings,
                       headers=await auth_header(response['body']['access_token']),
                       json={'login': '', 'password': user['password']+'_upd'}
                   )
               )['status'] == http.HTTPStatus.OK

        assert (
                   await method_login(test_settings, login=user['login'] + '_upd', password=user['password'])
               )['status'] == http.HTTPStatus.FORBIDDEN

        assert (
                   await method_login(test_settings, login=user['login'] + '_upd', password=user['password'] + '_upd')
               )['status'] == http.HTTPStatus.OK

    # 4. Тестирование одновременного изменения логина и пароля.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'] + '_upd', password=user['password'] + '_upd')
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        assert (
                   await make_patch_request(
                       method_name,
                       test_settings,
                       headers=await auth_header(response['body']['access_token']),
                       json={'login': user['login'], 'password': user['password']}
                   )
               )['status'] == http.HTTPStatus.OK

        assert (
                   await method_login(test_settings, login=user['login'] + '_upd', password=user['password'] + '_upd')
               )['status'] == http.HTTPStatus.FORBIDDEN

        assert (
                   await method_login(test_settings, login=user['login'], password=user['password'])
               )['status'] == http.HTTPStatus.OK

    # 5. Очистка.
    await clear_all()


@pytest.mark.asyncio(scope="session")
async def test_get_history(
        generate_fake_users, pg_set_users, method_login, clear_all, auth_header, make_get_request
):
    method_name = '/api/v1/auth/history'

    # 1. Подготовка данных.
    fake_users = await generate_fake_users(2)
    await pg_set_users(fake_users)

    # 2. Тестирование получение истории входов.
    for user in fake_users:
        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        response = await make_get_request(
            method_name,
            test_settings,
            headers=await auth_header(response['body']['access_token'])
        )
        assert response['status'] == http.HTTPStatus.OK
        assert len(response['body']) == 1

        response = await method_login(test_settings, login=user['login'], password=user['password'])
        assert response['status'] == http.HTTPStatus.OK
        assert 'access_token' in response['body']

        response = await make_get_request(
            method_name,
            test_settings,
            headers=await auth_header(response['body']['access_token'])
        )
        assert response['status'] == http.HTTPStatus.OK
        assert len(response['body']) == 2

    # 3. Очистка.
    await clear_all()
