from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db_act import engine, User


async def find_user(id_user):
    async with AsyncSession(engine) as session:
        try:
            result_user = await session.execute(select(User).filter_by(id=id_user))
            result = result_user.scalar_one_or_none()
        except Exception as error:
            print(f'найти юзера ошибка: {error} ,юзер: {id_user} ')
            return False
        await session.commit()
    return result


async def add_user(id_user, name):
    user = await find_user(id_user)
    if user is not None:
        return True
    async with AsyncSession(engine) as session:
        try:
            session.add(User(id=id_user,
                             name=name))
            await session.commit()
        except Exception as error:
            print(f'ошибка добавления юзера: {error}')
    return True


async def ban_user(id_user, ban_bool: bool = True):
    user = await find_user(id_user)
    if user is None:
        return False
    async with AsyncSession(engine) as session:
        user.ban = ban_bool
        await session.commit()
    return True


async def admin_user(id_user, admin_bool: bool):
    user = await find_user(id_user)
    if user is None:
        return False
    async with AsyncSession(engine) as session:
        if user:
            user.admin = admin_bool
        else:
            return False
        await session.commit()
    return True
