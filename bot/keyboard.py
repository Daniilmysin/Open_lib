from aiogram import types


def get_start_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Добавить книгу", callback_data="add_book"),
            types.InlineKeyboardButton(text="Добавить автора", callback_data="add_author"),
            types.InlineKeyboardButton(text='дебаг', callback_data='debug')
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_save(data : str):
    buttons = [
        [
            types.InlineKeyboardButton(text="Cохранить", callback_data=f"save_{data}"),
            types.InlineKeyboardButton(text="Изменить", callback_data=f"change_{data}"),
            types.InlineKeyboardButton(text='Отменить(удалить всё)',callback_data=f'del_{data}'),
            types.InlineKeyboardButton(text="Заново", callback_data=f"add_{data}")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard(button, command):
    buttons = [
        [
            types.InlineKeyboardButton(text=button, callback_data=command),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
