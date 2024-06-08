from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
Bot_token="7164218449:AAF3P06kHHnapAkqL2UB7ld0SFCxSGpW-Lw"
bot = Bot(token=Bot_token)

rt= Router()

@rt.message(Command('debug'))
async def debug_info(message: Message):
    await message.answer(
        "<b>Техническая информация</b>\n\n"
        + f"Telegram ID - <code>{message.from_user.id}</code>\n"
        + f"Username - <code>{message.from_user.username}</code>",
        parse_mode = ParseMode.HTML
    )

@rt.message(Command("test"))
async def ins_book_files_epub(message: Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path)
    await message.reply(f"Файл сохранен, вы можете добавить описание или закончить с /stop")