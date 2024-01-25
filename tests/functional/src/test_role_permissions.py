import http
from random import randrange

import pytest

from tests.functional.settings import test_settings
from tests.functional.testdata.roles_test_data import get_admin_data


async def prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login, auth_header,
                                           pg_get_permissions, generate_fake_permissions, pg_drop_users, pg_drop_roles,
                                           pg_drop_role_permissions):
    # 1. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()

    # 2. Подготовка данных.
    fake_roles = await generate_fake_roles()
    await pg_set_roles(fake_roles)
    admin = await get_admin_data()
    await pg_set_users([admin])
    fake_roles_test = await generate_fake_roles()
    permissions = await pg_get_permissions()
    fake_permissions = await generate_fake_permissions()

    # 3. Авторизация под админом
    response = await method_login(test_settings, login=admin['login'], password=admin['password'])
    access_token = response['body']['access_token']
    headers = await auth_header(access_token)
    return fake_roles, fake_roles_test, permissions, fake_permissions, headers


@pytest.mark.asyncio(scope="session")
async def test_assign_role_permission(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header, pg_get_permissions, generate_fake_permissions,
        pg_drop_role_permissions
):
    method_name = '/api/v1/roles/{role_id}/permissions/{permission_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, permissions, fake_permissions, headers = \
        await prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login,
                                               auth_header, pg_get_permissions, generate_fake_permissions,
                                               pg_drop_users, pg_drop_roles, pg_drop_role_permissions)

    # 2. Тестирование назначения доступа ролям
    for role in fake_roles:
        permission = permissions[randrange(0, len(permissions))]
        response = await make_post_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.CREATED

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()


@pytest.mark.asyncio(scope="session")
async def test_assign_role_permission_role_or_permission_not_found(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header, pg_get_permissions, generate_fake_permissions,
        pg_drop_role_permissions):

    method_name = '/api/v1/roles/{role_id}/permissions/{permission_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, permissions, fake_permissions, headers = \
        await prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login,
                                               auth_header, pg_get_permissions, generate_fake_permissions,
                                               pg_drop_users, pg_drop_roles, pg_drop_role_permissions)

    # 2. Тестирование назначения доступа ролям, роль не найдена
    for role in fake_roles_test:
        permission = permissions[randrange(0, len(permissions))]
        response = await make_post_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 4. Тестирование назначения доступа ролям, доступ не найден
    for role in fake_roles:
        permission = fake_permissions[randrange(0, len(permissions))]
        response = await make_post_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()


@pytest.mark.asyncio(scope="session")
async def test_assign_role_permission_role_permission_already_exist(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header, pg_get_permissions, generate_fake_permissions,
        pg_drop_role_permissions):

    method_name = '/api/v1/roles/{role_id}/permissions/{permission_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, permissions, fake_permissions, headers = \
        await prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login,
                                               auth_header, pg_get_permissions, generate_fake_permissions,
                                               pg_drop_users, pg_drop_roles, pg_drop_role_permissions)
    i = 0
    for role in fake_roles:
        permission = permissions[i % len(permissions)]
        await make_post_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        i += 1

    # 2. Тестирование назначения доступа ролям, доступ роли существует
    i = 0
    for role in fake_roles:
        permission = permissions[i % len(permissions)]
        response = await make_post_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        i += 1
        assert response['status'] == http.HTTPStatus.BAD_REQUEST

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()


@pytest.mark.asyncio(scope="session")
async def test_delete_role_permission(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header, pg_get_permissions, generate_fake_permissions,
        pg_drop_role_permissions, make_delete_request):
    method_name = '/api/v1/roles/{role_id}/permissions/{permission_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, permissions, fake_permissions, headers = \
        await prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login,
                                               auth_header, pg_get_permissions, generate_fake_permissions,
                                               pg_drop_users, pg_drop_roles, pg_drop_role_permissions)
    i = 0
    for role in fake_roles:
        permission = permissions[i % len(permissions)]
        await make_post_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        i += 1

    # 2. Тестирование удаления доступа ролей
    i = 0
    for role in fake_roles:
        permission = permissions[i % len(permissions)]
        response = await make_delete_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        i += 1
        assert response['status'] == http.HTTPStatus.NO_CONTENT

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()


@pytest.mark.asyncio(scope="session")
async def test_delete_role_permission_not_found(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header, pg_get_permissions, generate_fake_permissions,
        pg_drop_role_permissions, make_delete_request):
    method_name = '/api/v1/roles/{role_id}/permissions/{permission_id}'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, permissions, fake_permissions, headers = \
        await prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login,
                                               auth_header, pg_get_permissions, generate_fake_permissions,
                                               pg_drop_users, pg_drop_roles, pg_drop_role_permissions)

    # 2. Тестирование удаления несуществующих доступов ролей
    for role in fake_roles:
        permission = permissions[randrange(0, len(permissions))]
        response = await make_delete_request(
            method_name.format(role_id=role['id'], permission_id=permission['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.NOT_FOUND

    # 3. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()


@pytest.mark.asyncio(scope="session")
async def test_get_role_permissions(
        pg_drop_roles, pg_drop_users, generate_fake_roles, make_post_request, pg_set_roles,
        pg_set_users, method_login, auth_header, pg_get_permissions, generate_fake_permissions,
        pg_drop_role_permissions, make_get_request):
    method_name = '/api/v1/roles/{role_id}/permissions'

    # 1. Подготовка данных.
    fake_roles, fake_roles_test, permissions, fake_permissions, headers = \
        await prepare_to_role_permissions_test(generate_fake_roles, pg_set_roles, pg_set_users, method_login,
                                               auth_header, pg_get_permissions, generate_fake_permissions,
                                               pg_drop_users, pg_drop_roles, pg_drop_role_permissions)
    i = 0
    for role in fake_roles:
        permission = permissions[i % len(permissions)]
        await make_post_request(
            method_name.format(role_id=role['id']) + '/' + str(permission['id']), test_settings,
            headers=headers
        )
        i += 1

    # 2. Тестирование получения списка доступов роли
    for role in fake_roles:
        response = await make_get_request(
            method_name.format(role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.OK
        assert len(response['body']) == 1

    # 3. Тестирование получения списка доступов несуществующей роли
    for role in fake_roles_test:
        response = await make_get_request(
            method_name.format(role_id=role['id']), test_settings,
            headers=headers
        )
        assert response['status'] == http.HTTPStatus.OK
        assert len(response['body']) == 0

    # 4. Очистка таблиц
    await pg_drop_users()
    await pg_drop_roles()
    await pg_drop_role_permissions()
