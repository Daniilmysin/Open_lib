from sqlalchemy import Integer, String, \
    Column, Date, ForeignKey, Text, Boolean, select
from sqlalchemy.dialects.postgresql import TSVECTOR
import asyncio, logging
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
#user= input("введите логин: ")
#passwd= input("введите пароль: ")
#host= input("введите хост: ")
user= 'postgres'
passwd= 'postgres'
host= 'localhost'
engine = create_async_engine(f"postgresql+asyncpg://{user}:{passwd}@{host}/postgres", echo=True)
#Async_session = AsyncSession(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class book(Base):
    __tablename__='book'
    id= Column(Integer, primary_key=True, autoincrement=True)
    Name= Column(String(150))
    Author_id= Column(Integer, ForeignKey('author.id'))
    author = relationship("author")
    description= Column(Text)
    Teg= Column(TSVECTOR)
    Search= Column(TSVECTOR)
    Date_birth= Column(Date)
    creator= Column(Integer, ForeignKey('user.id'))
    check= Column(Boolean, default=False)
    adres= Column(String(200))

class author(Base):
    __tablename__='author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    last_name = Column(String(100))
    patronymic = Column(String(100)) #отчество
    creator= Column(Integer, ForeignKey("user.id"))
    photo = Column(String(100))
    check = Column(Boolean, default=False)
    books = relationship("book")


class user(Base):
    __tablename__ = 'user'
    id= Column(Integer, primary_key=True)
    name = Column(String(100))
    books = relationship("book")
    authors = relationship("author")
    status = Column(Integer)
    admin= Column(Boolean, default=False)
    ban = Column(Boolean, default=False)

class user_act():
    async def add_user(id, name):
        async with AsyncSession(engine) as session:
            session.add(user(id=id,
                             name=name))
            await session.commit()
        return

    async def ban_user(id):
        async with AsyncSession(engine) as session:
            session.add(user(id=id,
                             ban=True))
            await session.commit()
        pass
    async def find_user(id):
        pass
    async def change_user(id, change):
        pass

class add_book:
    async def name( name:str, id_user):
        async with AsyncSession(engine) as session:
            user_book=""
            add_book=book(
                        id=user_book,
                        name=name
                        )
            session.add(add_book)

            await session.commit()
            return True
    async def author_id(author_id:int , id_user):

        async with AsyncSession(engine) as session:
            session.add(book(
                author=author(id=author_id),
                creator= id_user
            ))

            await session.commit()
            return True

    async def description( des, id_user):
        user_book=""
        async with AsyncSession(engine) as session:
            session.add(book(
                id=user_book,
                description=des
            ))
            try:
                await session.commit()
            except Exception:
                return False
            return True

    async def end(id_user):
        return True
        pass


async def search_name(search, where_search="id"):
    async with (AsyncSession(engine) as session):
        if where_search=="id":
            stmt= select(book.Name).where(book.id==search)
        elif where_search == ("Name"):
            stmt = select(book.id).where(book.Name == search)
        elif where_search == ("dis"):
            stmt = select(book.Name).where(book.description == search)
        result = await session.execute(stmt)
        a1 = result.scalars().all()
        print(a1)
        return a1


async def make_BD():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(search_name(2))