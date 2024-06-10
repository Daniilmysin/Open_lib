from sqlalchemy import Integer, String, \
    Column, Date, ForeignKey, Text, Boolean, select
from sqlalchemy.dialects.postgresql import TSVECTOR
import asyncio, logging
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from dotenv import load_dotenv
import os

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
    author = relationship("author")
    description = Column(Text)
    teg = Column(TSVECTOR)
    search = Column(TSVECTOR)
    sate_birth = Column(Date)
    creator = Column(Integer, ForeignKey('user.id'))
    check = Column(Boolean, default=False)
    adres = Column(String(200))


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    last_name = Column(String(100))
    patronymic = Column(String(100))  #отчество
    creator = Column(Integer, ForeignKey("user.id"))
    photo = Column(String(100))
    check = Column(Boolean, default=False)
    books = relationship("book")


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    books = relationship("book")
    authors = relationship("author")
    status = Column(Integer)
    admin = Column(Boolean, default=False)
    ban = Column(Boolean, default=False)


class UserAct():
    async def add_user(id, name):
        async with AsyncSession(engine) as session:
            session.add(User(id=id,
                             name=name))
            await session.commit()
        return

    async def ban_user(id):
        async with AsyncSession(engine) as session:
            session.add(User(id=id,
                             ban=True))
            await session.commit()
        pass

    async def find_user(id):
        pass

    async def change_user(id, change):
        pass


class BookAct:
    class BookAdd:
        async def name(name: str, id_user):
            async with AsyncSession(engine) as session:
                user_book = ""
                add_book = Book(
                    id=user_book,
                    name=name
                )
                session.add(add_book)

                await session.commit()
                return True

        async def author_id(author_id: int, id_user):
            stmt = select(Author).where(Author.id == author_id)
            stmt1 = select(User).where(User.id == id_user)
            async with AsyncSession(engine) as session:
                result = await session.execute(stmt)
                result1 = await session.execute(stmt1)
                session.add(Book(
                    author=result.scalars().one(),
                    creator=id_user
                ))

                await session.commit()
                return True

        async def description(des, id_user):
            user_book = ""
            async with AsyncSession(engine) as session:
                session.add(Book(
                    id=user_book,
                    description=des
                ))
                try:
                    await session.commit()
                except Exception:
                    return False
                return True

            async def end(id_user):
                pass


async def search_name(search, where_search="id"):
    async with (AsyncSession(engine) as session):
        if where_search == "id":
            stmt = select(Book).where(Book.id == search)
        elif where_search == ("Name"):
            stmt = select(Book.id).where(Book.Name == search)
        elif where_search == ("dis"):
            stmt = select(Book.Name).where(Book.description == search)
        result = await session.execute(stmt)
        a1 = result.scalars().all()
        print(a1)
        return a1


async def make_BD():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(search_name(2))
