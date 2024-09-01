from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RedisManager, engine, Author


class AddAuthor(RedisManager):
    async def name(self, id_user, name) -> bool:
        data = {
            "name": name
        }
        return await self.set_data(id_user, data)

    async def add_data(self, id_user, add_data, key) -> bool or None:
        data = await self.get_data(id_user)
        data[str(key)] = add_data
        return await self.set_data(id_user, data)

    async def end(self, id_user) -> bool:
        data = await self.get_data(id_user)
        print(data)
        async with AsyncSession(engine) as session:
            session.add(Author(
                name=data['name'],
                description=data['description'],
                photo=data['photo'],
                creator=id_user
            ))
            try:
                await session.commit()
            except Exception as error:
                print(error)
                return False
        await self.del_data(id_user)
        return True


async def find_author(id_author):
    async with AsyncSession(engine) as session:
        result_author = await session.execute(select(Author).filter_by(id=id_author))
        author = result_author.scalar_one_or_none()
        try:
            await session.commit()
        except Exception as error:
            print(f'поиск автора ошибка:{error},юзер:{id_author}')
            return False
    if author is None:
        print('author is not exist')
    return author


async def delete(id_book, id_user) -> bool:
    pass
