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
    id = Column(primary_key=True, autoincrement=True)
    name = Column(String(150))
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship("Author")
    description = Column(Text)
    teg = Column(TSVECTOR)
    search = Column(TSVECTOR)
    last_update = Column(Date, onupdate=datetime.datetime.now)
    creator = Column(Integer, ForeignKey('user.id'))
    check = Column(Boolean, default=False)
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
        try:
            serialized_data = orjson.dumps(data)
            await self.redis.set(key, serialized_data)
            return True
        except Exception as e:
            # Обработка ошибки
            print(f"Error setting data: {e}")
            return False

    async def get_data(self, key):
        try:
            data = await self.redis.get(key)
            if data:
                return orjson.loads(data)
            return None
        except Exception as e:
            # Обработка ошибки
            print(f"Error getting data: {e}")
            return None

    async def close(self):
        await self.redis.aclose()

class UserAct():
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

    @staticmethod
    async def find_user(id_user):
        async with AsyncSession(engine) as session:
            try:
                result_user = await session.execute(select(User).filter_by(id=id_user))
                result = result_user.scalar_one_or_none()
            except Exception as error:
                print(f'ошибка:{error},юзер:{id_user}')
                return False
            await session.commit()
        return result

    @staticmethod
    async def change_user(user_id, change: dict):
        pass


class AuthorAct:
    class AuthorAdd(RedisManager):
        async def name(self, name, id_user) -> bool:
            name_list = name.split()
            data = {
                "name": name_list[0],
                "surname": name_list[1],
                "patronymic": name_list[2],
                "id": id_user
            }
            return await self.set_data(id_user, data)

        async def url(self, url, id_user) -> bool or None:
            data = await self.get_data(id_user)
            data["url"] = url
            return self.set_data(id_user, data)

        async def descripton(self, description, id_user) -> bool or None:
            data = self.get_data(id_user)
            data["description"] = description
            return self.set_data(id_user, data)

        async def end(id_user) -> bool:
            pass

    async def delete(self, id_book, id_user) -> bool:
        pass


class BookAct:
    class BookAdd(RedisManager):
        async def author_id(self, id_author, id_user) -> bool or None:
            async with AsyncSession(engine) as session:
                result_author = await session.execute(select(Author).filter_by(id=id_author))
                author = result_author.scalar_one_or_none()
                if author is None:
                    return None
                try:
                    await session.commit()
                except Exception as error:
                    print(f'ошибка:{error},юзер:{id_user}')
                    return False
            # заканчивается проверка автора и добавляем новую книгу в редис для дальнейших действий
            data = {
                "author": id_author
            }
            return await self.set_data(id_user, data)

        async def name(self, name, id_user) -> bool or None:
            data = await self.get_data(id_user)
            data["name"] = name
            return await self.set_data(id_user, data)

        async def description(self, id_user, description) -> bool or None:
            data = await self.get_data(id_user)
            data["description"] = description
            return await self.set_data(id_user, data)

        async def photo(self, id_user, photo) -> bool or None:
            data = await self.get_data(id_user)
            data["photo"] = photo
            return await self.set_data(id_user, data)

        async def end(self, id_user, epub) -> bool or None:
            data = await self.get_data(id_user)

            async with (AsyncSession(engine) as session):
                result_author = await session.execute(select(Author).filter_by(id=data["author"]))
                result_user = await session.execute(select(Author).filter_by(id=id_user))
                user = result_user.scalar_one_or_none()
                author = result_author.scalar_one_or_none()
                session.add(Book(
                    name=data["name"],
                    description=data["description"],
                    author_id=author,
                    user=user,
                    photo=data["photo"],
                    epub=epub,
                ))


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

    async def del_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def make_bd(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


AuthorAdd = AuthorAct.AuthorAdd()

asyncio.run(AuthorAdd.name(name='иван иванович иванов', id_user=1121))
