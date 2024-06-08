import asyncio, logging
from aiogram import Bot, Dispatcher
from Handlers.user import Add_book,other
from Handlers.debug import info
from DBScripts import make_BD

logging.basicConfig(level=logging.INFO, filename="py_bot.log", format="%(asctime)s %(levelname)s %(message)s")

Bot_token="7164218449:AAF3P06kHHnapAkqL2UB7ld0SFCxSGpW-Lw"
bot = Bot(token=Bot_token)
# Запуск бота
async def main():
    # Объект бота
    try:
        await make_BD()
    except:
        print("Ошибка создания базы данных, возможно база данных создана")
    # Диспетчер
    dp = Dispatcher()
    dp.include_routers(Add_book.rt, other.rt, info.rt)
    await bot.delete_webhook(drop_pending_updates=True) # удаляем вебхуки
    await dp.start_polling(bot) # запускаем


if __name__ == "__main__":
    asyncio.run(main())