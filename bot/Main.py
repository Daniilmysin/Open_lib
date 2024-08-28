import asyncio, logging
from aiogram import Bot, Dispatcher
from Handlers.user import Add_book, other
from Handlers.debug import info
from DBScripts import BDAct
import os

Bot_token = str(os.getenv("bot"))
bot = Bot(token=Bot_token)

logging.basicConfig(level=logging.INFO, filename="py_bot.log", format="%(asctime)s %(levelname)s %(message)s")


# Запуск бота
async def main():
    # Объект бота
    try:
        await BDAct.make_bd()
    except Exception as error:
        print("Ошибка создания базы данных: error")
    # Диспетчер
    dp = Dispatcher()
    dp.include_routers(Add_book.rt, other.rt, info.rt)
    await bot.delete_webhook(drop_pending_updates=True)  # удаляем вебхуки
    await dp.start_polling(bot)  # запускаем


if __name__ == "__main__":
    asyncio.run(main())
