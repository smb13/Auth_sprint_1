import http
from random import randrange

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.roles_test_data import get_admin_data


async def get_headers(auth_header, method_login):
    # Авторизация под админом
    admin = await get_admin_data()
    response = await method_login(test_settings, login=admin['login'], password=admin['password'])
    access_token = response['body']['access_token']
    headers = await auth_header(access_token)
    return headers


async def prepare_to_user_roles_test(generate_fake_roles, generate_fake_users, pg_set_roles, pg_set_users,
                                     pg_drop_users, pg_drop_roles, pg_drop_user_roles):
    # 1. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_user_roles()

    # 2. Подготовка данных.
    fake_roles = await generate_fake_roles()
    await pg_set_roles(fake_roles)
    fake_roles_test = await generate_fake_roles()
    fake_users = await generate_fake_users(10)
    admin = await get_admin_data()
    fake_users.append(admin)
    await pg_set_users(fake_users)
    fake_users_test = await generate_fake_users(10)

    return fake_roles, fake_roles_test, fake_users, fake_users_test


@pytest.mark.asyncio(scope="session")
async def test_assign_user_role(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles, generate_fake_users,
        pg_set_users, method_login, auth_header, pg_drop_user_roles
):
    method_name = '/api/v1/users/{user_id}/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, fake_users, fake_users_test = \
        await prepare_to_user_roles_test(generate_fake_roles, generate_fake_users, pg_set_roles, pg_set_users,
                                         pg_drop_users, pg_drop_roles, pg_drop_user_roles)

    # 2. Тестирование назначения роли пользователям
    for user in fake_users:
        headers = await get_headers(auth_header, method_login)
        role = fake_roles[randrange(0, len(fake_roles))]
        response = await make_post_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.CREATED

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_user_roles()


@pytest.mark.asyncio(scope="session")
async def test_assign_user_role_user_or_role_not_found(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles, generate_fake_users,
        pg_set_users, method_login, auth_header, pg_drop_user_roles
):
    method_name = '/api/v1/users/{user_id}/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, fake_users, fake_users_test = \
        await prepare_to_user_roles_test(generate_fake_roles, generate_fake_users, pg_set_roles, pg_set_users,
                                         pg_drop_users, pg_drop_roles, pg_drop_user_roles)
    headers = await get_headers(auth_header, method_login)

    # 2. Тестирование назначения ролей пользователям, пользователь не найден
    for user in fake_users_test:
        role = fake_roles[randrange(0, len(fake_roles))]
        response = await make_post_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 3. Тестирование назначения ролей пользователям, роль не найдена
    for user in fake_users:
        role = fake_roles_test[randrange(0, len(fake_roles_test))]
        response = await make_post_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 4. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_user_roles()


@pytest.mark.asyncio(scope="session")
async def test_assign_user_role_user_role_already_exist(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles, generate_fake_users,
        pg_set_users, method_login, auth_header, pg_drop_user_roles
):

    method_name = '/api/v1/users/{user_id}/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, fake_users, fake_users_test = \
        await prepare_to_user_roles_test(generate_fake_roles, generate_fake_users, pg_set_roles, pg_set_users,
                                         pg_drop_users, pg_drop_roles, pg_drop_user_roles)
    i = 0
    for user in fake_users:
        headers = await get_headers(auth_header, method_login)
        role = fake_roles[i % len(fake_roles)]
        await make_post_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        i += 1

    # 2. Тестирование назначения уже назначенных ролей пользователям
    i = 0
    for user in fake_users:
        headers = await get_headers(auth_header, method_login)
        role = fake_roles[i % len(fake_roles)]
        response = await make_post_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        i += 1
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_user_roles()


@pytest.mark.asyncio(scope="session")
async def test_delete_user_role(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles, generate_fake_users,
        pg_set_users, method_login, auth_header, pg_drop_user_roles, make_delete_request
):

    method_name = '/api/v1/users/{user_id}/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, fake_users, fake_users_test = \
        await prepare_to_user_roles_test(generate_fake_roles, generate_fake_users, pg_set_roles, pg_set_users,
                                         pg_drop_users, pg_drop_roles, pg_drop_user_roles)
    i = 0
    for user in fake_users:
        headers = await get_headers(auth_header, method_login)
        role = fake_roles[i % len(fake_roles)]
        await make_post_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        i += 1

    # 2. Тестирование удаления ролей пользователей
    i = 0
    for user in fake_users:
        headers = await get_headers(auth_header, method_login)
        role = fake_roles[i % len(fake_roles)]
        response = await make_delete_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        i += 1
        assert response['status'] == http.HTTPStatus.NO_CONTENT

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_user_roles()


@pytest.mark.asyncio(scope="session")
async def test_delete_user_role_not_found(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles, generate_fake_users,
        pg_set_users, method_login, auth_header, pg_drop_user_roles, make_delete_request
):
    method_name = '/api/v1/users/{user_id}/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, fake_users, fake_users_test = \
        await prepare_to_user_roles_test(generate_fake_roles, generate_fake_users, pg_set_roles, pg_set_users,
                                         pg_drop_users, pg_drop_roles, pg_drop_user_roles)

    # 2. Тестирование удаления несуществующих ролей пользователей
    for user in fake_users:
        headers = await get_headers(auth_header, method_login)
        role = fake_roles[randrange(0, len(fake_roles))]
        response = await make_delete_request(
            method_name.format(user_id=user['id'], role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.NOT_FOUND

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_user_roles()
