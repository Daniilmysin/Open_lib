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
    author_id = Column(Integer, ForeignKey('author.id')) # ссылка на автора
    description = Column(Text)
    creator = Column(Integer, ForeignKey('user.id')) # ссылка на того что добавил книгу
    check = Column(Boolean, default=False)
    epub = Column(String(150))


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
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
            return False

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
    async def find_user(self, id_user):
        async with AsyncSession(engine) as session:
            try:
                result_user = await session.execute(select(User).filter_by(id=id_user))
                result = result_user.scalar_one_or_none()
            except Exception as error:
                print(f'найти юзера ошибка: {error} ,юзер: {id_user} ')
                return False
            await session.commit()
        return result

    @staticmethod
    async def add_user(user_id, name):
        async with AsyncSession(engine) as session:
            session.add(User(id=user_id,
                             name=name))
            await session.commit()
        return True

    async def ban_user(self, id_user, ban_bool: bool = True):
        user = await self.find_user(id_user)
        async with AsyncSession(engine) as session:
            if user:
                user.ban = ban_bool
            else:
                return False
            await session.commit()
        return True

    async def admin_user(self, id_user, admin_bool: bool):
        user = await self.find_user(id_user)
        async with AsyncSession(engine) as session:
            if user:
                user.admin = admin_bool
            else:
                return False
            await session.commit()
        return True

    @staticmethod
    async def change_user(user_id, change: dict):
        pass


class AuthorAct:
    class AuthorAdd(RedisManager, UserAct):
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

    async def find_author(self, id_author):
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

        async def add_data(self, id_user, add_data, key:str) -> bool or None:
            data = await self.get_data(id_user)
            data[key] = add_data
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
    async def search(self, search, where_search="id"):# чисто тестовая функция чтобы разобраться как работает запросы к бд
        async with (AsyncSession(engine) as session):
            if where_search == "id":
                stmt = select(Book).filter_by(id=search)
            elif where_search == ("Name"):
                stmt = select(Book.id).filter_by(name=search)
            elif where_search == ("dis"):
                stmt = select(Book.name).filter_by(description=search)
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