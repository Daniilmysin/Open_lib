import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from Handlers.debug import info
from Handlers.user import add_book, add_author, other
from models import db_act

load_dotenv()
Bot_token = str(os.getenv('bot'))
bot = Bot(token=Bot_token)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Запуск бота
async def main():
    # Объект бота
    try:
        await db_act.make_bd()
    except Exception as error:
        print(f"Ошибка создания базы данных: {error}")
    # Диспетчер
    dp = Dispatcher()
    dp.include_routers(add_book.rt, other.rt, info.rt, add_author.rt)
    await dp.start_polling(bot)  # запускаем


if __name__ == "__main__":
    asyncio.run(main())
