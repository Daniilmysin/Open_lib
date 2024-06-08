import re
from aiogram import Router, F
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from DBScripts import user_act

rt= Router()

@rt.message(Command("start"))
async def start(message: Message):
    await message.answer("Добро пожаловать в бота с открытой библиотекой! "
                         "Вы можете как скачивать книги так и загружать их сюда."
                         " Загружая книги, ваш ID и никнейм, указывается как автор")
    await user_act.add_user(message.from_user.id, message.from_user.first_name)
