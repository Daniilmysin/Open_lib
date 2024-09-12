import os
import secrets

from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot.keyboard import get_keyboard_save, get_keyboard
from models import BookAdd
from models import RedisManager
from bot.scripts import transliterate

rt = Router()
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class AddingBook(StatesGroup):
    get_adder_author = State()
    get_adder_name = State()
    get_adder_des = State()
    get_adder_Files = State()
    get_adder_epub = State()
    end = State()


@rt.callback_query(F.data == "add_book")
async def ins_book(callback: types.CallbackQuery, state: FSMContext):
    """Начинает процесс добавления книги"""
    await callback.message.answer("Введите ID Автора."
                                  "Если автора нет в базе данных, то добавьте его",
                                  reply_markup=get_keyboard('добавить автора', 'add_author'))
    await state.set_state(AddingBook.get_adder_author)


@rt.message(F.text, StateFilter(AddingBook.get_adder_author))
async def ins_book_author(message: Message, state: FSMContext):
    """Принимает айди автора"""
    try:
        mes = int(message.text)
    except Exception:
        await message.answer("Это не айди, попробуйте ещё раз")
        return
    print(mes)
    status = await BookAdd().author_id(mes, message.from_user.id)
    if status is True:
        await message.answer("Добавлено. Введите название книги:")
        await state.set_state(AddingBook.get_adder_name)
    elif status is None:
        await message.answer("Автор не найден, повторите или добавьте автора с помощью /add_author")
        await state.set_state(AddingBook.get_adder_author)
    else:
        await message.answer("Что-то сломалось, повторите")
        await state.set_state(AddingBook.get_adder_author)


@rt.message(F.text, StateFilter(AddingBook.get_adder_name))
async def ins_book_name(message: Message, state: FSMContext):
    """Принимает название книги"""
    mes = str(message.text)
    print(mes)
    status = await BookAdd().add_data(id_user=message.from_user.id, add_data=mes, key='name')
    """Если всё нормально то всё True"""
    if status is True:
        await message.answer("Добавлено. Напишите описание книги")
        await state.set_state(AddingBook.get_adder_des)
    else:
        await message.answer("Что-то сломалось, повторите")
        await state.set_state(AddingBook.get_adder_name)


@rt.message(F.text, StateFilter(AddingBook.get_adder_des))
async def ins_book_name(message: Message, state: FSMContext):
    """Принимает описание"""
    mes = str(message.text)
    print(mes)
    status = await BookAdd().add_data(id_user=message.from_user.id, add_data=mes, key='description')
    """Если всё нормально то всё True"""
    if status is True:
        await message.answer("Добавлено. Отправьте файл книги Epub(скоро будет поддерживаться больше форматов)")
        await state.set_state(AddingBook.get_adder_epub)
    else:
        await message.answer("Что-то сломалось, повторите")
        await state.set_state(AddingBook.get_adder_name)


@rt.message(F.document, AddingBook.get_adder_epub)
async def ins_book_files_epub(message: Message, state: FSMContext):
    """принимает файл с книгой(В РАЗРАБОТКЕ)"""
    format_book = ('.epub', '.pdf', '.txt', '.fb2')                         # разрешённые форматы

    book = await RedisManager().get_data(message.from_user.id)  # получаем книгу
    save_folder = os.path.join(folder, 'books')
    name = str(await transliterate(book['name'])) + '_' + str(secrets.token_hex(16))  # создание имени файла с токеном

    document = message.document                                           # получаем документ
    format = os.path.splitext(document.file_name)[1]
    file_info = await message.bot.get_file(document.file_id)

    if format not in format_book:
        await message.answer(f'Данный формат не поддерживается, отправьте другой')
        return
    status = await RedisManager().set_array(message.from_user.id, format)
    if status is True:
        new_file_name = name + format
        downloaded_file = await message.bot.download_file(file_info.file_path)  # скачиваем
        destination = os.path.join(save_folder, new_file_name)

        try:
            with open(destination, 'wb') as f:                             # сохраняем
                f.write(downloaded_file.read())
        except Exception as Error:
            print(f'Ошибка открытия файла:{Error}')
            await message.reply("Ошибка открытия и сохранения файла, возможно файл побит")

        await BookAdd().add_data(message.from_user.id, str(name), 'file')
        await message.reply('Можете отправить ещё форматы или нажать на нужную кнопку:',
                            reply_markup=get_keyboard_save('book'))
    elif status is False:
        await message.answer('Этот формат уже есть, повторите с другим')


@rt.callback_query(F.data == 'save_book')
async def end(callback: types.CallbackQuery, state: FSMContext):
    """Запускает скрипт с загрузкой книги в базу данных"""

    status = await BookAdd().end(callback.from_user.id)
    if status is True:
        await callback.message.answer("Книга сохранена")
        await state.clear()
    else:
        await callback.message.answer("Что-то сломалось")
        await state.set_state(AddingBook.end)


@rt.message(Command("stop"))
async def stop(message: Message, state: FSMContext):
    """Заканчивает создание книги"""
    await message.answer("Отмена...")
    # await BookAdd.end(message.from_user.id)
    await state.clear()
