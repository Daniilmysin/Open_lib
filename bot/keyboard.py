from aiogram import types


def get_start_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Добавить книгу", callback_data="add_book"),
            types.InlineKeyboardButton(text="Добавить автора", callback_data="add_author")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
