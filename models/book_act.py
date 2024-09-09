import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.author_act import find_author
from models.db_act import RedisManager, engine, Book


class BookAdd(RedisManager):
    async def author_id(self, id_author, id_user) -> bool or None:
        author = await find_author(id_author)
        if author is None or False:
            return author
        # заканчивается проверка автора и добавляем новую книгу в редис для дальнейших действий

        data = {
            "author": id_author
        }
        return await self.set_data(id_user, data)

    async def add_data(self, id_user, add_data, key: str) -> bool or None:
        data = await self.get_data(id_user)
        if data is bool:
            return data
        data[key] = add_data
        return await self.set_data(id_user, data)

    async def end(self, id_user) -> bool or None:
        data = await self.get_data(id_user)
        if data is None or False:
            return data

        print(data)
        new_book = Book(
            name=data["name"],
            description=data["description"],
            author_id=data['author'],
            creator=id_user,
            formats=json.dumps(data['formats']),
            file=data['file']
        )
        async with (AsyncSession(engine) as session):
            session.add(new_book)
            try:
                await session.commit()
            except Exception as Error:
                print(Error)
                return False
        await self.del_data(id_user)
        return True


async def find_book_id(id_book):
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(select(Book).filter_by(id=id_book))
        except Exception as error:
            print(f'---ошибка поиска книги:{id_book}, result:{result}, id book: {id_book}, Error: {error}')
            return False
        await session.commit()
    return result.scalar_one_or_none()


async def find_book(text, page: int, page_size=5):
    async with AsyncSession(engine) as session:
        offset = (page - 1) * page_size
        try:
            result = await session.execute(select(Book).offset(offset).limit(page_size).filter_by(name=text))
        except Exception as error:
            print(f'---ошибка поиска книги:{text}, result:{result}, Error: {error}---')
            return False
        await session.commit()
    return result.scalars().all()
