from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from models import book_act, RedisManager, find_book_id, find_book

rt = Router()


class FindBook(StatesGroup):
    FindBook = State()


@rt.callback_query(F.data == "find_book")
async def callback_find_book(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите название книги:")
    await state.set_state(FindBook.FindBook)


@rt.message(F.text, FindBook.FindBook)
async def finding_book(message: Message, state: FSMContext):
    page = RedisManager().get_data(message.from_user.id)

    if page is not int:
        await RedisManager().set_int(message.from_user.id, 1)
        result = book_act.find_book(message.text, 1)
    elif page is int:
        await RedisManager().set_int(message.from_user.id, page+1)

    for book in result:
        messag = (
            f"ID: {book.id}\n"
            f"Title: {book.title}\n"
            f"Author: {book.author}\n"
            f"File Path: {book.file_path}\n"
            "--------------------"
        )
        await message.answer(messag)


@rt.callback_query(F.data.startswith('send_book_'))
async def send_book(callback: types.CallbackQuery):
    id_book = callback.data.split("_")[2]
    book = find_book_id(id_book)
