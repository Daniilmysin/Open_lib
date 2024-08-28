from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from DBScripts import UserAct
from bot.keyboard import get_start_keyboard

rt= Router()

@rt.message(Command("start"))
async def start(message: Message):
    await message.answer("Добро пожаловать в бота с открытой библиотекой! "
                         "Вы можете как скачивать книги так и загружать их сюда."
                         " Загружая книги, ваш ID и никнейм, указывается как автор", reply_markup=get_start_keyboard())
    await UserAct().add_user(id_user=message.from_user.id, name=message.from_user.first_name)
