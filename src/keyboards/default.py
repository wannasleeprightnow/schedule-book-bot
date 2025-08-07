from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

keyboard = (
    ReplyKeyboardBuilder()
    .row(
        KeyboardButton(text="Расписание"),
        KeyboardButton(text="Что нести?"),
        KeyboardButton(text="Помощь"),
    )
    .row(
        KeyboardButton(text="Распределить вручную"),
        KeyboardButton(text="Профиль"),
    )
).adjust(2)

restart_keyboard = ReplyKeyboardBuilder([[KeyboardButton(text="/start")]])
