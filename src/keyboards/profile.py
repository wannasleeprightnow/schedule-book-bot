from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.add(
    InlineKeyboardButton(text="Изменить класс", callback_data="Изменить класс")
)
builder.add(
    InlineKeyboardButton(
        text="Изменить соседа по парте",
        callback_data="Изменить соседа по парте",
    )
)
builder.add(
    InlineKeyboardButton(
        text="Изменить время напоминаний",
        callback_data="Изменить время напоминаний",
    )
)
builder.adjust(1)
