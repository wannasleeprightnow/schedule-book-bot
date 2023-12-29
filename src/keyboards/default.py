from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Профиль")],
    ],
    resize_keyboard=True,
)