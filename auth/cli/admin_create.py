from getpass import getpass

from asyncio import run
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import async_session
from models.role import Role, UserRole, admin_role_name
from models.user import User


async def get_admin_role_id(db: AsyncSession) -> UUID:
    result = await db.execute(select(Role).where(Role.name == admin_role_name))
    admin_role = result.scalars().first()

    if admin_role:
        print(f'Роль {admin_role_name} уже есть в базе.')
        return admin_role.id

    admin_role = Role(name=admin_role_name)
    db.add(admin_role)
    await db.commit()
    await db.refresh(admin_role)
    print('Роль admin добавлена в базу.')
    return admin_role.id


async def get_user_id(db: AsyncSession, email: str, login: str) -> UUID:
    result = await db.execute(select(User).where(User.email == email or User.login == login))
    user = result.scalars().first()

    if user:
        print('Пользователь с таким email уже есть в базе.')
        return user.id
    while True:
        password = getpass(prompt='Введите пароль нового пользователя: ')
        password_repeat = getpass(prompt='Повторите пароль нового пользователя: ')
        if password == password_repeat:
            break
        print('Пароли не совпадают, повторите ввод')

    first_name = str(input('Введите имя нового пользователя: '))
    last_name = str(input('Введите фамилию нового пользователя: '))

    user = User(
        email=email, password=password, first_name=first_name,
        last_name=last_name, login=login, superuser=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    print('Пользователь добавлен в базу.')
    return user.id


async def main():
    async with async_session() as db:
        email = str(input('Введите email нового пользователя: '))
        login = str(input('Введите login нового пользователя: '))
        user_id = await get_user_id(db, email, login)
        role_id = await get_admin_role_id(db)

        result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id,
                                   UserRole.role_id == role_id)
        )
        user_role = result.scalars().first()

        if user_role:
            print(f'У пользователя уже есть роль {admin_role_name}.')
            return

        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        await db.commit()
        print(f'Пользователю добавлена роль {admin_role_name}.')


if __name__ == '__main__':
    run(main())
