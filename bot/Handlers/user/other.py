from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboard import get_start_keyboard
from models import user_act

rt = Router()


@rt.message(Command("start"))
async def start(message: Message):
    await message.answer("Добро пожаловать в бота с открытой библиотекой! "
                         "Вы можете как скачивать книги так и загружать их сюда."
                         " Загружая книги, ваш ID и никнейм, указывается как автор", reply_markup=get_start_keyboard())
    await user_act.add_user(id_user=message.from_user.id, name=message.from_user.first_name)
