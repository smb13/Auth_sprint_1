import http
from random import randint, randrange

import pytest

from tests.functional.testdata.roles_test_data import get_admin_data
from tests.functional.settings import test_settings


async def prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login, auth_header,
                                pg_drop_users, pg_drop_roles):
    # 1. Очистка таблиц.
    await pg_drop_users()
    await pg_drop_roles()

    # 2. Подготовка данных.
    fake_roles = await generate_fake_roles()
    await pg_set_roles(fake_roles)
    admin = await get_admin_data()
    await pg_set_users([admin])
    fake_roles_test = await generate_fake_roles()

    # 3. Авторизация под админом
    response = await method_login(test_settings, login=admin['login'], password=admin['password'])
    access_token = response['body']['access_token']
    headers = await auth_header(access_token)
    return fake_roles, fake_roles_test, headers


@pytest.mark.asyncio(scope="session")
async def test_post_role(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование создания новых ролей
    for role in fake_roles_test:
        response = await make_post_request(
            method_name, test_settings, json={'name': role['name']},
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.CREATED
        assert 'id' in response['body']

    # 4. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_post_role_name_exist(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование создания повторных ролей
    for role in fake_roles:
        response = await make_post_request(
            method_name, test_settings, json={'name': role['name']},
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_patch_role(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_patch_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование patch ролей
    new_fake_roles = await generate_fake_roles(100)
    for role_to_patch in new_fake_roles:
        role = fake_roles[randrange(0, len(fake_roles))]
        response = await make_patch_request(
            method_name.format(role_id=role['id']), test_settings, json={'name': role_to_patch['name']},
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.OK
        assert 'id' in response['body']

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_patch_role_not_found(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_patch_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование patch несуществующих ролей
    for role in fake_roles_test:
        response = await make_patch_request(
            method_name.format(role_id=role['id']), test_settings, json={'name': role['name']},
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.NOT_FOUND

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_patch_role_name_exist(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_patch_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование patch с существующим именем
    for role_to_patch in fake_roles:
        while True:
            role = fake_roles[randrange(0, len(fake_roles))]
            if role != role_to_patch:
                break
        response = await make_patch_request(
            method_name.format(role_id=role_to_patch['id']), test_settings, json={'name': role['name']},
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_delete_role(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_delete_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование delete
    for role in fake_roles:
        response = await make_delete_request(
            method_name.format(role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.NO_CONTENT

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_delete_role_not_found(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_delete_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles/{role_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование delete несуществующей роли
    for role in fake_roles_test:
        response = await make_delete_request(
            method_name.format(role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.NOT_FOUND

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()


@pytest.mark.asyncio(scope="session")
async def test_roles_list(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_get_request, pg_set_roles,
        pg_set_users, method_login, auth_header
):
    method_name = '/api/v1/roles'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, headers = await prepare_to_roles_test(generate_fake_roles, pg_set_roles, pg_set_users,
                                                                       method_login, auth_header, pg_drop_users,
                                                                       pg_drop_roles)

    # 2. Тестирование получения списка ролей
    response = await make_get_request(
        method_name, test_settings, headers=headers
    )
    assert response['status'] == http.HTTPStatus.OK
    assert len(fake_roles) == len(response['body'])

    # 3. Очистка.
    await pg_drop_users()
    await pg_drop_roles()

