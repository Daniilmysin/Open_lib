from sqlalchemy import Integer, String, \
    Column, Date, ForeignKey, Text, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import TSVECTOR
import asyncio
import logging
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker

logging.basicConfig(level=logging.INFO, filename="py_bot.log", format="%(asctime)s %(levelname)s %(message)s")
user= input("введите логин: ")
passwd= input("введите пароль: ")
host= input("введите хост")
engine = create_async_engine(f"postgresql+asyncpg://{user}:{passwd}@{host}/postgres")
session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass
class book(Base):
    __tablename__='Books'
    id= Column(Integer, primary_key=True)
    Name= Column(String(150), nullable=False)
    Author_id= Column(Integer, ForeignKey('author.id'))
    author = relationship("author")
    Description= Column(Text)
    Teg= Column(TSVECTOR)
    Search= Column(TSVECTOR)
    Date_birth= Column(Date, nullable=False)
    user_id= Column(Integer, ForeignKey('users.id'))
    check= Column(Boolean)
    adres_epub= Column(String(200),nullable=False)
    adres_pdf = Column(String(200))
    
class author(Base):
    __tablename__='author'
    id= Column(Integer, primary_key=True)
    name=Column(String(100),nullable=False)
    last_name=Column(String(100),nullable=False)
    patronymic = Column(String(100)) #отчество
    books = relationship("book")

class users(Base):
    __tablename__ = 'users'
    id= Column(Integer, primary_key=True)
    like_books= Column(Integer)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(main())
