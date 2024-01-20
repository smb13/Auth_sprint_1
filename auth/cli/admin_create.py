from asyncio import run
from getpass import getpass

from sqlalchemy import select

from db.postgres import async_session
from models.user import User


async def main():
    async with async_session() as db:
        email = str(input('Введите email нового пользователя: '))
        login = str(input('Введите login нового пользователя: '))
        result = await db.execute(select(User).where(User.email == email or User.login == login))
        user = result.scalars().first()

        if user:
            print('Пользователь с таким email уже есть в базе.')
            return
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
        return


if __name__ == '__main__':
    run(main())
