import json

import orjson
import os
import redis.asyncio as aioredis
from dotenv import load_dotenv
from sqlalchemy import Integer, String, \
    Column, ForeignKey, Text, Boolean, select, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship

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
    author_id = Column(Integer, ForeignKey('author.id'))  # ссылка на автора
    description = Column(Text)
    creator = Column(Integer, ForeignKey('user.id'))  # ссылка на того что добавил книгу
    check = Column(Boolean, default=False)
    file = Column(String(150))
    formats = Column(JSON)


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    creator = Column(Integer, ForeignKey("user.id"))
    description = Column(Text)
    photo = Column(String(100))
    check = Column(Boolean, default=False)
    books = relationship("Book")


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

            except Exception as e:
                # Обработка ошибки
                print(f"Error setting data: {e}")
                return False
            return True

    async def set_array(self, key, format):
        async with self.redis as r:
            data = await self.get_data(key)
            if 'formats' in data:
                if format in data['formats']:
                    return False

                if format not in data['formats']:
                    data['formats'].append(format)
            else:
                # Если списка форматов нет, создаем его
                data['formats'] = [format]
            try:
                serialized_data = json.dumps(data)
                await r.set(key, serialized_data)
                await r.aclose()

            except Exception as e:
                # Обработка ошибки
                print(f"Error setting array data: {e}")
                return e
            return True

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


async def del_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def make_bd():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
