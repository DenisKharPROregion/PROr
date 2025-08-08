# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Записаться на мастер-класс", callback_data="register")],
            [InlineKeyboardButton(text="Мои записи", callback_data="my_registrations")]
        ]
    )

def master_class_keyboard(master_classes):
    keyboard = []
    for mc in master_classes:
        keyboard.append([InlineKeyboardButton(text=mc.title, callback_data=str(mc.id))])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
