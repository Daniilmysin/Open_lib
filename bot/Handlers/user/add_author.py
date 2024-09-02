import os
import secrets
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from models import AddAuthor, RedisManager
from bot.scripts import transliterate

rt = Router()
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class AddAuthorState(StatesGroup):
    add_name = State()
    add_description = State()
    add_photo = State()
    end = State()


@rt.callback_query(F.data == 'add_author')
async def start_add(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Напишите имя автора:')
    await state.set_state(AddAuthorState.add_name)


@rt.message(F.text, AddAuthorState.add_name)
async def add_name(message: Message, state: FSMContext):
    status = await AddAuthor().name(message.from_user.id, message.text)
    if status is False:
        await message.answer('Ошибка, попробуйте ещё раз')
        print(f'------Ошибка добавления имени автора, возможно проблемы с redis. Айди юзера: {message.from_user.id}, '
              f'имя автора: {message.text}------')
        await state.set_state(AddAuthorState.add_name)
    elif status is True:
        await message.answer('Имя добавлено, введите описание:')
        await state.set_state(AddAuthorState.add_description)


@rt.message(F.text, AddAuthorState.add_description)
async def add_description(message: Message, state: FSMContext):
    status = await AddAuthor().add_data(message.from_user.id, message.text, 'description' )
    if status is False:
        await message.answer('Ошибка, попробуйте ещё раз')
        print(f'------Ошибка добавления описание автора, возможно проблемы с redis. Айди: {message.from_user.id},'
              f' имя автора: {message.text}------')
        await state.set_state(AddAuthorState.add_description)
    elif status is True:
        await message.answer('Имя добавлено, отправьте фото автора:')
        await state.set_state(AddAuthorState.add_photo)


@rt.message(F.photo, AddAuthorState.add_photo)
async def add_photo(message: Message, state: FSMContext):
    author = await RedisManager().get_data(message.from_user.id)
    photo = message.photo.index
    file_info = await message.bot.get_file(photo)
    downloaded_file = await message.bot.download_file(file_info.file_path)
    name_photo = await transliterate(author['name']) + '_' + str(secrets.token_hex(16)) + '.jpg'
    destination = os.path.join(folder, 'photo', name_photo)
    try:
        with open(destination, 'wb') as f:
            f.write(downloaded_file.read())
    except Exception as error:
        print("нихуя не работает." + str(error))
    await message.reply("Фото успешно загружено и сохранено!")
    await state.set_state(AddAuthorState.end)
