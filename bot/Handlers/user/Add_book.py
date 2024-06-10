from aiogram import Router, F
from aiogram.types import Message
from DBScripts import BookAct
import os
from aiogram import Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ContentType
from bot.Main import Bot_token

bot = Bot(token=Bot_token)
rt = Router()
BookAdd = BookAct.BookAdd

class AddingBook(StatesGroup):
    get_adder_author = State()
    get_adder_name = State()
    get_adder_Files = State()
    get_adder_epub = State()

@rt.message(F.text.lower()=="добавить книгу" or Command("add_book"))
async def ins_book(message: Message, state: FSMContext):
    """Начинает процесс добавления книги"""
    await message.answer("Введите ID Автора. "
                         "Если автора нет в базе данных, то добавьте его с помощью /add_author")
    await state.set_state(AddingBook.get_adder_author)

@rt.message(F.text, StateFilter(AddingBook.get_adder_author))
async def ins_book_author(message: Message, state: FSMContext):
    """Принимает айди автора"""
    mes = int(message.text)
    print(mes)
    status = BookAdd.author_id(author_id=mes, id_user=message.from_user.id)
    await status
    if status:
        await message.answer("Добавлено. Введите название книги:")
        await state.set_state(AddingBook.get_adder_name)
    else:
        await message.answer("Что-то сломалось, повторите")
        await state.set_state(AddingBook.get_adder_author)

@rt.message(F.text, StateFilter(AddingBook.get_adder_name))
async def ins_book_name(message: Message, state: FSMContext):
    """Принимает название книги"""
    mes= str(message.text)
    print(mes)
    status = BookAdd.name(mes, message.from_user.id)
    await status
    """Если всё нормально то всё True"""
    if status:
        await message.answer("Добавлено. Отправьте файл книги Epub(скоро будет поддерживаться больше форматов)")
        await state.set_state(AddingBook.get_adder_epub)
    else:
        await message.answer("Что-то сломалось, повторите")
        await state.set_state(AddingBook.get_adder_name)

@rt.message(AddingBook.get_adder_epub)
async def ins_book_files_epub(message: Message, state: FSMContext):
    """принимает файл с книгой(В РАЗРАБОТКЕ)"""
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path)
    await message.reply(f"Файл сохранен, вы можете добавить описание или закончить с /stop")

@rt.message(Command("stop"))
async def stop(message: Message, state: FSMContext):
    """Заканчивает создание книги"""
    await message.answer("Отмена...")
    await BookAdd.end(message.from_user.id)
    await state.clear()