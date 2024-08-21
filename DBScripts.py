from sqlalchemy import Integer, String, \
    Column, Date, ForeignKey, Text, Boolean, select
from sqlalchemy.dialects.postgresql import TSVECTOR
import asyncio, logging, datetime  # асинк нужен для тестов
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from dotenv import load_dotenv
import os, orjson
import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()
user = str(os.getenv("user"))
passwd = str(os.getenv("passwd"))
host = str(os.getenv("host"))

engine = create_async_engine(f"postgresql+asyncpg://{user}:{passwd}@{host}/postgres", echo=True)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship("Author")
    description = Column(Text)
    teg = Column(TSVECTOR)
    search = Column(TSVECTOR)
    last_update = Column(Date, onupdate=datetime.datetime.now)
    creator = Column(Integer, ForeignKey('user.id'))
    check = Column(Boolean, default=False)
    epub = Column(String(150))
    url = Column(String(200))


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    last_name = Column(String(100))
    patronymic = Column(String(100))
    creator = Column(Integer, ForeignKey("user.id"))
    description = Column(Text)
    photo = Column(String(100))
    check = Column(Boolean, default=False)
    books = relationship("Book")
    url = Column(String(300))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    books = relationship("Book")
    authors = relationship("Author")
    status = Column(Integer)
    admin = Column(Boolean, default=False)
    ban = Column(Boolean, default=False)


# класс работы с менеджером
class RedisManager:
    def __init__(self):
        self.redis = aioredis.Redis()

    async def set_data(self, key, data) -> bool:
        async with self.redis as r:
            try:
                serialized_data = orjson.dumps(data)
                await r.set(key, serialized_data)
                await r.aclose()
                return True
            except Exception as e:
                # Обработка ошибки
                print(f"Error setting data: {e}")
                return False

    async def get_data(self, key):
        async with self.redis as r:
            try:
                data = await r.get(key)
            except Exception as e:
                # Обработка ошибки
                print(f"Error getting data: {e}")
                return None
            if data:
                return orjson.loads(data)

            return None

    async def del_data(self, key):
        async with self.redis as r:
            try:
                data = await r.delete(key)
                await r.aclose()
            except Exception as e:
                # Обработка ошибки
                print(f"Error deleting: {e}")
                return False


class UserAct:
    @staticmethod
    async def add_user(user_id, name):
        async with AsyncSession(engine) as session:
            session.add(User(id=user_id,
                             name=name))
            await session.commit()
        return

    @staticmethod
    async def ban_user(id_user, ban: bool = True):
        async with AsyncSession(engine) as session:
            try:
                result_user = await session.execute(select(User).filter_by(id=id_user))
                result = result_user.scalar_one_or_none()
            except Exception as error:
                print(f'ошибка:{error},юзер:{id_user}')
                return False
            session.add(User(id=result,
                             ban=ban))
            await session.commit()
        return True

    async def find_user(self, id_user):
        async with AsyncSession(engine) as session:
            try:
                result_user = await session.execute(select(User).filter_by(id=id_user))
                result = result_user.scalar_one_or_none()
            except Exception as error:
                print(f'ошибка: {error} ,юзер: {id_user} ')
                return False
            await session.commit()
        return result

    @staticmethod
    async def change_user(user_id, change: dict):
        pass


class AuthorAct:
    class AuthorAdd(RedisManager, UserAct):
        async def name(self, id_user, name) -> bool:
            name_list = name.split()
            data = {
                "name": name_list[0],
                "surname": name_list[1],
                "patronymic": name_list[2],
                "id": id_user
            }
            return await self.set_data(id_user, data)

        async def url(self, id_user, url) -> bool or None:
            data = await self.get_data(id_user)
            data["url"] = url
            return await self.set_data(id_user, data)

        async def description(self, id_user, description) -> bool or None:
            data = await self.get_data(id_user)
            data["description"] = description
            return await self.set_data(id_user, data)

        async def photo(self, id_user, photo) -> bool or None:
            data = await self.get_data(id_user)
            data["photo"] = photo
            return await self.set_data(id_user, data)

        async def end(self, id_user) -> bool:
            data = await self.get_data(id_user)
            user = await self.find_user(id_user)
            if user is None:
                print('user is not exist')
                return False
            print(data)
            async with AsyncSession(engine) as session:
                session.add(Author(
                    name=data['name'],
                    last_name=data['surname'],
                    patronymic=data['patronymic'],
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

    async def find_author(self, id_author):
        async with AsyncSession(engine) as session:
            result_author = await session.execute(select(Author).filter_by(id=id_author))
            author = result_author.scalar_one_or_none()
            try:
                await session.commit()
            except Exception as error:
                print(f'ошибка:{error},юзер:{id_author}')
                return False
        if author is None:
            print('author is None')
        return author

    async def delete(self, id_book, id_user) -> bool:
        pass


class BookAct:
    class BookAdd(RedisManager, UserAct, AuthorAct):
        async def author_id(self, id_author, id_user) -> bool or None:
            author = await self.find_author(id_author)
            if author is None or False:
                return author
            # заканчивается проверка автора и добавляем новую книгу в редис для дальнейших действий

            data = {
                "author": id_author
            }
            return await self.set_data(id_user, data)

        async def name(self, id_user, name) -> bool or None:
            data = await self.get_data(id_user)
            data['name'] = name
            return await self.set_data(id_user, data)

        async def description(self, id_user, description) -> bool or None:
            data = await self.get_data(id_user)
            data['description'] = description
            return await self.set_data(id_user, data)

        async def url(self, id_user, url) -> bool or None:
            data = await self.get_data(id_user)
            data['url'] = url
            return await self.set_data(id_user, data)

        async def end(self, id_user, epub) -> bool or None:
            data = await self.get_data(id_user)
            print(data)
            async with (AsyncSession(engine) as session):
                session.add(Book(
                    name=data["name"],
                    description=data["description"],
                    author_id=data['author'],
                    creator=id_user,
                    epub=epub,
                ))
                try:
                    await session.commit()
                except Exception as Error:
                    print(Error)
                    return False
            await self.del_data(id_user)
            return True


class BDAct:
    async def search(self, search, where_search="id"):
        async with (AsyncSession(engine) as session):
            if where_search == "id":
                stmt = select(Book).filter_by(Book.id == search)
            elif where_search == ("Name"):
                stmt = select(Book.id).filter_by(Book.name == search)
            elif where_search == ("dis"):
                stmt = select(Book.name).filter_by(Book.description == search)
            result = await session.execute(select(User))
            users = result.scalars().all()
            #a1 = result.scalars().all()
            print("========")
            print(users)

    @staticmethod
    async def del_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def make_bd():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


aut = AuthorAct().AuthorAdd()
bok = BookAct().BookAdd()
#asyncio.run(bok.author_id(4, 1111))
#asyncio.run(bok.name(1111, 'test'))
#asyncio.run(bok.description(1111, 'test'))
#asyncio.run(bok.url(1111, 'photo'))
#asyncio.run(bok.end(1111,'test'))
asyncio.run(aut.name(1111, 'иван иванович иванав'))
asyncio.run(aut.description(1111, 'test'))
asyncio.run(aut.photo(1111, 'photo'))
asyncio.run(aut.end(1111))
