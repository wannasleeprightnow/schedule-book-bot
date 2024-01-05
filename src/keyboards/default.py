from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Помощь")],
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Расписание")],
    ],
    resize_keyboard=True,
)
