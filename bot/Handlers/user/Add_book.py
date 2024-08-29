import os

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot.Main import bot
from models import BookAdd
from models import RedisManager

rt = Router()


class AddingBook(StatesGroup):
    get_adder_author = State()
    get_adder_name = State()
    get_adder_des = State()
    get_adder_Files = State()
    get_adder_epub = State()
    end = State()


def transliterate(text):
    # Словарь с соответствиями русских букв и латиницы
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sh', 'ы': 'y', 'э': 'e', 'ю': 'yu',
        'я': 'ya', 'ь': '', 'ъ': '', ' ': '_',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
        'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I',
        'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
        'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T',
        'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
        'Ш': 'Sh', 'Щ': 'Sh', 'Ы': 'Y', 'Э': 'E', 'Ю': 'Yu',
        'Я': 'Ya', 'Ь': '', 'Ъ': '',
    }

    # Заменяем русские буквы на латиницу
    result = []
    for char in text:
        result.append(translit_dict.get(char, char))

    return ''.join(result)


@rt.message(F.data() == "add_book")
async def ins_book(message: Message, state: FSMContext):
    """Начинает процесс добавления книги"""
    await message.answer("Введите ID Автора."
                         "Если автора нет в базе данных, то добавьте его с помощью /add_author")
    await state.set_state(AddingBook.get_adder_author)


@rt.message(F.text, StateFilter(AddingBook.get_adder_author))
async def ins_book_author(message: Message, state: FSMContext):
    """Принимает айди автора"""
    mes = int(message.text)
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
        await message.answer("Добавлено. Добавьте описание книги или ")
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
    document = message.document
    data = RedisManager().get_data(message.from_user.id)
    new_name = transliterate(data['name'])  # именует латиницей
    top_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    save_folder = os.path.join(top_folder, 'books', new_name)
    file_info = await bot.get_file(document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    destination = os.path.join(save_folder, document.file_name)

    with open(destination, 'wb') as f:
        f.write(downloaded_file.read())
    await BookAdd().add_data(message.from_user.id, str(destination), 'epub')
    await message.reply("Файл сохранен")
    book = await RedisManager().get_data(message.from_user.id)
    await message.answer('Книга будет выглядеть так: \n' + book['name'] + '\nОписание: \n' + book['description'])
    await state.set_state(AddingBook.end)


@rt.message(F.text.lower() == 'сохранить', AddingBook.end)
async def end(message: Message, state: FSMContext):
    """Запускает скрипт с загрузкой книги в базу данных"""
    status = await BookAdd().end(message.from_user.id)
    if status is True:
        await message.answer("Книга сохранена")
    else:
        await message.answer("Что-то сломалось")


@rt.message(Command("stop"))
async def stop(message: Message, state: FSMContext):
    """Заканчивает создание книги"""
    await message.answer("Отмена...")
    # await BookAdd.end(message.from_user.id)
    await state.clear()
