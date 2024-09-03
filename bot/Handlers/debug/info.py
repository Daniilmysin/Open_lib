from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode

rt = Router()

@rt.message(Command('debug'))
async def debug_info(message: Message):
    await message.answer(
        "<b>Техническая информация</b>\n\n"
        + f"Telegram ID - <code>{message.from_user.id}</code>\n"
        + f"Username - <code>{message.from_user.username}</code>",
        parse_mode=ParseMode.HTML
    )


@rt.callback_query(F.data == 'debug')
async def debug_callback(callback: CallbackQuery):
    await callback.message.answer(f'Telegram ID - {callback.from_user.id}')