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
    return author


async def find_author_all(text, page: int, page_size=5):
    async with AsyncSession(engine) as session:
        offset = (page - 1) * page_size
        try:
            result = await session.execute(select(Author).offset(offset).limit(page_size).filter_by(name=text))
        except Exception as error:
            print(f'---ошибка поиска aвтора:{text}, result:{result}, Error: {error}---')
            return False
        await session.commit()
    return result.scalars().all()


async def delete(id_book, id_user) -> bool:
    pass
